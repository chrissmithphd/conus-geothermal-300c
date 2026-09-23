#!/usr/bin/env python3
"""
Calculate depth required to reach 300°C across CONUS.
Combines Stanford (0-7 km) and SMU digitized (7.5-10 km) data.

VERSION 2: Addresses technical improvements from TECHNICAL_IMPROVEMENTS.md
- Grid alignment validation
- Geographic distance correction for SMU matching
- Match distance tracking and quality metrics
- Improved interpolation for non-monotonic profiles
- Source type metadata (interpolated vs bounded)
- Cross-validation in overlap region
"""
import sys
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from scipy.interpolate import interp1d
from scipy.spatial import cKDTree
import warnings
warnings.filterwarnings('ignore')

# Force unbuffered output for progress tracking
sys.stdout.reconfigure(line_buffering=True) if hasattr(sys.stdout, 'reconfigure') else None

def log(msg):
    """Print with timestamp and flush."""
    timestamp = time.strftime("%H:%M:%S")
    print(f"[{timestamp}] {msg}")
    sys.stdout.flush()

# Constants
TARGET_TEMP = 300  # °C
EARTH_RADIUS_KM = 6371  # km
MAX_SMU_MATCH_DISTANCE_KM = 50  # Maximum distance for SMU match to be considered valid

# Output directories
OUTPUT_DIR = Path("data/processed")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

PLOT_DIR = Path("plots")
PLOT_DIR.mkdir(exist_ok=True)

def load_stanford_data():
    """
    Load all available Stanford temperature layers.

    CRITICAL FIX: Stanford JSON files have identical coordinates but in different orders.
    We must sort by (lat, lon) to ensure row-wise alignment across depths.
    """
    data_dir = Path("data/raw/stanford")
    json_files = sorted(data_dir.glob("temperature_*.json"))

    log("Loading Stanford data...")

    import json

    all_data = {}
    for json_file in json_files:
        # Extract depth from filename
        depth_str = json_file.stem.replace('temperature_', '').replace('km', '')
        depth_km = float(depth_str)

        log(f"  Loading {depth_str} km...")

        with open(json_file, 'r') as f:
            data = json.load(f)

        features = data['features']

        records = []
        for feature in features:
            attrs = feature['attributes']
            records.append({
                'lat': attrs['Lat'],
                'lon': attrs['Long'],
                'temperature': attrs['T']
            })

        df = pd.DataFrame(records)

        # CRITICAL: Sort by (lat, lon) to ensure alignment across depths
        df = df.sort_values(['lat', 'lon']).reset_index(drop=True)

        all_data[depth_km] = df
        log(f"    Loaded {len(df):,} points (sorted by lat, lon)")

    return all_data

def validate_grid_alignment(stanford_data):
    """
    CRITICAL: Validate that all Stanford depth layers have identical coordinate grids.
    Returns True if valid, raises ValueError if misaligned.
    """
    log("\n" + "="*80)
    log("GRID ALIGNMENT VALIDATION (CRITICAL)")
    log("="*80)

    depths = sorted(stanford_data.keys())
    ref_depth = depths[0]
    ref_df = stanford_data[ref_depth]

    log(f"  Reference layer: {ref_depth} km ({len(ref_df):,} points)")

    all_aligned = True

    for depth in depths[1:]:
        test_df = stanford_data[depth]

        # Check length
        if len(test_df) != len(ref_df):
            log(f"  ❌ FAILED: {depth} km has {len(test_df):,} points, expected {len(ref_df):,}")
            all_aligned = False
            continue

        # Check coordinate match
        lat_match = np.allclose(ref_df['lat'].values, test_df['lat'].values, atol=1e-6)
        lon_match = np.allclose(ref_df['lon'].values, test_df['lon'].values, atol=1e-6)

        if not lat_match or not lon_match:
            log(f"  ❌ FAILED: {depth} km coordinates don't match reference")

            # Show sample mismatches
            lat_diff = np.abs(ref_df['lat'].values - test_df['lat'].values)
            lon_diff = np.abs(ref_df['lon'].values - test_df['lon'].values)
            max_lat_diff = lat_diff.max()
            max_lon_diff = lon_diff.max()

            log(f"     Max lat difference: {max_lat_diff:.6f}°")
            log(f"     Max lon difference: {max_lon_diff:.6f}°")

            all_aligned = False
        else:
            log(f"  ✅ PASSED: {depth} km grid aligned")

    if not all_aligned:
        raise ValueError(
            "Grid alignment validation FAILED. "
            "Stanford depth layers have different coordinate grids. "
            "Cannot safely create temperature profiles."
        )

    log("\n✅ Grid alignment validation PASSED - all layers have identical coordinates")
    return True

def load_smu_data():
    """Load digitized SMU data."""
    log("\nLoading SMU digitized data...")

    smu_file = Path("data/processed/smu_digitized/smu_digitized_all_depths.parquet")

    if not smu_file.exists():
        smu_file = Path("data/processed/smu_digitized/smu_digitized_all_depths.csv")

    log(f"  Reading {smu_file.name}...")
    df = pd.read_parquet(smu_file) if smu_file.suffix == '.parquet' else pd.read_csv(smu_file)

    log(f"  Loaded {len(df):,} points across {df['depth_km'].nunique()} depths")

    # Organize by depth
    log("  Organizing by depth...")
    smu_by_depth = {}
    for depth in sorted(df['depth_km'].unique()):
        smu_by_depth[depth] = df[df['depth_km'] == depth][['lat', 'lon', 'temperature_c']].copy()
        smu_by_depth[depth].rename(columns={'lat': 'lat', 'lon': 'lon', 'temperature_c': 'temperature'}, inplace=True)
        log(f"    {depth} km: {len(smu_by_depth[depth]):,} points")

    return smu_by_depth

def interpolate_depth_to_temp_improved(depths, temps, target_temp):
    """
    Improved interpolation to find depth where temperature reaches target.

    Improvements:
    - Handles non-monotonic profiles by finding first crossing
    - Uses linear interpolation between bracketing points
    - Returns NaN if target not reached or if not enough data
    """
    # Need at least 2 points to interpolate
    if len(depths) < 2:
        return np.nan, 'insufficient_data'

    # Check if target is reached
    if temps.max() < target_temp:
        return np.nan, 'not_reached'

    if temps.min() > target_temp:
        return 0.0, 'surface'

    # Find first adjacent pair that brackets target temperature
    # This handles non-monotonic profiles correctly
    for i in range(len(depths) - 1):
        temp1, temp2 = temps[i], temps[i+1]
        depth1, depth2 = depths[i], depths[i+1]

        # Check if target is between these two temperatures
        if (temp1 <= target_temp <= temp2) or (temp2 <= target_temp <= temp1):
            # Linear interpolation between these two points
            if temp2 == temp1:
                # Edge case: same temperature at both depths
                depth_300 = (depth1 + depth2) / 2
            else:
                depth_300 = depth1 + (target_temp - temp1) * (depth2 - depth1) / (temp2 - temp1)

            # Constrain to reasonable range
            if depth_300 < 0:
                return 0.0, 'interpolated'

            return depth_300, 'interpolated'

    # If we get here, temperature crosses target but we couldn't find bracket
    # Fall back to scipy interpolation
    try:
        f = interp1d(temps, depths, kind='linear', bounds_error=False, fill_value='extrapolate')
        depth_300 = float(f(target_temp))

        # Constrain to reasonable range
        if depth_300 < 0:
            return 0.0, 'interpolated'
        if depth_300 > depths.max() + 1:  # Allow small extrapolation
            return np.nan, 'extrapolation_failed'

        return depth_300, 'interpolated'
    except:
        return np.nan, 'interpolation_error'

def calculate_stanford_depth_to_300c(stanford_data):
    """
    Calculate depth to 300°C for each Stanford grid location.
    """
    log("\nCalculating depth to 300°C from Stanford data...")

    # CRITICAL: Validate grid alignment first
    validate_grid_alignment(stanford_data)

    # Get reference grid from first depth layer
    depths = sorted(stanford_data.keys())
    ref_depth = depths[0]
    df = stanford_data[ref_depth][['lat', 'lon']].copy()

    log(f"  Processing {len(df):,} grid locations...")

    # For each location, collect temperature profile
    depth_to_300 = []
    interp_status = []
    start_time = time.time()

    for idx in range(len(df)):
        if (idx + 1) % 50000 == 0:
            elapsed = time.time() - start_time
            rate = (idx + 1) / elapsed
            remaining = (len(df) - idx - 1) / rate
            log(f"    Progress: {idx+1:,}/{len(df):,} ({(idx+1)/len(df)*100:.1f}%) - {rate:.0f} pts/sec - ETA: {remaining/60:.1f} min")

        # Collect temperature at all depths for this location
        # NOTE: Grid alignment validated, so iloc[idx] is safe
        temps = []
        depth_list = []

        for depth_km in depths:
            temp = stanford_data[depth_km].iloc[idx]['temperature']
            temps.append(temp)
            depth_list.append(depth_km)

        # Improved interpolation
        depth_300, status = interpolate_depth_to_temp_improved(
            np.array(depth_list), np.array(temps), TARGET_TEMP
        )
        depth_to_300.append(depth_300)
        interp_status.append(status)

    df['depth_300_km'] = depth_to_300
    df['source'] = 'stanford'
    df['source_type'] = 'interpolated'
    df['interp_status'] = interp_status

    # Count how many reached 300°C
    n_reached = df['depth_300_km'].notna().sum()
    pct_reached = (n_reached / len(df)) * 100

    log(f"\n  Results:")
    log(f"    Reached 300°C within 7 km: {n_reached:,} ({pct_reached:.1f}%)")
    log(f"    Did not reach 300°C by 7 km: {len(df) - n_reached:,} ({100-pct_reached:.1f}%)")

    # Report interpolation status
    status_counts = pd.Series(interp_status).value_counts()
    log(f"\n  Interpolation status:")
    for status, count in status_counts.items():
        log(f"    {status}: {count:,} ({count/len(df)*100:.1f}%)")

    return df

def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate great circle distance between two points on Earth.
    Returns distance in kilometers.
    """
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
    c = 2 * np.arcsin(np.sqrt(a))

    return EARTH_RADIUS_KM * c

def match_smu_to_stanford_grid(stanford_grid, smu_data):
    """
    For Stanford locations that didn't reach 300°C by 7 km,
    look up SMU temperatures at 7.5, 8.5, 10 km to determine deeper category.

    IMPROVEMENTS:
    - Uses geographic distance correction (cos(latitude))
    - Tracks match distances
    - Applies maximum match distance threshold
    - Reports match quality statistics
    """
    log("\nMatching SMU data to Stanford grid...")

    # Get locations that didn't reach 300°C
    no_reach = stanford_grid[stanford_grid['depth_300_km'].isna()].copy()
    log(f"  {len(no_reach):,} locations need SMU lookup")

    if len(no_reach) == 0:
        return stanford_grid

    # Build KD-trees for SMU data at each depth
    # Use geographic distance correction: scale longitude by cos(latitude)
    smu_depths = [7.5, 8.5, 10.0]
    smu_trees = {}
    smu_coords_geographic = {}
    smu_temps_arrays = {}

    log("  Building KD-trees for SMU data (with geographic distance correction)...")
    for depth in smu_depths:
        if depth in smu_data:
            smu_df = smu_data[depth]

            # Apply geographic correction: scale longitude by cos(latitude)
            lat_rad = np.radians(smu_df['lat'].values)
            lon_scaled = smu_df['lon'].values * np.cos(lat_rad)

            coords = np.column_stack([smu_df['lat'].values, lon_scaled])
            coords_geographic = np.column_stack([smu_df['lat'].values, smu_df['lon'].values])
            temps = smu_df['temperature'].values

            # Build KDTree for fast nearest neighbor queries
            tree = cKDTree(coords)
            smu_trees[depth] = tree
            smu_coords_geographic[depth] = coords_geographic
            smu_temps_arrays[depth] = temps
            log(f"    Built KDTree for {depth} km ({len(smu_df):,} points)")

    # Query all no-reach locations at once for better performance
    log(f"\n  Querying SMU temperatures for {len(no_reach):,} locations...")

    # Apply same geographic correction to query points
    query_lats = no_reach['lat'].values
    query_lons = no_reach['lon'].values
    lat_rad = np.radians(query_lats)
    lon_scaled = query_lons * np.cos(lat_rad)
    query_coords = np.column_stack([query_lats, lon_scaled])

    smu_temps = {}
    smu_distances_deg = {}
    smu_distances_km = {}
    start_time = time.time()

    for depth in smu_depths:
        if depth in smu_trees:
            log(f"    Querying {depth} km depth...")

            # Query nearest neighbor for all points at once
            distances_deg, indices = smu_trees[depth].query(query_coords, k=1)

            # Get temperatures from nearest neighbors
            smu_temps[depth] = smu_temps_arrays[depth][indices]
            smu_distances_deg[depth] = distances_deg

            # Calculate actual geographic distances using Haversine
            matched_lats = smu_coords_geographic[depth][indices, 0]
            matched_lons = smu_coords_geographic[depth][indices, 1]

            distances_km = haversine_distance(
                query_lats, query_lons,
                matched_lats, matched_lons
            )
            smu_distances_km[depth] = distances_km

            # Report statistics
            elapsed = time.time() - start_time
            log(f"      Completed in {elapsed:.1f}s ({len(no_reach)/elapsed:.0f} queries/sec)")
            log(f"      Distance stats: min={distances_km.min():.1f} km, "
                f"median={np.median(distances_km):.1f} km, max={distances_km.max():.1f} km")
            log(f"      Matches beyond {MAX_SMU_MATCH_DISTANCE_KM} km: "
                f"{(distances_km > MAX_SMU_MATCH_DISTANCE_KM).sum():,} "
                f"({(distances_km > MAX_SMU_MATCH_DISTANCE_KM).sum()/len(distances_km)*100:.1f}%)")
        else:
            smu_temps[depth] = np.full(len(no_reach), np.nan)
            smu_distances_km[depth] = np.full(len(no_reach), np.nan)

    # Add SMU temperatures and distances to no_reach dataframe
    for depth in smu_depths:
        no_reach[f'smu_temp_{depth}km'] = smu_temps[depth]
        no_reach[f'smu_dist_{depth}km'] = smu_distances_km[depth]

    log("  Categorizing depth bins...")

    # Vectorized categorization with distance filtering
    def categorize_smu_depth_vectorized(df):
        """
        Vectorized depth categorization.

        NOTE: SMU values are UPPER BOUNDS, not interpolated crossings.
        If temperature >= 300°C at 8.5 km, the true crossing is somewhere in [7.5, 8.5] km.
        """
        depth_300 = np.full(len(df), np.nan)
        source_type = np.full(len(df), 'none', dtype=object)
        match_distance = np.full(len(df), np.nan)

        # Check each depth from deepest to shallowest
        # Apply distance threshold
        for depth_km in [10.0, 8.5, 7.5]:
            temp_col = f'smu_temp_{depth_km}km'
            dist_col = f'smu_dist_{depth_km}km'

            if temp_col not in df.columns:
                continue

            temp = df[temp_col]
            dist = df[dist_col]

            # Valid match: temperature >= target AND distance within threshold
            mask = (temp >= TARGET_TEMP) & temp.notna() & (dist <= MAX_SMU_MATCH_DISTANCE_KM)

            depth_300[mask] = depth_km
            source_type[mask] = 'smu_upper_bound'
            match_distance[mask] = dist[mask]

        return depth_300, source_type, match_distance

    depth_300, source_type, match_distance = categorize_smu_depth_vectorized(no_reach)

    no_reach['depth_300_km'] = depth_300
    no_reach['source'] = 'smu'
    no_reach['source_type'] = source_type
    no_reach['smu_match_distance_km'] = match_distance

    # Update main grid efficiently
    log("  Updating main grid...")
    stanford_grid.loc[no_reach.index, 'depth_300_km'] = no_reach['depth_300_km']
    stanford_grid.loc[no_reach.index, 'source'] = no_reach['source']
    stanford_grid.loc[no_reach.index, 'source_type'] = no_reach['source_type']
    stanford_grid.loc[no_reach.index, 'smu_match_distance_km'] = no_reach['smu_match_distance_km']

    # Report results
    n_smu_reached = no_reach['depth_300_km'].notna().sum()
    n_smu_filtered = ((no_reach['smu_temp_10.0km'] >= TARGET_TEMP) &
                      (no_reach['smu_dist_10.0km'] > MAX_SMU_MATCH_DISTANCE_KM)).sum()

    log(f"\n  SMU results:")
    log(f"    Reached 300°C by 10 km (within {MAX_SMU_MATCH_DISTANCE_KM} km): {n_smu_reached:,}")
    log(f"    Filtered out (distance > {MAX_SMU_MATCH_DISTANCE_KM} km): {n_smu_filtered:,}")
    log(f"    Still not reached by 10 km: {len(no_reach) - n_smu_reached:,}")

    return stanford_grid

def cross_validate_stanford_smu_overlap(stanford_data, smu_data):
    """
    Cross-validate Stanford and SMU predictions in overlap region.
    Stanford predicts to 7 km, SMU starts at 7.5 km.

    Compare Stanford 7km temperatures with SMU 7.5km temperatures.
    """
    log("\n" + "="*80)
    log("CROSS-VALIDATION: Stanford vs SMU in overlap region")
    log("="*80)

    if 7.0 not in stanford_data or 7.5 not in smu_data:
        log("  Skipped: Missing depth layers for cross-validation")
        return None

    stanford_7km = stanford_data[7.0]
    smu_75km = smu_data[7.5]

    log(f"  Stanford 7 km: {len(stanford_7km):,} points")
    log(f"  SMU 7.5 km: {len(smu_75km):,} points")

    # Match Stanford points to nearest SMU points
    log("  Matching Stanford to SMU...")

    # Apply geographic correction
    smu_lat = smu_75km['lat'].values
    smu_lon = smu_75km['lon'].values
    smu_lat_rad = np.radians(smu_lat)
    smu_lon_scaled = smu_lon * np.cos(smu_lat_rad)
    smu_coords = np.column_stack([smu_lat, smu_lon_scaled])

    stanford_lat = stanford_7km['lat'].values
    stanford_lon = stanford_7km['lon'].values
    stanford_lat_rad = np.radians(stanford_lat)
    stanford_lon_scaled = stanford_lon * np.cos(stanford_lat_rad)
    stanford_coords = np.column_stack([stanford_lat, stanford_lon_scaled])

    tree = cKDTree(smu_coords)
    distances_deg, indices = tree.query(stanford_coords, k=1)

    # Get matched temperatures
    stanford_temps = stanford_7km['temperature'].values
    smu_temps = smu_75km['temperature'].values[indices]

    # Calculate match distances in km
    matched_smu_lat = smu_lat[indices]
    matched_smu_lon = smu_lon[indices]
    distances_km = haversine_distance(
        stanford_lat, stanford_lon,
        matched_smu_lat, matched_smu_lon
    )

    # Filter to reasonable matches
    valid_mask = distances_km <= MAX_SMU_MATCH_DISTANCE_KM
    n_valid = valid_mask.sum()

    log(f"  Valid matches (≤{MAX_SMU_MATCH_DISTANCE_KM} km): {n_valid:,}/{len(stanford_7km):,}")

    if n_valid < 100:
        log("  Too few valid matches for meaningful cross-validation")
        return None

    stanford_temps_valid = stanford_temps[valid_mask]
    smu_temps_valid = smu_temps[valid_mask]

    # Calculate statistics
    correlation = np.corrcoef(stanford_temps_valid, smu_temps_valid)[0, 1]
    bias = np.mean(stanford_temps_valid - smu_temps_valid)
    rmse = np.sqrt(np.mean((stanford_temps_valid - smu_temps_valid)**2))
    mae = np.mean(np.abs(stanford_temps_valid - smu_temps_valid))

    log(f"\n  Cross-validation statistics:")
    log(f"    Correlation: {correlation:.3f}")
    log(f"    Bias (Stanford - SMU): {bias:.1f}°C")
    log(f"    RMSE: {rmse:.1f}°C")
    log(f"    MAE: {mae:.1f}°C")

    # Create scatter plot
    fig, ax = plt.subplots(figsize=(10, 10))

    # Subsample for plotting if too many points
    if n_valid > 10000:
        sample_idx = np.random.choice(n_valid, 10000, replace=False)
        plot_stanford = stanford_temps_valid[sample_idx]
        plot_smu = smu_temps_valid[sample_idx]
        log(f"  (Plotting random sample of 10,000 points)")
    else:
        plot_stanford = stanford_temps_valid
        plot_smu = smu_temps_valid

    ax.scatter(plot_stanford, plot_smu, alpha=0.3, s=10, color='steelblue', edgecolors='none')

    # Add 1:1 line
    min_temp = min(plot_stanford.min(), plot_smu.min())
    max_temp = max(plot_stanford.max(), plot_smu.max())
    ax.plot([min_temp, max_temp], [min_temp, max_temp], 'r--', linewidth=2, label='1:1 line')

    ax.set_xlabel('Stanford 7 km Temperature (°C)\n(Continuous Model)', fontsize=12, fontweight='bold')
    ax.set_ylabel('SMU 7.5 km Temperature (°C)\n(Digitized from Color Maps)', fontsize=12, fontweight='bold')
    ax.set_title(f'Cross-Validation: Stanford vs SMU in Overlap Region\n'
                f'Correlation: {correlation:.3f}, RMSE: {rmse:.1f}°C, n={n_valid:,}',
                fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=11, loc='upper left')

    # Add annotation explaining SMU quantization
    textstr = ('Note: SMU data shows horizontal bands\n'
               'because it was digitized from color-\n'
               'coded temperature maps with discrete\n'
               'bins (~25°C intervals), not continuous\n'
               'measurements. Stanford data is from\n'
               'a continuous thermal model.')
    ax.text(0.98, 0.02, textstr, transform=ax.transAxes,
           fontsize=9, verticalalignment='bottom', horizontalalignment='right',
           bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

    plt.tight_layout()
    out_file = PLOT_DIR / "cross_validation_stanford_smu.png"
    plt.savefig(out_file, dpi=150, bbox_inches='tight')
    plt.close()
    log(f"  Saved: {out_file}")

    return {
        'correlation': correlation,
        'bias': bias,
        'rmse': rmse,
        'mae': mae,
        'n_valid': n_valid
    }

def assign_depth_bins(df):
    """Assign depth to appropriate bin category."""
    log("\nAssigning depth bins...")

    def get_bin(depth):
        if np.isnan(depth):
            return ">10 km"
        elif depth <= 4:
            return "≤4 km"
        elif depth <= 5:
            return "4-5 km"
        elif depth <= 6:
            return "5-6 km"
        elif depth <= 7:
            return "6-7 km"
        elif depth <= 8:
            return "7-8 km"
        elif depth <= 10:
            return "8-10 km"
        else:
            return ">10 km"

    df['depth_bin'] = df['depth_300_km'].apply(get_bin)

    # Count by bin
    log("\n  Distribution by depth bin:")
    bin_counts = df['depth_bin'].value_counts()
    bin_order = ["≤4 km", "4-5 km", "5-6 km", "6-7 km", "7-8 km", "8-10 km", ">10 km"]

    for bin_name in bin_order:
        count = bin_counts.get(bin_name, 0)
        pct = (count / len(df)) * 100
        log(f"    {bin_name:8s}: {count:7,} ({pct:5.1f}%)")

    return df

def calculate_cell_area(lat, lat_spacing, lon_spacing):
    """
    Calculate area of a lat/lon cell in km².
    Area varies with latitude due to Earth's curvature.
    """
    # Convert to radians
    lat_rad = np.radians(lat)
    dlat_rad = np.radians(lat_spacing)
    dlon_rad = np.radians(lon_spacing)

    # Area = R² * cos(lat) * dlat * dlon
    area = EARTH_RADIUS_KM**2 * np.cos(lat_rad) * dlat_rad * dlon_rad

    return area

def calculate_area_statistics(df):
    """Calculate area-weighted statistics for each depth bin."""
    log("\nCalculating area-weighted statistics...")

    # Estimate grid spacing (assume uniform)
    lat_diff = df['lat'].diff().abs()
    lon_diff = df['lon'].diff().abs()

    lat_spacing = lat_diff[lat_diff > 0].median()
    lon_spacing = lon_diff[lon_diff > 0].median()

    log(f"  Grid spacing: ~{lat_spacing:.3f}° lat x {lon_spacing:.3f}° lon")

    # Calculate area for each cell
    df['cell_area_km2'] = df['lat'].apply(
        lambda lat: calculate_cell_area(lat, lat_spacing, lon_spacing)
    )

    total_area = df['cell_area_km2'].sum()
    log(f"  Total CONUS area (gridded): {total_area:,.0f} km²")

    # Calculate area by depth bin
    bin_order = ["≤4 km", "4-5 km", "5-6 km", "6-7 km", "7-8 km", "8-10 km", ">10 km"]

    results = []
    cumulative_area = 0

    log(f"\n  Area statistics by depth bin:")
    log(f"  {'Bin':10s} {'Area (km²)':>15s} {'% of Total':>12s} {'Cumulative %':>15s}")
    log(f"  {'-'*10} {'-'*15} {'-'*12} {'-'*15}")

    for bin_name in bin_order:
        bin_df = df[df['depth_bin'] == bin_name]
        area = bin_df['cell_area_km2'].sum()
        pct = (area / total_area) * 100
        cumulative_area += area
        cumulative_pct = (cumulative_area / total_area) * 100

        results.append({
            'bin': bin_name,
            'area_km2': area,
            'percent': pct,
            'cumulative_percent': cumulative_pct
        })

        log(f"  {bin_name:10s} {area:15,.0f} {pct:12.2f} {cumulative_pct:15.2f}")

    return pd.DataFrame(results)

def print_quality_metrics(df):
    """Print data quality and source metrics."""
    log("\n" + "="*80)
    log("DATA QUALITY METRICS")
    log("="*80)

    # Source breakdown
    log("\n1. Data Source:")
    source_counts = df['source'].value_counts()
    for source, count in source_counts.items():
        log(f"   {source}: {count:,} ({count/len(df)*100:.1f}%)")

    # Source type breakdown
    log("\n2. Source Type:")
    source_type_counts = df['source_type'].value_counts()
    for stype, count in source_type_counts.items():
        log(f"   {stype}: {count:,} ({count/len(df)*100:.1f}%)")

    # SMU match distances
    smu_mask = df['source'] == 'smu'
    if smu_mask.sum() > 0:
        smu_distances = df.loc[smu_mask, 'smu_match_distance_km'].dropna()
        if len(smu_distances) > 0:
            log("\n3. SMU Match Quality:")
            log(f"   Matches: {len(smu_distances):,}")
            log(f"   Min distance: {smu_distances.min():.1f} km")
            log(f"   Median distance: {smu_distances.median():.1f} km")
            log(f"   Max distance: {smu_distances.max():.1f} km")
            log(f"   Within 10 km: {(smu_distances <= 10).sum():,} ({(smu_distances <= 10).sum()/len(smu_distances)*100:.1f}%)")
            log(f"   Within 25 km: {(smu_distances <= 25).sum():,} ({(smu_distances <= 25).sum()/len(smu_distances)*100:.1f}%)")

def print_cumulative_statistics(stats_df):
    """Print cumulative accessibility statistics."""
    log("\n" + "="*80)
    log("CUMULATIVE ACCESSIBILITY STATISTICS")
    log("="*80)

    thresholds = [4, 5, 6, 7, 8, 10]

    for threshold in thresholds:
        bins_within = []
        if threshold >= 4:
            bins_within.append("≤4 km")
        if threshold >= 5:
            bins_within.append("4-5 km")
        if threshold >= 6:
            bins_within.append("5-6 km")
        if threshold >= 7:
            bins_within.append("6-7 km")
        if threshold >= 8:
            bins_within.append("7-8 km")
        if threshold >= 10:
            bins_within.append("8-10 km")

        cumulative_pct = stats_df[stats_df['bin'].isin(bins_within)]['percent'].sum()
        log(f"  Reachable within {threshold:2d} km: {cumulative_pct:6.2f}% of CONUS")

def main():
    start_time = time.time()
    log("="*80)
    log("CALCULATING DEPTH TO 300°C ACROSS CONUS - VERSION 2")
    log("="*80)

    # 1. Load data
    stanford_data = load_stanford_data()
    smu_data = load_smu_data()

    # 2. Cross-validate in overlap region
    cross_val_results = cross_validate_stanford_smu_overlap(stanford_data, smu_data)

    # 3. Calculate depth to 300°C using Stanford data (with grid validation)
    grid = calculate_stanford_depth_to_300c(stanford_data)

    # 4. Fill in deeper locations using SMU data (with geographic correction)
    grid = match_smu_to_stanford_grid(grid, smu_data)

    # 5. Assign depth bins
    grid = assign_depth_bins(grid)

    # 6. Calculate area-weighted statistics (single source of truth for per-bin
    #    area/percent; downstream figure scripts read this instead of hardcoding).
    stats_df = calculate_area_statistics(grid)
    stats_file = OUTPUT_DIR / "depth_bin_area_stats.csv"
    stats_df.to_csv(stats_file, index=False)
    log(f"  Per-bin area stats: {stats_file}")

    # 7. Print quality metrics
    print_quality_metrics(grid)

    # 8. Print cumulative statistics
    print_cumulative_statistics(stats_df)

    # 9. Save final grid
    log("\nSaving output files...")
    output_file = OUTPUT_DIR / "conus_depth_to_300c.csv"

    # Select columns for output
    output_cols = ['lat', 'lon', 'depth_300_km', 'depth_bin',
                   'source', 'source_type', 'smu_match_distance_km']

    # Add interp_status for stanford points
    if 'interp_status' in grid.columns:
        grid_to_save = grid[output_cols + ['interp_status']].copy()
    else:
        grid_to_save = grid[output_cols].copy()

    grid_to_save.to_csv(output_file, index=False)

    parquet_file = OUTPUT_DIR / "conus_depth_to_300c.parquet"
    grid_to_save.to_parquet(parquet_file, index=False)

    log("\n" + "="*80)
    log("OUTPUT FILES")
    log("="*80)
    log(f"  Grid data (CSV):     {output_file}")
    log(f"  Grid data (Parquet): {parquet_file}")
    log(f"  Cross-validation:    {PLOT_DIR / 'cross_validation_stanford_smu.png'}")

    total_time = time.time() - start_time
    log(f"\nTotal processing time: {total_time/60:.1f} minutes")

    log("\n" + "="*80)
    log("ANALYSIS COMPLETE")
    log("="*80)

if __name__ == "__main__":
    main()

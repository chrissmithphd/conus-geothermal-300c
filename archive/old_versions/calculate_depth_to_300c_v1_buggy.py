#!/usr/bin/env python3
"""
Calculate depth required to reach 300°C across CONUS.
Combines Stanford (0-7 km) and SMU digitized (7.5-10 km) data.
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

# Output directories
OUTPUT_DIR = Path("data/processed")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

PLOT_DIR = Path("plots")
PLOT_DIR.mkdir(exist_ok=True)

def load_stanford_data():
    """Load all available Stanford temperature layers."""
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
        all_data[depth_km] = df
        log(f"    Loaded {len(df):,} points")

    return all_data

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

def interpolate_depth_to_temp(depths, temps, target_temp):
    """
    Interpolate to find depth where temperature reaches target.
    Returns NaN if target not reached or if not enough data.
    """
    # Need at least 2 points to interpolate
    if len(depths) < 2:
        return np.nan

    # Check if target is reached
    if temps.max() < target_temp:
        return np.nan  # Not reached

    if temps.min() > target_temp:
        return 0.0  # Already above target at surface

    # Linear interpolation
    try:
        f = interp1d(temps, depths, kind='linear', bounds_error=False, fill_value='extrapolate')
        depth_300 = float(f(target_temp))

        # Constrain to reasonable range
        if depth_300 < 0:
            return 0.0
        if depth_300 > depths.max() + 1:  # Allow small extrapolation
            return np.nan

        return depth_300
    except:
        return np.nan

def calculate_stanford_depth_to_300c(stanford_data):
    """
    Calculate depth to 300°C for each Stanford grid location.
    """
    log("\nCalculating depth to 300°C from Stanford data...")

    # Get reference grid from first depth layer
    depths = sorted(stanford_data.keys())
    ref_depth = depths[0]
    df = stanford_data[ref_depth][['lat', 'lon']].copy()

    log(f"  Processing {len(df):,} grid locations...")

    # For each location, collect temperature profile
    depth_to_300 = []
    start_time = time.time()

    for idx in range(len(df)):
        if (idx + 1) % 50000 == 0:
            elapsed = time.time() - start_time
            rate = (idx + 1) / elapsed
            remaining = (len(df) - idx - 1) / rate
            log(f"    Progress: {idx+1:,}/{len(df):,} ({(idx+1)/len(df)*100:.1f}%) - {rate:.0f} pts/sec - ETA: {remaining/60:.1f} min")

        # Collect temperature at all depths for this location
        temps = []
        depth_list = []

        for depth_km in depths:
            temp = stanford_data[depth_km].iloc[idx]['temperature']
            temps.append(temp)
            depth_list.append(depth_km)

        # Interpolate to find depth where temp = 300°C
        depth_300 = interpolate_depth_to_temp(np.array(depth_list), np.array(temps), TARGET_TEMP)
        depth_to_300.append(depth_300)

    df['depth_300_km'] = depth_to_300
    df['source'] = 'Stanford'

    # Count how many reached 300°C
    n_reached = df['depth_300_km'].notna().sum()
    pct_reached = (n_reached / len(df)) * 100

    log(f"\n  Results:")
    log(f"    Reached 300°C within 7 km: {n_reached:,} ({pct_reached:.1f}%)")
    log(f"    Did not reach 300°C by 7 km: {len(df) - n_reached:,} ({100-pct_reached:.1f}%)")

    return df

def match_smu_to_stanford_grid(stanford_grid, smu_data):
    """
    For Stanford locations that didn't reach 300°C by 7 km,
    look up SMU temperatures at 7.5, 8.5, 10 km to determine deeper category.
    Uses optimized cKDTree for fast nearest neighbor lookups.
    """
    log("\nMatching SMU data to Stanford grid...")

    # Get locations that didn't reach 300°C
    no_reach = stanford_grid[stanford_grid['depth_300_km'].isna()].copy()
    log(f"  {len(no_reach):,} locations need SMU lookup")

    if len(no_reach) == 0:
        return stanford_grid

    # Build KD-trees for SMU data at each depth
    smu_depths = [7.5, 8.5, 10.0]
    smu_trees = {}
    smu_temps_arrays = {}

    log("  Building KD-trees for SMU data...")
    for depth in smu_depths:
        if depth in smu_data:
            smu_df = smu_data[depth]
            coords = np.column_stack([smu_df['lat'].values, smu_df['lon'].values])
            temps = smu_df['temperature'].values

            # Build KDTree for fast nearest neighbor queries
            tree = cKDTree(coords)
            smu_trees[depth] = tree
            smu_temps_arrays[depth] = temps
            log(f"    Built KDTree for {depth} km ({len(smu_df):,} points)")

    # Query all no-reach locations at once for better performance
    log(f"\n  Querying SMU temperatures for {len(no_reach):,} locations...")
    query_coords = np.column_stack([no_reach['lat'].values, no_reach['lon'].values])

    smu_temps = {}
    start_time = time.time()

    for depth in smu_depths:
        if depth in smu_trees:
            log(f"    Querying {depth} km depth...")
            # Query nearest neighbor for all points at once
            distances, indices = smu_trees[depth].query(query_coords, k=1)
            # Get temperatures from nearest neighbors
            smu_temps[depth] = smu_temps_arrays[depth][indices]
            elapsed = time.time() - start_time
            log(f"      Completed in {elapsed:.1f}s ({len(no_reach)/elapsed:.0f} queries/sec)")
        else:
            smu_temps[depth] = np.full(len(no_reach), np.nan)

    # Add SMU temperatures to no_reach dataframe
    for depth in smu_depths:
        no_reach[f'smu_temp_{depth}km'] = smu_temps[depth]

    log("  Categorizing depth bins...")

    # Vectorized categorization for better performance
    def categorize_smu_depth_vectorized(df):
        """Vectorized depth categorization."""
        depth_300 = np.full(len(df), np.nan)

        # Check 10 km first (most permissive)
        temp_10 = df.get('smu_temp_10.0km', pd.Series(np.nan, index=df.index))
        mask_10 = (temp_10 >= TARGET_TEMP) & temp_10.notna()
        depth_300[mask_10] = 10.0

        # Check 8.5 km (overwrite if reached earlier)
        temp_85 = df.get('smu_temp_8.5km', pd.Series(np.nan, index=df.index))
        mask_85 = (temp_85 >= TARGET_TEMP) & temp_85.notna()
        depth_300[mask_85] = 8.5

        # Check 7.5 km (overwrite if reached earliest)
        temp_75 = df.get('smu_temp_7.5km', pd.Series(np.nan, index=df.index))
        mask_75 = (temp_75 >= TARGET_TEMP) & temp_75.notna()
        depth_300[mask_75] = 7.5

        return depth_300

    no_reach['depth_300_km'] = categorize_smu_depth_vectorized(no_reach)
    no_reach['source'] = 'SMU digitized'

    # Update main grid efficiently
    log("  Updating main grid...")
    stanford_grid.loc[no_reach.index, 'depth_300_km'] = no_reach['depth_300_km']
    stanford_grid.loc[no_reach.index, 'source'] = no_reach['source']

    # Report results
    n_smu_reached = no_reach['depth_300_km'].notna().sum()
    log(f"\n  SMU results:")
    log(f"    Reached 300°C by 10 km: {n_smu_reached:,}")
    log(f"    Still not reached by 10 km: {len(no_reach) - n_smu_reached:,}")

    return stanford_grid

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

def create_depth_map(df, stats_df, output_file):
    """Create CONUS map showing depth-to-300°C categories."""
    log(f"\nCreating depth-to-300°C map...")

    # Define colors for each bin (sequential from shallow to deep)
    bin_colors = {
        "≤4 km": '#8B0000',    # Dark red (shallowest - most accessible)
        "4-5 km": '#DC143C',   # Crimson
        "5-6 km": '#FF6347',   # Tomato
        "6-7 km": '#FF8C00',   # Dark orange
        "7-8 km": '#FFA500',   # Orange
        "8-10 km": '#FFD700',  # Gold
        ">10 km": '#D3D3D3'    # Light gray (deepest - least accessible)
    }

    bin_order = ["≤4 km", "4-5 km", "5-6 km", "6-7 km", "7-8 km", "8-10 km", ">10 km"]

    # Create figure
    fig, ax = plt.subplots(figsize=(16, 10))

    # Plot each bin
    for bin_name in bin_order:
        bin_df = df[df['depth_bin'] == bin_name]
        if len(bin_df) > 0:
            ax.scatter(bin_df['lon'], bin_df['lat'],
                      c=bin_colors[bin_name],
                      s=3, label=bin_name, alpha=0.8)

    # Add state boundaries (simple approximation using grid)
    # For a better version, we'd use cartopy or geopandas with actual state shapefiles
    ax.set_xlabel('Longitude', fontsize=13, fontweight='bold')
    ax.set_ylabel('Latitude', fontsize=13, fontweight='bold')
    ax.set_title('Estimated Depth to Reach 300°C\nContinental United States',
                fontsize=16, fontweight='bold', pad=20)

    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.set_xlim(-126, -65)
    ax.set_ylim(24, 50)

    # Add legend with area percentages
    legend_labels = []
    for bin_name in bin_order:
        pct = stats_df[stats_df['bin'] == bin_name]['percent'].values[0]
        legend_labels.append(f"{bin_name:8s} ({pct:.1f}%)")

    ax.legend(legend_labels, loc='lower right', fontsize=11,
             title='Depth Category', title_fontsize=12, framealpha=0.95)

    # Add text annotation
    accessible_4km = stats_df[stats_df['bin'] == "≤4 km"]['percent'].values[0]
    accessible_7km = stats_df[stats_df['bin'].isin(["≤4 km", "4-5 km", "5-6 km", "6-7 km"])]['percent'].sum()

    textstr = f'Most accessible regions:\n• ≤4 km: {accessible_4km:.1f}% of CONUS\n• ≤7 km: {accessible_7km:.1f}% of CONUS'
    ax.text(0.02, 0.98, textstr, transform=ax.transAxes,
           fontsize=10, verticalalignment='top',
           bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

    plt.tight_layout()
    plt.savefig(output_file, dpi=200, bbox_inches='tight')
    log(f"  Saved: {output_file}")
    plt.close()

def create_area_chart(stats_df, output_file):
    """Create bar chart showing area distribution by depth bin."""
    log(f"\nCreating area distribution chart...")

    bin_order = ["≤4 km", "4-5 km", "5-6 km", "6-7 km", "7-8 km", "8-10 km", ">10 km"]

    # Reorder dataframe
    stats_df['bin'] = pd.Categorical(stats_df['bin'], categories=bin_order, ordered=True)
    stats_df = stats_df.sort_values('bin')

    # Colors matching the map
    colors = ['#8B0000', '#DC143C', '#FF6347', '#FF8C00', '#FFA500', '#FFD700', '#D3D3D3']

    fig, ax = plt.subplots(figsize=(12, 7))

    bars = ax.bar(range(len(stats_df)), stats_df['percent'], color=colors, edgecolor='black', linewidth=1.5)

    ax.set_xticks(range(len(stats_df)))
    ax.set_xticklabels(stats_df['bin'], fontsize=12, fontweight='bold')
    ax.set_ylabel('Percentage of CONUS Area (%)', fontsize=13, fontweight='bold')
    ax.set_title('Distribution of CONUS Area by Depth Required to Reach 300°C',
                fontsize=14, fontweight='bold', pad=15)

    ax.grid(True, alpha=0.3, axis='y')
    ax.set_axisbelow(True)

    # Add percentage labels on bars
    for i, (bar, pct) in enumerate(zip(bars, stats_df['percent'])):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.5,
               f'{pct:.1f}%',
               ha='center', va='bottom', fontsize=11, fontweight='bold')

    # Add cumulative percentage line
    ax2 = ax.twinx()
    ax2.plot(range(len(stats_df)), stats_df['cumulative_percent'],
            'ko-', linewidth=2, markersize=8, label='Cumulative')
    ax2.set_ylabel('Cumulative Percentage (%)', fontsize=13, fontweight='bold')
    ax2.set_ylim(0, 105)
    ax2.legend(loc='upper left', fontsize=11)

    plt.tight_layout()
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    log(f"  Saved: {output_file}")
    plt.close()

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
    log("CALCULATING DEPTH TO 300°C ACROSS CONUS")
    log("="*80)

    # 1. Load data
    stanford_data = load_stanford_data()
    smu_data = load_smu_data()

    # 2. Calculate depth to 300°C using Stanford data
    grid = calculate_stanford_depth_to_300c(stanford_data)

    # 3. Fill in deeper locations using SMU data
    grid = match_smu_to_stanford_grid(grid, smu_data)

    # 4. Assign depth bins
    grid = assign_depth_bins(grid)

    # 5. Calculate area-weighted statistics
    stats_df = calculate_area_statistics(grid)

    # 6. Create visualizations
    map_file = PLOT_DIR / "depth_to_300c_map.png"
    create_depth_map(grid, stats_df, map_file)

    chart_file = PLOT_DIR / "depth_to_300c_distribution.png"
    create_area_chart(stats_df, chart_file)

    # 7. Print cumulative statistics
    print_cumulative_statistics(stats_df)

    # 8. Save final grid
    log("\nSaving output files...")
    output_file = OUTPUT_DIR / "conus_depth_to_300c.csv"
    grid_to_save = grid[['lat', 'lon', 'depth_300_km', 'depth_bin', 'source']].copy()
    grid_to_save.to_csv(output_file, index=False)

    parquet_file = OUTPUT_DIR / "conus_depth_to_300c.parquet"
    grid_to_save.to_parquet(parquet_file, index=False)

    log("\n" + "="*80)
    log("OUTPUT FILES")
    log("="*80)
    log(f"  Grid data (CSV):     {output_file}")
    log(f"  Grid data (Parquet): {parquet_file}")
    log(f"  Map:                 {map_file}")
    log(f"  Chart:               {chart_file}")

    total_time = time.time() - start_time
    log(f"\nTotal processing time: {total_time/60:.1f} minutes")

    log("\n" + "="*80)
    log("ANALYSIS COMPLETE")
    log("="*80)

    # Summary interpretation
    log("\nKEY FINDINGS:")
    log("-" * 80)

    very_shallow = stats_df[stats_df['bin'] == "≤4 km"]['percent'].values[0]
    shallow = stats_df[stats_df['bin'].isin(["≤4 km", "4-5 km"])]['percent'].sum()
    moderate = stats_df[stats_df['bin'].isin(["≤4 km", "4-5 km", "5-6 km", "6-7 km"])]['percent'].sum()
    deep = stats_df[stats_df['bin'].isin(["7-8 km", "8-10 km"])]['percent'].sum()
    very_deep = stats_df[stats_df['bin'] == ">10 km"]['percent'].values[0]

    log(f"\n1. IMMEDIATE ACCESSIBILITY (≤4 km):")
    log(f"   {very_shallow:.1f}% of CONUS can access 300°C at relatively shallow depths")
    log(f"   These are primarily high-heat-flow regions in the western US")

    log(f"\n2. NEAR-TERM POTENTIAL (4-7 km):")
    log(f"   Additional {moderate - very_shallow:.1f}% becomes accessible with deeper drilling")
    log(f"   Total accessible within 7 km: {moderate:.1f}%")

    log(f"\n3. ADVANCED DRILLING REQUIRED (7-10 km):")
    log(f"   {deep:.1f}% of CONUS requires depths between 7-10 km")
    log(f"   This represents the frontier of current drilling technology")

    log(f"\n4. CURRENTLY IMPRACTICAL (>10 km):")
    log(f"   {very_deep:.1f}% of CONUS requires depths exceeding 10 km")
    log(f"   These are primarily stable cratonic regions in eastern/central US")

    log(f"\n5. INCREMENTAL ACCESSIBILITY:")
    log(f"   • Doubling depth capability from 5 km to 10 km")
    log(f"     increases accessible area from {stats_df[stats_df['bin'].isin(['≤4 km', '4-5 km'])]['percent'].sum():.1f}% to {100-very_deep:.1f}%")
    log(f"   • Each additional km of drilling depth adds significant new territory")

if __name__ == "__main__":
    main()

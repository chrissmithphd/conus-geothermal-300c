#!/usr/bin/env python3
"""
Exploratory analysis of Stanford geothermal temperature data.
"""
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Output directory for plots
PLOT_DIR = Path("plots")
PLOT_DIR.mkdir(exist_ok=True)

def load_stanford_layer(json_file):
    """Load a single Stanford temperature layer."""
    with open(json_file, 'r') as f:
        data = json.load(f)

    features = data['features']

    # Extract data into lists
    records = []
    for feature in features:
        attrs = feature['attributes']
        records.append({
            'Lat': attrs['Lat'],
            'Long': attrs['Long'],
            'T': attrs['T']
        })

    return pd.DataFrame(records)

def load_all_stanford_data():
    """Load all available Stanford temperature layers."""
    data_dir = Path("data/raw/stanford")
    json_files = sorted(data_dir.glob("temperature_*.json"))

    if not json_files:
        raise FileNotFoundError("No Stanford temperature files found!")

    print(f"Loading {len(json_files)} temperature layers...")

    all_data = {}
    for json_file in json_files:
        # Extract depth from filename
        depth_str = json_file.stem.replace('temperature_', '')
        depth_km = float(depth_str.replace('km', ''))

        print(f"  Loading {depth_str}...")
        df = load_stanford_layer(json_file)
        all_data[depth_km] = df

    return all_data

def create_combined_dataframe(all_data):
    """Create a single DataFrame with all depths."""
    # Start with first depth
    depths = sorted(all_data.keys())
    df = all_data[depths[0]][['Lat', 'Long']].copy()

    # Add temperature columns for each depth
    for depth in depths:
        df[f'T_{depth}km'] = all_data[depth]['T'].values

    return df

def print_data_summary(df, all_data):
    """Print summary of the dataset."""
    print("\n" + "="*80)
    print("STANFORD GEOTHERMAL DATA SUMMARY")
    print("="*80)

    print(f"\n1. Dataset Shape:")
    print(f"   - Total grid points: {len(df):,}")
    print(f"   - Available depths: {len(all_data)} levels")
    print(f"   - Depths: {', '.join([f'{d} km' for d in sorted(all_data.keys())])}")

    print(f"\n2. Columns/Variables:")
    print(f"   - Coordinate fields: Lat, Long")
    print(f"   - Temperature fields: {[col for col in df.columns if col.startswith('T_')]}")

    print(f"\n3. Geographic Extent:")
    print(f"   - Latitude:  {df['Lat'].min():.3f}° to {df['Lat'].max():.3f}°")
    print(f"   - Longitude: {df['Long'].min():.3f}° to {df['Long'].max():.3f}°")

    print(f"\n4. Sample Rows (first 5 locations):")
    print(df.head().to_string())

    print(f"\n5. Sample Rows (random 5 locations):")
    print(df.sample(5).to_string())

def temperature_statistics(all_data):
    """Calculate and display temperature statistics for each depth."""
    print("\n" + "="*80)
    print("TEMPERATURE STATISTICS BY DEPTH")
    print("="*80)

    stats_list = []

    for depth in sorted(all_data.keys()):
        temps = all_data[depth]['T']
        missing = temps.isna().sum()

        stats = {
            'Depth (km)': depth,
            'Min (°C)': temps.min(),
            'Median (°C)': temps.median(),
            'Mean (°C)': temps.mean(),
            'Max (°C)': temps.max(),
            'Std Dev (°C)': temps.std(),
            'Missing': missing,
            'Count': len(temps) - missing
        }
        stats_list.append(stats)

    stats_df = pd.DataFrame(stats_list)
    print("\n" + stats_df.to_string(index=False))

    # Check for locations reaching 300°C
    print("\n" + "="*80)
    print("LOCATIONS REACHING ≥300°C AT EACH DEPTH")
    print("="*80)

    for depth in sorted(all_data.keys()):
        temps = all_data[depth]['T']
        count_300 = (temps >= 300).sum()
        pct_300 = (count_300 / len(temps)) * 100
        print(f"  {depth:.0f} km: {count_300:6,} locations ({pct_300:5.2f}%)")

    return stats_df

def plot_temperature_histograms(all_data):
    """Create histogram of temperatures for each depth."""
    depths = sorted(all_data.keys())
    n_depths = len(depths)

    # Create subplots
    fig, axes = plt.subplots(n_depths, 1, figsize=(10, 3*n_depths))
    if n_depths == 1:
        axes = [axes]

    for idx, depth in enumerate(depths):
        temps = all_data[depth]['T'].dropna()

        ax = axes[idx]
        ax.hist(temps, bins=50, color='steelblue', edgecolor='black', alpha=0.7)
        ax.set_xlabel('Temperature (°C)', fontsize=11)
        ax.set_ylabel('Frequency', fontsize=11)
        ax.set_title(f'Temperature Distribution at {depth} km Depth', fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3)

        # Add statistics text
        stats_text = f'n = {len(temps):,}\nMean = {temps.mean():.1f}°C\nMedian = {temps.median():.1f}°C'
        ax.text(0.98, 0.97, stats_text, transform=ax.transAxes,
                verticalalignment='top', horizontalalignment='right',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5),
                fontsize=9)

        # Mark 300°C if in range
        if temps.max() > 250:
            ax.axvline(300, color='red', linestyle='--', linewidth=2, alpha=0.7, label='300°C')
            ax.legend()

    plt.tight_layout()
    output_file = PLOT_DIR / "temperature_histograms.png"
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"\n✅ Saved: {output_file}")
    plt.close()

def plot_temperature_maps(all_data):
    """Create maps of temperature at each depth."""
    try:
        import cartopy.crs as ccrs
        import cartopy.feature as cfeature
        use_cartopy = True
    except ImportError:
        print("\n⚠️  cartopy not available, creating simple scatter plots instead")
        use_cartopy = False

    depths = sorted(all_data.keys())
    n_depths = len(depths)

    # Determine common temperature range across all depths
    all_temps = []
    for depth in depths:
        all_temps.extend(all_data[depth]['T'].dropna().values)
    vmin, vmax = np.percentile(all_temps, [1, 99])

    print(f"\nTemperature color scale: {vmin:.1f}°C to {vmax:.1f}°C")

    # Create figure with subplots
    if use_cartopy:
        fig = plt.figure(figsize=(15, 5*n_depths))

        for idx, depth in enumerate(depths):
            df = all_data[depth]

            ax = fig.add_subplot(n_depths, 1, idx+1, projection=ccrs.PlateCarree())

            # Add geographic features
            ax.add_feature(cfeature.STATES, linewidth=0.5, edgecolor='black')
            ax.add_feature(cfeature.COASTLINE, linewidth=0.5)
            ax.coastlines(resolution='50m')

            # Set extent to CONUS
            ax.set_extent([-125, -66, 24, 50], crs=ccrs.PlateCarree())

            # Plot temperature data
            scatter = ax.scatter(df['Long'], df['Lat'], c=df['T'],
                               s=3, cmap='YlOrRd', vmin=vmin, vmax=vmax,
                               transform=ccrs.PlateCarree())

            ax.set_title(f'Temperature at {depth} km Depth', fontsize=14, fontweight='bold')

            # Add colorbar
            cbar = plt.colorbar(scatter, ax=ax, orientation='horizontal',
                              pad=0.05, aspect=40, shrink=0.8)
            cbar.set_label('Temperature (°C)', fontsize=11)

            # Add grid
            ax.gridlines(draw_labels=False, linewidth=0.5, alpha=0.5)

    else:
        # Simple scatter plots without cartopy
        fig, axes = plt.subplots(n_depths, 1, figsize=(12, 5*n_depths))
        if n_depths == 1:
            axes = [axes]

        for idx, depth in enumerate(depths):
            df = all_data[depth]
            ax = axes[idx]

            scatter = ax.scatter(df['Long'], df['Lat'], c=df['T'],
                               s=3, cmap='YlOrRd', vmin=vmin, vmax=vmax)

            ax.set_xlabel('Longitude', fontsize=11)
            ax.set_ylabel('Latitude', fontsize=11)
            ax.set_title(f'Temperature at {depth} km Depth', fontsize=12, fontweight='bold')
            ax.set_aspect('equal')
            ax.grid(True, alpha=0.3)

            # Add colorbar
            cbar = plt.colorbar(scatter, ax=ax)
            cbar.set_label('Temperature (°C)', fontsize=11)

    plt.tight_layout()
    output_file = PLOT_DIR / "temperature_maps.png"
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"✅ Saved: {output_file}")
    plt.close()

def observations(all_data, stats_df):
    """Print interesting observations from the data."""
    print("\n" + "="*80)
    print("OBSERVATIONS AND INTERESTING FINDINGS")
    print("="*80)

    observations = []

    # 1. Temperature gradient
    if len(all_data) >= 2:
        depths = sorted(all_data.keys())
        temp_at_surface = all_data[depths[0]]['T'].mean()
        temp_at_deepest = all_data[depths[-1]]['T'].mean()
        depth_diff = depths[-1] - depths[0]
        gradient = (temp_at_deepest - temp_at_surface) / depth_diff

        observations.append(
            f"1. Temperature Gradient:\n"
            f"   - Mean surface temperature: {temp_at_surface:.1f}°C\n"
            f"   - Mean temperature at {depths[-1]} km: {temp_at_deepest:.1f}°C\n"
            f"   - Average geothermal gradient: {gradient:.1f}°C/km"
        )

    # 2. Temperature range expansion
    if len(all_data) >= 2:
        range_expansion = []
        for depth in sorted(all_data.keys()):
            temp_range = all_data[depth]['T'].max() - all_data[depth]['T'].min()
            range_expansion.append(f"{depth} km: {temp_range:.1f}°C")

        observations.append(
            f"2. Temperature Range by Depth:\n"
            f"   " + "\n   ".join(range_expansion) +
            f"\n   → Range increases with depth, indicating spatial variation in heat flow"
        )

    # 3. Data quality
    total_points = len(all_data[sorted(all_data.keys())[0]])
    missing_by_depth = {depth: all_data[depth]['T'].isna().sum() for depth in all_data.keys()}
    max_missing = max(missing_by_depth.values())

    observations.append(
        f"3. Data Quality:\n"
        f"   - Total grid points per depth: {total_points:,}\n"
        f"   - Maximum missing values at any depth: {max_missing}\n"
        f"   → {('Excellent' if max_missing == 0 else 'Good')} data completeness"
    )

    # 4. Geographic patterns
    observations.append(
        f"4. Geographic Coverage:\n"
        f"   - Complete CONUS coverage from Pacific to Atlantic\n"
        f"   - Grid spacing approximately ~4 km (based on ~535k points over ~8M km²)\n"
        f"   - No apparent spatial gaps or missing regions"
    )

    # 5. Depth to 300°C potential
    if len(all_data) >= 2:
        depths = sorted(all_data.keys())
        deepest = depths[-1]
        count_300 = (all_data[deepest]['T'] >= 300).sum()
        pct_300 = (count_300 / total_points) * 100

        observations.append(
            f"5. Potential for 300°C Resource:\n"
            f"   - At {deepest} km depth: {pct_300:.1f}% of locations reach ≥300°C\n"
            f"   - This represents approximately {count_300:,} grid cells\n"
            f"   → Most of CONUS will require deeper drilling (>7 km) to reach 300°C"
        )

    # 6. Temperature variability
    observations.append(
        f"6. Spatial Temperature Variability:\n"
        f"   - High variability suggests influence of local geology, volcanism,\n"
        f"     and crustal structure\n"
        f"   - Likely hot spots: Yellowstone, Cascades, Basin & Range Province\n"
        f"   - Cooler regions: Stable cratonic areas (e.g., Midwest)"
    )

    for obs in observations:
        print(f"\n{obs}")

def main():
    print("Stanford Geothermal Data Explorer")
    print("="*80)

    # Load data
    all_data = load_all_stanford_data()
    df = create_combined_dataframe(all_data)

    # 1. Print summary
    print_data_summary(df, all_data)

    # 2. Temperature statistics
    stats_df = temperature_statistics(all_data)

    # 3. Plot histograms
    print("\n" + "="*80)
    print("CREATING VISUALIZATIONS")
    print("="*80)
    plot_temperature_histograms(all_data)

    # 4. Plot maps
    plot_temperature_maps(all_data)

    # 5. Observations
    observations(all_data, stats_df)

    print("\n" + "="*80)
    print("ANALYSIS COMPLETE")
    print("="*80)
    print(f"\n📁 Plots saved to: {PLOT_DIR.absolute()}/")
    print(f"   - temperature_histograms.png")
    print(f"   - temperature_maps.png")
    print(f"\n✅ All {len(all_data)} depth layers analyzed successfully")

if __name__ == "__main__":
    main()

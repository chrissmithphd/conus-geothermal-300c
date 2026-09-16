#!/usr/bin/env python3
"""
Montana Regional Validation Plot

Zoomed view of Montana/Yellowstone region showing:
- All grid cells with depth categories
- State boundaries for geographic reference
- Labeled cities/landmarks for validation
"""
import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

# Load data
df = pd.read_csv("data/processed/conus_depth_to_300c.csv")

# Load state boundaries
states = gpd.read_file("data/raw/boundaries/cb_2023_us_state_20m.shp")
states = states[~states["STUSPS"].isin({"AK", "HI", "PR", "VI", "GU", "MP", "AS"})]
states = states.to_crs("EPSG:4326")

# Montana region bounds
lon_min, lon_max = -116, -104
lat_min, lat_max = 43.5, 49.5

# Filter to region
region_df = df[(df['lon'] >= lon_min) & (df['lon'] <= lon_max) &
               (df['lat'] >= lat_min) & (df['lat'] <= lat_max)].copy()

print(f"Montana region: {len(region_df):,} grid cells")
print("\nDepth distribution in Montana region:")
for bin_name in ["≤4 km", "4-5 km", "5-6 km", "6-7 km", "7-8 km", "8-10 km", ">10 km"]:
    count = (region_df['depth_bin'] == bin_name).sum()
    pct = (count / len(region_df)) * 100 if len(region_df) > 0 else 0
    print(f"  {bin_name:8s}: {count:5,} ({pct:5.1f}%)")

# Exact color scheme
COLORS = {
    "≤4 km": '#08306B',
    "4-5 km": '#2171B5',
    "5-6 km": '#00B050',
    "6-7 km": '#FFE100',
    "7-8 km": '#FF8C00',
    "8-10 km": '#E31A1C',
    ">10 km": '#D9D9D9'
}

# Create figure
fig, ax = plt.subplots(figsize=(16, 12))
ax.set_facecolor('#F5F5F5')

# Plot cells by depth category (deepest first)
bin_order = ["≤4 km", "4-5 km", "5-6 km", "6-7 km", "7-8 km", "8-10 km", ">10 km"]

for bin_name in reversed(bin_order):
    bin_df = region_df[region_df['depth_bin'] == bin_name]
    if len(bin_df) > 0:
        # Size based on rarity
        if bin_name in ["≤4 km", "4-5 km"]:
            size = 80
            alpha = 1.0
            edge = 'black'
            width = 1.0
        elif bin_name == "5-6 km":
            size = 50
            alpha = 0.95
            edge = 'black'
            width = 0.8
        elif bin_name == "6-7 km":
            size = 35
            alpha = 0.9
            edge = 'black'
            width = 0.5
        elif bin_name in ["7-8 km", "8-10 km"]:
            size = 25
            alpha = 0.85
            edge = 'none'
            width = 0
        else:
            size = 15
            alpha = 0.6
            edge = 'none'
            width = 0

        ax.scatter(bin_df['lon'], bin_df['lat'],
                  c=COLORS[bin_name],
                  s=size,
                  alpha=alpha,
                  edgecolors=edge,
                  linewidths=width,
                  label=f"{bin_name} ({len(bin_df):,} cells)",
                  zorder=100 - bin_order.index(bin_name))

# Add state boundaries
states_region = states.cx[lon_min:lon_max, lat_min:lat_max]
states_region.boundary.plot(ax=ax, linewidth=1.5, edgecolor='black', alpha=0.8, zorder=200)

# Add reference locations
locations = {
    'Yellowstone': (-110.5, 44.6),
    'Billings': (-108.5, 45.8),
    'Missoula': (-114.0, 46.9),
    'Great Falls': (-111.3, 47.5),
    'Butte': (-112.5, 46.0),
    'Bozeman': (-111.0, 45.7),
}

for name, (lon, lat) in locations.items():
    ax.plot(lon, lat, 'k*', markersize=12, markeredgewidth=1.5,
            markerfacecolor='white', zorder=250)
    ax.text(lon, lat + 0.15, name, fontsize=10, fontweight='bold',
           ha='center', va='bottom',
           bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                    edgecolor='black', alpha=0.9), zorder=250)

# Styling
ax.set_xlabel('Longitude', fontsize=14, fontweight='bold')
ax.set_ylabel('Latitude', fontsize=14, fontweight='bold')
ax.set_title('Montana/Yellowstone Regional Validation - Depth to 300°C\n'
            'Grid Cell Resolution: ~3 km',
            fontsize=16, fontweight='bold', pad=15)

ax.set_xlim(lon_min, lon_max)
ax.set_ylim(lat_min, lat_max)
ax.set_aspect('equal')
ax.grid(True, alpha=0.2, linestyle=':', linewidth=0.5, color='gray', zorder=0)

# Legend (drawn last with high z-order to appear on top)
legend = ax.legend(loc='upper right', fontsize=11,
                  title='Depth Category',
                  title_fontsize=12,
                  framealpha=0.98,
                  edgecolor='black',
                  fancybox=True)
legend.get_title().set_fontweight('bold')
legend.set_zorder(300)  # Ensure legend is on top

# Add scale bar
scale_lon = lon_min + 1
scale_lat = lat_min + 0.5
scale_width = 2.0  # 2 degrees longitude ≈ 150 km at this latitude
ax.plot([scale_lon, scale_lon + scale_width], [scale_lat, scale_lat],
       'k-', linewidth=3, zorder=250)
ax.text(scale_lon + scale_width/2, scale_lat - 0.2, '~150 km',
       fontsize=10, ha='center', fontweight='bold',
       bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.9))

plt.tight_layout()
plt.savefig('plots/montana_validation.png', dpi=300, bbox_inches='tight', facecolor='white')
print("\n✅ Saved: plots/montana_validation.png")
plt.close()

# Also create a Yellowstone close-up
print("\nCreating Yellowstone close-up...")

# Yellowstone region
ys_lon_min, ys_lon_max = -111.5, -109.5
ys_lat_min, ys_lat_max = 44.0, 45.5

ys_df = df[(df['lon'] >= ys_lon_min) & (df['lon'] <= ys_lon_max) &
           (df['lat'] >= ys_lat_min) & (df['lat'] <= ys_lat_max)].copy()

print(f"Yellowstone region: {len(ys_df):,} grid cells")
print("\nDepth distribution near Yellowstone:")
for bin_name in bin_order:
    count = (ys_df['depth_bin'] == bin_name).sum()
    pct = (count / len(ys_df)) * 100 if len(ys_df) > 0 else 0
    print(f"  {bin_name:8s}: {count:5,} ({pct:5.1f}%)")

fig, ax = plt.subplots(figsize=(14, 12))
ax.set_facecolor('#F5F5F5')

for bin_name in reversed(bin_order):
    bin_df = ys_df[ys_df['depth_bin'] == bin_name]
    if len(bin_df) > 0:
        if bin_name in ["≤4 km", "4-5 km"]:
            size = 120
            alpha = 1.0
            edge = 'black'
            width = 1.5
        elif bin_name == "5-6 km":
            size = 80
            alpha = 0.95
            edge = 'black'
            width = 1.0
        elif bin_name == "6-7 km":
            size = 50
            alpha = 0.9
            edge = 'black'
            width = 0.5
        else:
            size = 30
            alpha = 0.8
            edge = 'none'
            width = 0

        ax.scatter(bin_df['lon'], bin_df['lat'],
                  c=COLORS[bin_name],
                  s=size,
                  alpha=alpha,
                  edgecolors=edge,
                  linewidths=width,
                  label=f"{bin_name} ({len(bin_df):,})",
                  zorder=100 - bin_order.index(bin_name))

# State boundaries
states_ys = states.cx[ys_lon_min:ys_lon_max, ys_lat_min:ys_lat_max]
states_ys.boundary.plot(ax=ax, linewidth=1.5, edgecolor='black', alpha=0.8, zorder=200)

# Yellowstone caldera outline (approximate)
caldera_lon = [-111.1, -110.9, -110.6, -110.4, -110.4, -110.8, -111.1, -111.1]
caldera_lat = [44.3, 44.4, 44.5, 44.5, 44.1, 44.1, 44.2, 44.3]
ax.plot(caldera_lon, caldera_lat, 'k--', linewidth=2, alpha=0.7,
       label='Yellowstone Caldera (approx)', zorder=250)

# Reference points
ys_locations = {
    'Old Faithful': (-110.83, 44.46),
    'West Yellowstone': (-111.1, 44.66),
    'Mammoth': (-110.70, 44.98),
}

for name, (lon, lat) in ys_locations.items():
    ax.plot(lon, lat, 'k*', markersize=15, markeredgewidth=1.5,
            markerfacecolor='yellow', zorder=250)
    ax.text(lon, lat + 0.08, name, fontsize=11, fontweight='bold',
           ha='center', va='bottom',
           bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                    edgecolor='black', alpha=0.95), zorder=250)

ax.set_xlabel('Longitude', fontsize=14, fontweight='bold')
ax.set_ylabel('Latitude', fontsize=14, fontweight='bold')
ax.set_title('Yellowstone National Park - Depth to 300°C\n'
            'Known Geothermal System',
            fontsize=16, fontweight='bold', pad=15)

ax.set_xlim(ys_lon_min, ys_lon_max)
ax.set_ylim(ys_lat_min, ys_lat_max)
ax.set_aspect('equal')
ax.grid(True, alpha=0.2, linestyle=':', linewidth=0.5, color='gray', zorder=0)

legend = ax.legend(loc='lower left', fontsize=10,
                  title='Depth Category',
                  title_fontsize=11,
                  framealpha=0.98,
                  edgecolor='black')
legend.get_title().set_fontweight('bold')
legend.set_zorder(300)

plt.tight_layout()
plt.savefig('plots/yellowstone_validation.png', dpi=300, bbox_inches='tight', facecolor='white')
print("✅ Saved: plots/yellowstone_validation.png")
plt.close()

print("\n" + "="*60)
print("VALIDATION PLOTS COMPLETE")
print("="*60)
print("\nExpected patterns:")
print("• Yellowstone/Snake River Plain: 6-8 km depth (active hotspot)")
print("• Western MT mountains: 6-9 km (Basin & Range extension)")
print("• Eastern MT plains: >10 km (stable craton)")
print("\nThese regional plots allow verification that:")
print("1. Known geothermal systems (Yellowstone) show shallow depths")
print("2. Geographic patterns match tectonic provinces")
print("3. Grid resolution (~3 km) captures local variations")

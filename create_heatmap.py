#!/usr/bin/env python3
"""
Create smooth heatmap version of depth-to-300C map with state boundaries.
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm
from scipy.interpolate import griddata

# Load data
df = pd.read_csv("data/processed/conus_depth_to_300c.csv")

# Map categories to numeric values for interpolation
depth_map = {
    "≤4 km": 3,
    "4-5 km": 4.5,
    "5-6 km": 5.5,
    "6-7 km": 6.5,
    "7-8 km": 7.5,
    "8-10 km": 9,
    ">10 km": 12
}

df['depth_numeric'] = df['depth_bin'].map(depth_map)

# Create grid for interpolation
lon_min, lon_max = -126, -65
lat_min, lat_max = 24, 50.5

# High resolution grid
grid_lon = np.linspace(lon_min, lon_max, 1200)
grid_lat = np.linspace(lat_min, lat_max, 600)
grid_lon_2d, grid_lat_2d = np.meshgrid(grid_lon, grid_lat)

print("Creating smooth heatmap interpolation...")
# Interpolate to create smooth heatmap
points = np.column_stack([df['lon'].values, df['lat'].values])
values = df['depth_numeric'].values

grid_depth = griddata(points, values, (grid_lon_2d, grid_lat_2d), method='linear')

# Create figure
fig, ax = plt.subplots(figsize=(20, 11))
ax.set_facecolor('#E8E8E8')

# Define colors for heatmap (continuous)
colors = ['#0000CC', '#0066FF', '#00CC00', '#FFFF00', '#FF9900', '#FF3300', '#CCCCCC']
boundaries = [0, 3.5, 5, 6, 7, 8, 10, 15]
cmap = ListedColormap(colors)
norm = BoundaryNorm(boundaries, cmap.N)

# Plot heatmap
im = ax.contourf(grid_lon_2d, grid_lat_2d, grid_depth,
                 levels=boundaries, cmap=cmap, norm=norm, extend='both')

# Add state boundaries (US states approximate lat/lon lines)
state_boundaries = {
    'WA/OR': 46.0, 'OR/CA': 42.0, 'CA/Mexico': 32.5,
    'ID/MT': 45.0, 'WY/CO': 41.0, 'CO/NM': 37.0, 'NM/Mexico': 32.0,
    'ND/SD': 46.0, 'SD/NE': 43.0, 'NE/KS': 40.0, 'KS/OK': 37.0, 'OK/TX': 36.5,
    'MN/IA': 43.5, 'IA/MO': 40.5, 'MO/AR': 36.5,
    'WI/IL': 42.5, 'IL/KY': 37.0, 'KY/TN': 36.5, 'TN/GA': 35.0, 'GA/FL': 30.7,
    'VA/NC': 36.5, 'NC/SC': 34.0, 'SC/GA': 32.5
}

# Vertical state lines (longitude)
state_lons = {
    'WA/ID': -117, 'ID/MT': -116, 'ID/WY': -111, 'MT/ND': -104,
    'WY/NE': -104, 'CO/KS': -102, 'NM/TX': -103, 'TX/OK': -100,
    'OK/AR': -94.5, 'AR/MS': -91, 'MS/AL': -88, 'AL/GA': -85,
    'GA/SC': -81, 'SC/NC': -80, 'NC/VA': -77, 'MD/DE': -75.5
}

# Draw state boundaries
for name, lat in state_boundaries.items():
    ax.axhline(lat, color='white', linewidth=1.2, alpha=0.6, zorder=5)

for name, lon in state_lons.items():
    ax.axvline(lon, color='white', linewidth=1.2, alpha=0.6, zorder=5)

# More detailed grid
for lon in range(-125, -65, 2):
    ax.axvline(lon, color='white', linewidth=0.3, alpha=0.3, zorder=4)
for lat in range(25, 50, 1):
    ax.axhline(lat, color='white', linewidth=0.3, alpha=0.3, zorder=4)

# Styling
ax.set_xlabel('Longitude', fontsize=16, fontweight='bold')
ax.set_ylabel('Latitude', fontsize=16, fontweight='bold')
ax.set_title('Depth Required to Reach 300°C Supercritical Geothermal Conditions\nContinental United States',
            fontsize=20, fontweight='bold', pad=20)

ax.set_xlim(lon_min, lon_max)
ax.set_ylim(lat_min, lat_max)
ax.set_aspect('equal')

# Colorbar with discrete categories
cbar = plt.colorbar(im, ax=ax, orientation='horizontal', pad=0.05,
                     aspect=50, shrink=0.8, ticks=[3, 4.5, 5.5, 6.5, 7.5, 9, 12])
cbar.set_label('Drilling Depth Required (km)', fontsize=14, fontweight='bold')
cbar.ax.set_xticklabels(['≤4\n(0.0%)', '4-5\n(0.0%)', '5-6\n(0.2%)',
                         '6-7\n(4.9%)', '7-8\n(0.4%)', '8-10\n(11.6%)',
                         '>10\n(82.9%)'], fontsize=11)

# Add summary text (clean, no box clutter)
summary = (
    "CONUS Supercritical Geothermal Accessibility\n\n"
    "Only 5.0% accessible within proven drilling depths (≤7 km)\n"
    "83% requires depths exceeding current technology (>10 km)\n"
    "Western US extensional tectonics = high accessibility\n"
    "Eastern US cratonic stability = very deep requirements"
)

props = dict(boxstyle='round,pad=0.8', facecolor='white', alpha=0.92,
             edgecolor='gray', linewidth=1.5)
ax.text(0.015, 0.97, summary, transform=ax.transAxes,
       fontsize=11, verticalalignment='top', bbox=props,
       family='sans-serif', linespacing=1.5)

# Data source (bottom)
source = "Data: Stanford Thermal Earth Model (2024) + SMU Geothermal Lab (2011) | Analysis: 534,942 grid points"
ax.text(0.5, -0.08, source, transform=ax.transAxes,
       fontsize=10, ha='center', style='italic', color='#666')

plt.tight_layout()
plt.savefig('plots/depth_to_300c_heatmap.png', dpi=300, bbox_inches='tight', facecolor='white')
print("✅ Saved: plots/depth_to_300c_heatmap.png")
plt.close()

print("\nHeatmap created successfully!")
print("Smooth interpolation shows physical heat flow patterns")
print("State boundaries visible as white grid lines")

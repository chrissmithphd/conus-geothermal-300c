#!/usr/bin/env python3
"""
Create smooth heatmap version of depth-to-300C map with state boundaries.
"""
import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm
from scipy.interpolate import griddata

# Load data
df = pd.read_csv("data/processed/conus_depth_to_300c.csv")

# Load state boundaries
states = gpd.read_file("data/raw/boundaries/cb_2023_us_state_20m.shp")
states = states[~states["STUSPS"].isin({"AK", "HI", "PR", "VI", "GU", "MP", "AS"})]
states = states.to_crs("EPSG:4326")

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

# Add state boundaries
states.boundary.plot(ax=ax, linewidth=0.8, edgecolor='white', alpha=0.7, zorder=5)

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
cbar.ax.set_xticklabels(['≤4\n(0.0%)', '4-5\n(0.01%)', '5-6\n(0.5%)',
                         '6-7\n(4.2%)', '7-8\n(2.5%)', '8-10\n(14.4%)',
                         '>10\n(78.3%)'], fontsize=11)

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

#!/usr/bin/env python3
"""
Create depth-to-300C map with ALL categories and interactive Leaflet map.
"""
import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt

# Load ORIGINAL data
df = pd.read_csv("data/processed/conus_depth_to_300c.csv")

# Load state boundaries
states = gpd.read_file("data/raw/boundaries/cb_2023_us_state_20m.shp")
states = states[~states["STUSPS"].isin({"AK", "HI", "PR", "VI", "GU", "MP", "AS"})]
states = states.to_crs("EPSG:4326")

print(f"Loaded {len(df):,} grid points")
print("\nActual distribution:")
print(df['depth_bin'].value_counts().sort_index())

# Define ALL 7 categories with distinct colors (blue → green → yellow → orange → red → gray)
bin_order = ["≤4 km", "4-5 km", "5-6 km", "6-7 km", "7-8 km", "8-10 km", ">10 km"]

colors_all = {
    "≤4 km": '#0000CC',      # Dark blue (shallowest - MOST critical)
    "4-5 km": '#0066FF',     # Blue
    "5-6 km": '#00CC00',     # Green
    "6-7 km": '#FFFF00',     # Yellow
    "7-8 km": '#FF9900',     # Orange
    "8-10 km": '#FF3300',    # Red-orange
    ">10 km": '#CCCCCC'      # Gray (deepest - least accessible)
}

# Count actual occurrences
print("\nCounts per bin:")
for bin_name in bin_order:
    count = (df['depth_bin'] == bin_name).sum()
    pct = (count / len(df)) * 100
    print(f"  {bin_name:10s}: {count:7,} ({pct:5.2f}%)")

# STATIC MAP with ALL categories
fig, ax = plt.subplots(figsize=(20, 12))
ax.set_facecolor('#F5F5F5')

# Plot in reverse order (deepest first) so shallow shows on top
for bin_name in reversed(bin_order):
    bin_df = df[df['depth_bin'] == bin_name]
    if len(bin_df) > 0:
        count = len(bin_df)
        pct = (count / len(df)) * 100

        # Dot size: larger for rare shallow, normal for deep
        if bin_name in ["≤4 km", "4-5 km"]:
            size = 50  # HUGE dots for the rare shallow ones
        elif bin_name == "5-6 km":
            size = 30
        elif bin_name == "6-7 km":
            size = 20
        elif bin_name in ["7-8 km", "8-10 km"]:
            size = 15
        else:
            size = 8  # Gray background

        alpha = 0.5 if bin_name == ">10 km" else 0.9

        ax.scatter(bin_df['lon'], bin_df['lat'],
                  c=colors_all[bin_name],
                  s=size,
                  alpha=alpha,
                  edgecolors='black' if size > 20 else 'none',
                  linewidths=0.5 if size > 20 else 0,
                  label=f"{bin_name}: {pct:.2f}%",
                  zorder=100-bin_order.index(bin_name))

# Add state boundaries (draw AFTER scatter plots so they appear on top)
states.boundary.plot(ax=ax, linewidth=1.0, edgecolor='black', alpha=0.6, zorder=150)

ax.set_xlabel('Longitude', fontsize=16, fontweight='bold')
ax.set_ylabel('Latitude', fontsize=16, fontweight='bold')
ax.set_title('Depth Required to Reach 300°C - Continental United States\n(All Categories Shown - No Binning)',
            fontsize=20, fontweight='bold', pad=20)

ax.set_xlim(-126, -65)
ax.set_ylim(24, 50.5)
ax.set_aspect('equal')
ax.grid(True, alpha=0.15, linestyle=':', linewidth=0.5, color='gray', zorder=0)

# Legend
legend = ax.legend(loc='lower right', fontsize=14,
                  title='Depth Category',
                  title_fontsize=16,
                  framealpha=0.98,
                  edgecolor='black',
                  fancybox=True,
                  shadow=True,
                  markerscale=2)
legend.get_title().set_fontweight('bold')
legend.set_zorder(300)  # Draw legend on top of everything

plt.tight_layout()
# Save as both filenames (README uses points.png)
plt.savefig('plots/depth_to_300c_all_categories.png', dpi=300, bbox_inches='tight', facecolor='white')
plt.savefig('plots/depth_to_300c_points.png', dpi=300, bbox_inches='tight', facecolor='white')
print("\n✅ Saved: plots/depth_to_300c_all_categories.png")
print("✅ Saved: plots/depth_to_300c_points.png")
plt.close()

# INTERACTIVE LEAFLET MAP
print("\nCreating interactive Leaflet map...")

import folium
from folium.plugins import MarkerCluster

# Sample data for performance (every 10th point for ≤10km, every 50th for >10km)
df_plot = pd.concat([
    df[df['depth_bin'] != '>10 km'].iloc[::10],  # More detail for shallow
    df[df['depth_bin'] == '>10 km'].iloc[::50]   # Less detail for deep (gray background)
])

print(f"Plotting {len(df_plot):,} points (sampled from {len(df):,} total)")

# Create map centered on CONUS
m = folium.Map(
    location=[39.8, -98.5],
    zoom_start=5,
    tiles='OpenStreetMap',
    control_scale=True
)

# Add data points with clustering for performance
marker_cluster = MarkerCluster(
    name='Geothermal Depth Data',
    overlay=True,
    control=True,
    show=True
).add_to(m)

# Add points
print("Adding data points...")
for idx, row in df_plot.iterrows():
    folium.CircleMarker(
        location=[row['lat'], row['lon']],
        radius=3 if row['depth_bin'] != '>10 km' else 1,
        popup=folium.Popup(
            f"<b>Depth to 300°C:</b> {row['depth_bin']}<br>"
            f"<b>Location:</b> {row['lat']:.2f}°N, {abs(row['lon']):.2f}°W<br>"
            f"<b>Source:</b> {row['source']}",
            max_width=250
        ),
        tooltip=f"{row['depth_bin']}",
        color=colors_all[row['depth_bin']],
        fill=True,
        fillColor=colors_all[row['depth_bin']],
        fillOpacity=0.7 if row['depth_bin'] != '>10 km' else 0.3,
        weight=1
    ).add_to(marker_cluster)

# Add major city markers
cities = {
    'Denver, CO': (39.74, -104.99),
    'Salt Lake City, UT': (40.76, -111.89),
    'Las Vegas, NV': (36.17, -115.14),
    'Phoenix, AZ': (33.45, -112.07),
    'Los Angeles, CA': (34.05, -118.24),
    'San Francisco, CA': (37.77, -122.42),
    'Portland, OR': (45.52, -122.68),
    'Seattle, WA': (47.61, -122.33),
    'Boise, ID': (43.62, -116.21),
    'Albuquerque, NM': (35.08, -106.65),
    'Yellowstone, WY': (44.43, -110.59),
    'New York, NY': (40.71, -74.01),
    'Chicago, IL': (41.88, -87.63),
    'Houston, TX': (29.76, -95.37)
}

print("Adding city markers...")
for city, (lat, lon) in cities.items():
    # Find nearest grid cell
    distances = np.sqrt((df['lat'] - lat)**2 + (df['lon'] - lon)**2)
    nearest_idx = distances.idxmin()
    nearest = df.loc[nearest_idx]

    folium.Marker(
        location=[lat, lon],
        popup=folium.Popup(
            f"<h4>{city}</h4>"
            f"<b>Modeled depth to 300°C:</b> {nearest['depth_bin']}<br>"
            f"<b>Grid cell distance:</b> {distances.min()*111:.1f} km<br>"
            f"<i>Note: Nearest ~3km grid cell</i>",
            max_width=300
        ),
        tooltip=city,
        icon=folium.Icon(color='red', icon='info-sign')
    ).add_to(m)

# Add legend
legend_html = '''
<div style="position: fixed;
     bottom: 50px; right: 50px; width: 200px; height: auto;
     background-color: white; border:2px solid grey; z-index:9999;
     font-size:14px; padding: 10px; border-radius: 5px;
     box-shadow: 0 0 15px rgba(0,0,0,0.2);">
<h4 style="margin-top:0;">Depth to 300°C</h4>
<div style="margin: 5px 0;">
    <span style="display:inline-block; width:20px; height:20px;
          background:#08306B; border:1px solid black;"></span> ≤4 km
</div>
<div style="margin: 5px 0;">
    <span style="display:inline-block; width:20px; height:20px;
          background:#2171B5; border:1px solid black;"></span> 4-5 km
</div>
<div style="margin: 5px 0;">
    <span style="display:inline-block; width:20px; height:20px;
          background:#00B050; border:1px solid black;"></span> 5-6 km
</div>
<div style="margin: 5px 0;">
    <span style="display:inline-block; width:20px; height:20px;
          background:#FFE100; border:1px solid black;"></span> 6-7 km
</div>
<div style="margin: 5px 0;">
    <span style="display:inline-block; width:20px; height:20px;
          background:#FF8C00; border:1px solid black;"></span> 7-8 km
</div>
<div style="margin: 5px 0;">
    <span style="display:inline-block; width:20px; height:20px;
          background:#E31A1C; border:1px solid black;"></span> 8-10 km
</div>
<div style="margin: 5px 0;">
    <span style="display:inline-block; width:20px; height:20px;
          background:#D9D9D9; border:1px solid black;"></span> >10 km
</div>
<p style="font-size:11px; margin-top:10px; color:#666;">
Click markers for details.<br>
Zoom to explore regions.
</p>
</div>
'''
m.get_root().html.add_child(folium.Element(legend_html))

# Add layer control
folium.LayerControl().add_to(m)

# Save
print("Saving interactive map...")
m.save('index.html')
print("✅ Saved: index.html")

import os
size_mb = os.path.getsize('index.html') / (1024*1024)
print(f"File size: {size_mb:.1f} MB")

print("\n" + "="*80)
print("ALL MAPS CREATED SUCCESSFULLY")
print("="*80)
print("\n1. Static map (all categories): plots/depth_to_300c_all_categories.png")
print("2. Static map (points version): plots/depth_to_300c_points.png")
print("3. Interactive Leaflet map:     index.html")

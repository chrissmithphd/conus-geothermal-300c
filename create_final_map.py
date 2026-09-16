#!/usr/bin/env python3
"""
Create PROPER depth-to-300C map with ALL categories, no collapsing.
Uses the ACTUAL calculated data without modification.
"""
import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go

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

# Add state boundaries
states.boundary.plot(ax=ax, linewidth=0.8, edgecolor='white', alpha=0.7, zorder=50)

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
                  framealpha=0.95,
                  edgecolor='black',
                  fancybox=True,
                  shadow=True,
                  markerscale=2)
legend.get_title().set_fontweight('bold')

plt.tight_layout()
plt.savefig('plots/depth_to_300c_all_categories.png', dpi=300, bbox_inches='tight', facecolor='white')
print("\n✅ Saved: plots/depth_to_300c_all_categories.png")
plt.close()

# INTERACTIVE ZOOMABLE MAP with plotly
print("\nCreating interactive zoomable map...")

# Add hover text
df['hover_text'] = df.apply(
    lambda row: f"Lat: {row['lat']:.2f}<br>Lon: {row['lon']:.2f}<br>Depth: {row['depth_bin']}<br>Source: {row['source']}",
    axis=1
)

# Create plotly figure
fig = go.Figure()

# Add traces for each category in reverse order
for bin_name in reversed(bin_order):
    bin_df = df[df['depth_bin'] == bin_name]
    if len(bin_df) > 0:
        count = len(bin_df)
        pct = (count / len(df)) * 100

        # Marker size
        if bin_name in ["≤4 km", "4-5 km"]:
            size = 8
        elif bin_name == "5-6 km":
            size = 6
        elif bin_name == "6-7 km":
            size = 5
        elif bin_name in ["7-8 km", "8-10 km"]:
            size = 4
        else:
            size = 3

        fig.add_trace(go.Scattergl(
            x=bin_df['lon'],
            y=bin_df['lat'],
            mode='markers',
            name=f"{bin_name}: {pct:.2f}%",
            marker=dict(
                color=colors_all[bin_name],
                size=size,
                opacity=0.6 if bin_name == ">10 km" else 0.9,
                line=dict(width=0)
            ),
            text=bin_df['hover_text'],
            hovertemplate='%{text}<extra></extra>'
        ))

fig.update_layout(
    title={
        'text': 'Interactive: Depth to 300°C Across CONUS<br><sub>Zoom, pan, and hover for details</sub>',
        'x': 0.5,
        'xanchor': 'center',
        'font': {'size': 20}
    },
    xaxis_title='Longitude',
    yaxis_title='Latitude',
    width=1400,
    height=800,
    hovermode='closest',
    showlegend=True,
    legend=dict(
        title='Depth Category',
        yanchor="bottom",
        y=0.01,
        xanchor="right",
        x=0.99
    )
)

fig.update_xaxes(range=[-126, -65])
fig.update_yaxes(range=[24, 50.5], scaleanchor="x", scaleratio=1)

# Save interactive HTML
fig.write_html('plots/depth_to_300c_interactive.html')
print("✅ Saved: plots/depth_to_300c_interactive.html")

# Also save as static image from plotly
fig.write_image('plots/depth_to_300c_plotly.png', width=1400, height=800, scale=2)
print("✅ Saved: plots/depth_to_300c_plotly.png")

print("\n" + "="*80)
print("ALL MAPS CREATED SUCCESSFULLY")
print("="*80)
print("\n1. Static map (all categories): plots/depth_to_300c_all_categories.png")
print("2. Interactive HTML (zoomable): plots/depth_to_300c_interactive.html")
print("3. Plotly static export:        plots/depth_to_300c_plotly.png")

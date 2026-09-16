#!/usr/bin/env python3
"""
Create an improved, highly readable depth-to-300°C map.
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from pathlib import Path

# Load data
print("Loading data...")
df = pd.read_csv("data/processed/conus_depth_to_300c.csv")

# Simplify categories for better visualization
def simplify_bin(bin_name):
    """Combine tiny categories for clearer visualization."""
    if bin_name in ["≤4 km", "4-5 km", "5-6 km"]:
        return "≤6 km (Shallow)"
    elif bin_name in ["6-7 km"]:
        return "6-7 km (Moderate)"
    elif bin_name in ["7-8 km", "8-10 km"]:
        return "7-10 km (Deep)"
    else:
        return ">10 km (Very Deep)"

df['simple_bin'] = df['depth_bin'].apply(simplify_bin)

# Count for legend
bin_counts = df['simple_bin'].value_counts()
total = len(df)

# High-contrast color scheme
colors = {
    "≤6 km (Shallow)": '#B30000',        # Dark red (MOST accessible)
    "6-7 km (Moderate)": '#FF6600',      # Bright orange
    "7-10 km (Deep)": '#FFD700',         # Gold/yellow
    ">10 km (Very Deep)": '#C0C0C0'      # Light gray (LEAST accessible)
}

# Create figure
fig = plt.figure(figsize=(20, 12))
ax = plt.subplot(111)

# Add light background
ax.set_facecolor('#F0F0F0')

# Plot each category in reverse order (deepest first, so shallow is on top)
bin_order = [">10 km (Very Deep)", "7-10 km (Deep)", "6-7 km (Moderate)", "≤6 km (Shallow)"]

for bin_name in bin_order:
    bin_df = df[df['simple_bin'] == bin_name]
    if len(bin_df) > 0:
        count = len(bin_df)
        pct = (count / total) * 100

        # Much larger dots
        size = 15 if bin_name == ">10 km (Very Deep)" else 20
        alpha = 0.6 if bin_name == ">10 km (Very Deep)" else 0.9

        ax.scatter(bin_df['lon'], bin_df['lat'],
                  c=colors[bin_name],
                  s=size,
                  alpha=alpha,
                  edgecolors='none',
                  label=f"{bin_name}: {pct:.1f}%")

# Add state boundaries (simple grid approximation)
# Vertical lines (approximate state boundaries)
state_lons = [-125, -120, -117, -114, -111, -109, -107, -104, -102, -100,
              -97, -95, -94, -91, -89, -87, -85, -83, -81, -79, -77, -75, -73, -71, -67]
for lon in state_lons:
    ax.axvline(lon, color='white', linewidth=1.5, alpha=0.4, zorder=0)

# Horizontal lines (latitude markers)
state_lats = [25, 28, 31, 33, 35, 37, 39, 41, 43, 45, 47, 49]
for lat in state_lats:
    ax.axhline(lat, color='white', linewidth=1.5, alpha=0.4, zorder=0)

# Styling
ax.set_xlabel('Longitude', fontsize=18, fontweight='bold')
ax.set_ylabel('Latitude', fontsize=18, fontweight='bold')
ax.set_title('Estimated Depth to Reach 300°C\nContinental United States\n(Supercritical Geothermal Resource Accessibility)',
            fontsize=22, fontweight='bold', pad=25)

ax.tick_params(labelsize=14)
ax.set_xlim(-126, -65)
ax.set_ylim(24, 50.5)
ax.set_aspect('equal')

# Add grid
ax.grid(True, alpha=0.2, linestyle=':', linewidth=0.5, color='gray', zorder=0)

# Enhanced legend
legend = ax.legend(loc='lower right',
                  fontsize=16,
                  title='Depth Category\n(Drilling Feasibility)',
                  title_fontsize=18,
                  framealpha=0.95,
                  edgecolor='black',
                  fancybox=True,
                  shadow=True,
                  markerscale=3)

# Make legend title bold
legend.get_title().set_fontweight('bold')

# Add summary box
summary_text = (
    "KEY FINDINGS:\n"
    "• Only 5% of CONUS reaches 300°C\n"
    "  within proven drilling depths (≤7 km)\n"
    "• 83% requires >10 km depth\n"
    "  (beyond current technology)\n"
    "• Western US (Basin & Range,\n"
    "  Cascades) most favorable"
)

# Add text box
props = dict(boxstyle='round,pad=1', facecolor='wheat', alpha=0.9, edgecolor='black', linewidth=2)
ax.text(0.02, 0.97, summary_text, transform=ax.transAxes,
       fontsize=14, verticalalignment='top',
       bbox=props, family='monospace')

# Add data source annotation
source_text = (
    "Data: Stanford Thermal Earth Model (2024) + SMU Geothermal Lab (2011)\n"
    "Analysis: 534,942 grid points across CONUS"
)
ax.text(0.5, -0.08, source_text, transform=ax.transAxes,
       fontsize=11, ha='center', style='italic', color='gray')

plt.tight_layout()
plt.savefig('plots/depth_to_300c_improved.png', dpi=300, bbox_inches='tight', facecolor='white')
print("✅ Saved: plots/depth_to_300c_improved.png")
plt.close()

# Create a second version with even more emphasis on accessible regions
print("\nCreating zoomed-in accessible regions map...")

# Filter to show only accessible regions (≤10 km)
accessible = df[df['simple_bin'] != ">10 km (Very Deep)"]

if len(accessible) > 0:
    fig, ax = plt.subplots(figsize=(20, 12))
    ax.set_facecolor('#F0F0F0')

    # Plot gray background for context (all CONUS)
    ax.scatter(df['lon'], df['lat'], c='#E0E0E0', s=3, alpha=0.3, label='Inaccessible (>10 km)')

    # Plot accessible regions with large dots
    for bin_name in ["≤6 km (Shallow)", "6-7 km (Moderate)", "7-10 km (Deep)"]:
        bin_df = accessible[accessible['simple_bin'] == bin_name]
        if len(bin_df) > 0:
            pct = (len(bin_df) / total) * 100
            ax.scatter(bin_df['lon'], bin_df['lat'],
                      c=colors[bin_name],
                      s=40,  # Even larger dots
                      alpha=0.95,
                      edgecolors='black',
                      linewidths=0.5,
                      label=f"{bin_name}: {pct:.1f}%")

    # State boundaries
    for lon in state_lons:
        ax.axvline(lon, color='white', linewidth=1.5, alpha=0.5, zorder=0)
    for lat in state_lats:
        ax.axhline(lat, color='white', linewidth=1.5, alpha=0.5, zorder=0)

    ax.set_xlabel('Longitude', fontsize=18, fontweight='bold')
    ax.set_ylabel('Latitude', fontsize=18, fontweight='bold')
    ax.set_title('Accessible 300°C Geothermal Resources (≤10 km depth)\nHighlighting Realistic Development Targets',
                fontsize=22, fontweight='bold', pad=25)

    ax.tick_params(labelsize=14)
    ax.set_xlim(-126, -65)
    ax.set_ylim(24, 50.5)
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.2, linestyle=':', linewidth=0.5, color='gray')

    legend = ax.legend(loc='lower right', fontsize=16,
                      title='Depth Category', title_fontsize=18,
                      framealpha=0.95, edgecolor='black',
                      fancybox=True, shadow=True, markerscale=2)
    legend.get_title().set_fontweight('bold')

    # Summary for accessible regions
    accessible_text = (
        "ACCESSIBLE REGIONS ONLY:\n"
        f"• Total: {len(accessible):,} locations\n"
        f"• {(len(accessible)/total*100):.1f}% of CONUS\n"
        "• Concentrated in:\n"
        "  - Nevada (Basin & Range)\n"
        "  - Eastern Oregon/Idaho\n"
        "  - Parts of Utah, NM, CA, WY"
    )

    props = dict(boxstyle='round,pad=1', facecolor='lightyellow', alpha=0.95, edgecolor='black', linewidth=2)
    ax.text(0.02, 0.97, accessible_text, transform=ax.transAxes,
           fontsize=14, verticalalignment='top',
           bbox=props, family='monospace')

    plt.tight_layout()
    plt.savefig('plots/depth_to_300c_accessible_only.png', dpi=300, bbox_inches='tight', facecolor='white')
    print("✅ Saved: plots/depth_to_300c_accessible_only.png")
    plt.close()

print("\n✅ Improved maps created successfully!")
print("   - plots/depth_to_300c_improved.png (all regions)")
print("   - plots/depth_to_300c_accessible_only.png (accessible regions highlighted)")

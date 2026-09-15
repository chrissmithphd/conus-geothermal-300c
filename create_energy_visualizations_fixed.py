#!/usr/bin/env python3
"""
Energy generation visualizations - EXACT bins matching original analysis.
"""
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

PLOT_DIR = Path("plots")

# EXACT color scheme from original maps - DO NOT CHANGE
COLORS = {
    "≤4 km": "#08306B",
    "4-5 km": "#2171B5",
    "5-6 km": "#00B050",
    "6-7 km": "#FFE100",
    "7-8 km": "#FF8C00",
    "8-10 km": "#E31A1C",
    ">10 km": "#D9D9D9"
}

# Data - INDIVIDUAL bins, not cumulative (updated Sep 15 2026)
BINS = ["≤4 km", "4-5 km", "5-6 km", "6-7 km", "7-8 km", "8-10 km", ">10 km"]
AREA_KM2 = [0, 46, 16285, 412296, 217321, 1546782, 6407277]
CAPACITY_GW = [0, 0.3, 114, 2886, 1521, 10827, 44851]

def create_capacity_by_bin_chart():
    """Bar chart showing capacity for each individual depth bin."""
    fig, ax = plt.subplots(figsize=(16, 9))

    x_pos = np.arange(len(BINS))
    colors = [COLORS[b] for b in BINS]

    bars = ax.bar(x_pos, CAPACITY_GW, color=colors, edgecolor='black',
                   linewidth=1.5, alpha=0.9)

    # Add values on bars
    for i, (bar, cap) in enumerate(zip(bars, CAPACITY_GW)):
        if cap > 500:
            ax.text(bar.get_x() + bar.get_width()/2., cap + 1000,
                    f'{cap:,.0f} GW', ha='center', va='bottom',
                    fontsize=11, fontweight='bold')
        elif cap > 10:
            ax.text(bar.get_x() + bar.get_width()/2., cap + 50,
                    f'{cap:.0f} GW', ha='center', va='bottom',
                    fontsize=10, fontweight='bold')

    # US total reference line
    us_total = 1287
    ax.axhline(y=us_total, color='red', linestyle='--', linewidth=2,
               label=f'US Total: {us_total:,} GW', zorder=5)

    ax.set_ylabel('Generation Capacity (GW)', fontsize=13, fontweight='bold')
    ax.set_xlabel('Depth to 300°C', fontsize=13, fontweight='bold')
    ax.set_title('Geothermal Energy Potential by Depth\nCONUS — 20% development, 35 MW/km² power density',
                 fontsize=15, fontweight='bold', pad=15)
    ax.set_xticks(x_pos)
    ax.set_xticklabels(BINS, fontsize=11)
    ax.tick_params(axis='y', labelsize=11)
    ax.set_ylim(0, max(CAPACITY_GW) * 1.1)
    ax.legend(fontsize=11, loc='upper left')
    ax.grid(axis='y', alpha=0.3, linestyle='--')

    fig.text(0.5, 0.02,
             'Based on superhot geothermal (300-400°C) power density. IDDP-2 demonstrated 45 MW per well at 427°C.',
             ha='center', fontsize=10, style='italic', color='#555')

    plt.tight_layout(rect=[0, 0.04, 1, 1])
    out = PLOT_DIR / "energy_by_depth_bin.png"
    plt.savefig(out, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"✅ {out}")

def create_area_and_capacity_chart():
    """Accessible resources only - detailed breakdown with cumulative metrics."""
    # Focus on accessible bins (≤10 km), exclude >10 km
    accessible_bins = ["4-5 km", "5-6 km", "6-7 km", "7-8 km", "8-10 km"]
    accessible_idx = [BINS.index(b) for b in accessible_bins]
    accessible_areas = [AREA_KM2[i] for i in accessible_idx]
    accessible_capacity = [CAPACITY_GW[i] for i in accessible_idx]
    accessible_colors = [COLORS[b] for b in accessible_bins]

    # Calculate cumulatives
    cumulative_area = np.cumsum(accessible_areas)
    cumulative_capacity = np.cumsum(accessible_capacity)

    # Create figure with 2x2 grid
    fig = plt.figure(figsize=(16, 10))
    gs = fig.add_gridspec(2, 2, hspace=0.35, wspace=0.3)

    # Top left: Area by bin with values
    ax1 = fig.add_subplot(gs[0, 0])
    bars1 = ax1.bar(range(len(accessible_bins)), accessible_areas,
                    color=accessible_colors, edgecolor='black', linewidth=1.5, alpha=0.9)
    ax1.set_ylabel('Area (km²)', fontsize=12, fontweight='bold')
    ax1.set_title('Accessible Area by Drilling Depth', fontsize=13, fontweight='bold', pad=10)
    ax1.set_xticks(range(len(accessible_bins)))
    ax1.set_xticklabels(accessible_bins, fontsize=10)
    ax1.grid(axis='y', alpha=0.3)
    # Add values on bars
    for bar, area in zip(bars1, accessible_areas):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{area:,.0f}', ha='center', va='bottom', fontsize=9, fontweight='bold')

    # Top right: Capacity by bin with values and US total reference
    ax2 = fig.add_subplot(gs[0, 1])
    bars2 = ax2.bar(range(len(accessible_bins)), accessible_capacity,
                    color=accessible_colors, edgecolor='black', linewidth=1.5, alpha=0.9)
    ax2.set_ylabel('Generation Capacity (GW)', fontsize=12, fontweight='bold')
    ax2.set_title('Accessible Energy Potential by Drilling Depth', fontsize=13, fontweight='bold', pad=10)
    ax2.set_xticks(range(len(accessible_bins)))
    ax2.set_xticklabels(accessible_bins, fontsize=10)
    ax2.grid(axis='y', alpha=0.3)
    # Add US total reference line
    us_total = 1287
    ax2.axhline(y=us_total, color='red', linestyle='--', linewidth=2,
                label=f'US Total: {us_total:,} GW', alpha=0.7)
    ax2.legend(fontsize=10, loc='upper left')
    # Add values on bars
    for bar, cap in zip(bars2, accessible_capacity):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{cap:,.0f}', ha='center', va='bottom', fontsize=9, fontweight='bold')

    # Bottom left: Cumulative area
    ax3 = fig.add_subplot(gs[1, 0])
    ax3.fill_between(range(len(accessible_bins)), cumulative_area,
                     color='#2171B5', alpha=0.3, edgecolor='#08306B', linewidth=2)
    ax3.plot(range(len(accessible_bins)), cumulative_area, 'o-',
            color='#08306B', linewidth=2, markersize=8)
    ax3.set_ylabel('Cumulative Area (km²)', fontsize=12, fontweight='bold')
    ax3.set_xlabel('Maximum Drilling Depth', fontsize=12, fontweight='bold')
    ax3.set_title('Cumulative Accessible Area', fontsize=13, fontweight='bold', pad=10)
    ax3.set_xticks(range(len(accessible_bins)))
    ax3.set_xticklabels(['≤5 km', '≤6 km', '≤7 km', '≤8 km', '≤10 km'], fontsize=10)
    ax3.grid(axis='y', alpha=0.3)
    # Add values at points
    for i, (x, y) in enumerate(zip(range(len(accessible_bins)), cumulative_area)):
        ax3.text(x, y, f'{y:,.0f}', ha='center', va='bottom',
                fontsize=9, fontweight='bold')

    # Bottom right: Cumulative capacity vs drilling depth
    ax4 = fig.add_subplot(gs[1, 1])
    ax4.fill_between(range(len(accessible_bins)), cumulative_capacity,
                     color='#E31A1C', alpha=0.3, edgecolor='#A00000', linewidth=2)
    ax4.plot(range(len(accessible_bins)), cumulative_capacity, 'o-',
            color='#A00000', linewidth=2, markersize=8)
    ax4.set_ylabel('Cumulative Capacity (GW)', fontsize=12, fontweight='bold')
    ax4.set_xlabel('Maximum Drilling Depth', fontsize=12, fontweight='bold')
    ax4.set_title('Cumulative Energy Potential', fontsize=13, fontweight='bold', pad=10)
    ax4.set_xticks(range(len(accessible_bins)))
    ax4.set_xticklabels(['≤5 km', '≤6 km', '≤7 km', '≤8 km', '≤10 km'], fontsize=10)
    ax4.grid(axis='y', alpha=0.3)
    # Add US total reference
    ax4.axhline(y=us_total, color='red', linestyle='--', linewidth=2,
                label=f'US Total: {us_total:,} GW', alpha=0.7)
    ax4.legend(fontsize=10, loc='upper left')
    # Add values at points
    for i, (x, y) in enumerate(zip(range(len(accessible_bins)), cumulative_capacity)):
        ax4.text(x, y, f'{y:,.0f}', ha='center', va='bottom',
                fontsize=9, fontweight='bold')

    fig.suptitle('Accessible Geothermal Resources (<10 km drilling depth)\nConterminous United States',
                 fontsize=15, fontweight='bold', y=0.98)

    fig.text(0.5, 0.01,
             'Assumes 20% area development, 35 MW/km² power density (300-400°C superhot). Excludes >10 km (74.5% of CONUS, not accessible).',
             ha='center', fontsize=9, style='italic', color='#555')

    out = PLOT_DIR / "area_and_capacity_by_bin.png"
    plt.savefig(out, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"✅ {out}")

def main():
    print("Creating energy visualizations with exact bins...")
    create_capacity_by_bin_chart()
    create_area_and_capacity_chart()
    print("Done")

if __name__ == "__main__":
    main()

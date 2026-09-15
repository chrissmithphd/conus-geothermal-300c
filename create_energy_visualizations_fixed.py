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
    """Combined area and capacity visualization with ALL 7 bins - dual axis for information density."""
    fig, ax1 = plt.subplots(figsize=(16, 9))

    x_pos = np.arange(len(BINS))
    colors = [COLORS[b] for b in BINS]

    # Primary axis: Area bars
    bars = ax1.bar(x_pos, AREA_KM2, color=colors, edgecolor='black',
                   linewidth=1.5, alpha=0.7, label='Area (km²)')
    ax1.set_ylabel('Area (km²)', fontsize=13, fontweight='bold', color='black')
    ax1.set_xlabel('Depth to 300°C', fontsize=13, fontweight='bold')
    ax1.set_xticks(x_pos)
    ax1.set_xticklabels(BINS, fontsize=11, fontweight='bold')
    ax1.tick_params(axis='y', labelcolor='black', labelsize=11)
    ax1.grid(axis='y', alpha=0.3, linestyle='--')

    # Add area values on bars (showing in millions for >1M)
    for i, (bar, area) in enumerate(zip(bars, AREA_KM2)):
        height = bar.get_height()
        if area > 1_000_000:
            label = f'{area/1_000_000:.1f}M'
        elif area > 1_000:
            label = f'{area/1_000:.0f}K'
        elif area > 0:
            label = f'{area:.0f}'
        else:
            continue
        ax1.text(bar.get_x() + bar.get_width()/2., height * 0.5,
                label, ha='center', va='center', fontsize=10,
                fontweight='bold', color='white')

    # Secondary axis: Capacity line
    ax2 = ax1.twinx()
    line = ax2.plot(x_pos, CAPACITY_GW, 'o-', color='#E31A1C',
                   linewidth=3, markersize=10, label='Capacity (GW)',
                   markeredgecolor='white', markeredgewidth=2)
    ax2.set_ylabel('Generation Capacity (GW)', fontsize=13, fontweight='bold', color='#E31A1C')
    ax2.tick_params(axis='y', labelcolor='#E31A1C', labelsize=11)

    # Add capacity values above points
    for i, (x, cap) in enumerate(zip(x_pos, CAPACITY_GW)):
        if cap > 1000:
            label = f'{cap/1000:.1f}K'
        elif cap > 0:
            label = f'{cap:.0f}'
        else:
            continue
        ax2.text(x, cap, label, ha='center', va='bottom',
                fontsize=10, fontweight='bold', color='#E31A1C')

    # Add US total reference line on capacity axis
    us_total = 1287
    ax2.axhline(y=us_total, color='red', linestyle=':', linewidth=2,
               label=f'US Total: {us_total:,} GW', alpha=0.7)

    # Combined legend
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2,
              loc='upper left', fontsize=11, framealpha=0.95)

    ax1.set_title('Area and Energy Potential by Depth\nConterminous United States',
                 fontsize=15, fontweight='bold', pad=15)

    fig.text(0.5, 0.02,
             'Bars: CONUS area at each depth. Line: Generation capacity (20% development, 35 MW/km²). K=thousand, M=million.',
             ha='center', fontsize=10, style='italic', color='#555')

    plt.tight_layout(rect=[0, 0.03, 1, 1])
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

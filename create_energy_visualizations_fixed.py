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
    """Side-by-side: area vs capacity for each bin."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 8))

    x_pos = np.arange(len(BINS))
    colors = [COLORS[b] for b in BINS]

    # Left: Area
    ax1.bar(x_pos, AREA_KM2, color=colors, edgecolor='black', linewidth=1.5, alpha=0.9)
    ax1.set_ylabel('Area (km²)', fontsize=12, fontweight='bold')
    ax1.set_xlabel('Depth Bin', fontsize=12, fontweight='bold')
    ax1.set_title('CONUS Area by Depth', fontsize=14, fontweight='bold', pad=10)
    ax1.set_xticks(x_pos)
    ax1.set_xticklabels(BINS, fontsize=10, rotation=0)
    ax1.tick_params(axis='y', labelsize=10)
    ax1.grid(axis='y', alpha=0.3)

    # Right: Capacity
    ax2.bar(x_pos, CAPACITY_GW, color=colors, edgecolor='black', linewidth=1.5, alpha=0.9)
    ax2.set_ylabel('Capacity (GW)', fontsize=12, fontweight='bold')
    ax2.set_xlabel('Depth Bin', fontsize=12, fontweight='bold')
    ax2.set_title('Energy Potential by Depth', fontsize=14, fontweight='bold', pad=10)
    ax2.set_xticks(x_pos)
    ax2.set_xticklabels(BINS, fontsize=10, rotation=0)
    ax2.tick_params(axis='y', labelsize=10)
    ax2.grid(axis='y', alpha=0.3)

    fig.suptitle('Area and Energy Potential Distribution\nConterminous United States',
                 fontsize=15, fontweight='bold', y=0.98)

    fig.text(0.5, 0.02,
             'Left: Total CONUS area at each depth. Right: Potential capacity (20% development, 35 MW/km²).',
             ha='center', fontsize=10, style='italic', color='#555')

    plt.tight_layout(rect=[0, 0.04, 1, 0.95])
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

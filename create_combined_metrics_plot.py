#!/usr/bin/env python3
"""
Single plot with all data labeled - area bars with capacity/% text overlays.
"""
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

PLOT_DIR = Path("plots")

# EXACT color scheme
COLORS = {
    "≤4 km": "#08306B",
    "4-5 km": "#2171B5",
    "5-6 km": "#00B050",
    "6-7 km": "#FFE100",
    "7-8 km": "#FF8C00",
    "8-10 km": "#E31A1C",
    ">10 km": "#D9D9D9"
}

BINS = ["≤4 km", "4-5 km", "5-6 km", "6-7 km", "7-8 km", "8-10 km", ">10 km"]
AREA_KM2 = [0, 46, 16285, 412296, 217321, 1546782, 6407277]
CAPACITY_GW = [0, 0.3, 114, 2886, 1521, 10827, 44851]

def create_combined_metrics():
    """Single bar chart with all metrics as text annotations."""
    fig, ax = plt.subplots(figsize=(18, 10))

    x_pos = np.arange(len(BINS))
    colors = [COLORS[b] for b in BINS]

    # Main bars: Area
    bars = ax.bar(x_pos, AREA_KM2, color=colors, edgecolor='black',
                  linewidth=2, alpha=0.9, width=0.7)

    # Calculate percentages
    total_area = sum(AREA_KM2)
    pct_by_bin = [(a / total_area * 100) for a in AREA_KM2]

    # Add text annotations on each bar
    for i, (bar, area, cap, pct, bin_name) in enumerate(zip(bars, AREA_KM2, CAPACITY_GW, pct_by_bin, BINS)):
        height = bar.get_height()
        x_center = bar.get_x() + bar.get_width() / 2

        if area == 0:
            continue

        # Format numbers
        if area >= 1_000_000:
            area_str = f'{area/1_000_000:.2f}M km²'
        elif area >= 1_000:
            area_str = f'{area/1_000:.0f}K km²'
        else:
            area_str = f'{area:.0f} km²'

        if cap >= 1000:
            cap_str = f'{cap/1000:.1f}K GW'
        elif cap >= 1:
            cap_str = f'{cap:.0f} GW'
        else:
            cap_str = f'{cap:.1f} GW'

        pct_str = f'{pct:.1f}%' if pct >= 0.1 else '<0.1%'

        # Position text based on bar height
        if height > total_area * 0.3:  # Tall bars - text inside
            y_pos = height * 0.5
            text_color = 'white' if bin_name != ">10 km" else 'black'
            fontsize = 11
        else:  # Short bars - text above
            y_pos = height
            text_color = 'black'
            fontsize = 10

        # Multi-line annotation
        annotation = f'{area_str}\n{cap_str}\n({pct_str} CONUS)'

        if height > total_area * 0.3:
            ax.text(x_center, y_pos, annotation,
                   ha='center', va='center', fontsize=fontsize,
                   fontweight='bold', color=text_color,
                   linespacing=1.5)
        else:
            ax.text(x_center, height * 1.02, annotation,
                   ha='center', va='bottom', fontsize=fontsize,
                   fontweight='bold', color=text_color,
                   linespacing=1.4,
                   bbox=dict(boxstyle='round,pad=0.5', facecolor='white',
                            edgecolor=colors[i], linewidth=2, alpha=0.9))

    ax.set_ylabel('Area (km²)', fontsize=14, fontweight='bold')
    ax.set_xlabel('Depth to 300°C', fontsize=14, fontweight='bold')
    ax.set_title('Geothermal Resource Metrics by Depth — All 7 Bins\nConterminous United States (Single Plot with Annotated Metrics)',
                fontsize=16, fontweight='bold', pad=20)
    ax.set_xticks(x_pos)
    ax.set_xticklabels(BINS, fontsize=13, fontweight='bold')
    ax.tick_params(axis='y', labelsize=12)
    ax.grid(axis='y', alpha=0.3, linestyle='--', linewidth=1)

    # Add US total capacity reference line (on hidden second axis)
    ax2 = ax.twinx()
    us_total = 1287
    ax2.set_ylim(ax.get_ylim())  # Match primary axis range
    ax2.set_ylabel('', fontsize=1)  # Hide label
    ax2.set_yticks([])  # Hide ticks

    # Add legend explaining the metrics
    legend_text = (
        'Each bar shows:\n'
        '  • Area at that depth (km²)\n'
        '  • Generation capacity (GW)\n'
        '  • Percentage of CONUS\n\n'
        f'Capacity: 20% development, 35 MW/km²\n'
        f'US Total Capacity: {us_total:,} GW'
    )
    ax.text(0.02, 0.98, legend_text,
           transform=ax.transAxes, fontsize=11,
           verticalalignment='top',
           bbox=dict(boxstyle='round,pad=0.8', facecolor='white',
                    edgecolor='black', linewidth=2, alpha=0.95),
           family='monospace')

    plt.tight_layout()
    out = PLOT_DIR / "geothermal_metrics_by_depth.png"
    plt.savefig(out, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"✅ {out}")

if __name__ == "__main__":
    create_combined_metrics()

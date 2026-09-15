#!/usr/bin/env python3
"""
Create energy generation potential visualizations.

Graphs showing:
1. Cumulative capacity by drilling depth
2. Capacity by depth bin with breakdown
"""
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

PLOT_DIR = Path("plots")
PLOT_DIR.mkdir(exist_ok=True)

# Match the original color scheme
COLORS = {
    "≤4 km": "#08306B",
    "4-5 km": "#2171B5",
    "5-6 km": "#00B050",
    "6-7 km": "#FFE100",
    "7-8 km": "#FF8C00",
    "8-10 km": "#E31A1C",
    ">10 km": "#DDDDDD"
}

# Data from energy analysis
CAPACITY_BY_DEPTH = {
    "4-5 km": 0.3,      # GW
    "5-6 km": 114,
    "6-7 km": 2886,
    "7-8 km": 224,
    "8-10 km": 7118,
    ">10 km": 49858     # Beyond current frontier but not impossible!
}

AREA_BY_DEPTH = {
    "4-5 km": 46,
    "5-6 km": 16285,
    "6-7 km": 412296,
    "7-8 km": 32000,
    "8-10 km": 1016841,
    ">10 km": 7122540
}

def create_cumulative_capacity_chart():
    """Bar chart showing cumulative capacity by drilling depth capability."""
    fig, ax = plt.subplots(figsize=(14, 8))

    # Drilling scenarios
    scenarios = [
        ("≤7 km\n(Proven)", ["4-5 km", "5-6 km", "6-7 km"], 3000),
        ("≤8 km\n(Advanced)", ["4-5 km", "5-6 km", "6-7 km", "7-8 km"], 3224),
        ("≤10 km\n(Frontier)", ["4-5 km", "5-6 km", "6-7 km", "7-8 km", "8-10 km"], 10342),
        ("≤20 km\n(Next-Gen)", ["4-5 km", "5-6 km", "6-7 km", "7-8 km", "8-10 km", ">10 km"], 60200)
    ]

    x_pos = np.arange(len(scenarios))
    capacities = [s[2] for s in scenarios]
    labels = [s[0] for s in scenarios]

    # Create bars
    bars = ax.bar(x_pos, capacities, color=['#2171B5', '#00B050', '#FF8C00', '#8B0000'],
                   edgecolor='black', linewidth=1.5, alpha=0.85)

    # Add US total capacity reference line
    us_total = 1287
    ax.axhline(y=us_total, color='red', linestyle='--', linewidth=2,
               label='US Total Capacity (1,287 GW)', zorder=5)

    # Add capacity values on bars
    for i, (bar, cap) in enumerate(zip(bars, capacities)):
        height = bar.get_height()
        multiplier = cap / us_total
        ax.text(bar.get_x() + bar.get_width()/2., height + 500,
                f'{cap:,.0f} GW\n({multiplier:.1f}× US total)',
                ha='center', va='bottom', fontsize=12, fontweight='bold')

    ax.set_ylabel('Generation Capacity (GW)', fontsize=14, fontweight='bold')
    ax.set_xlabel('Drilling Depth Capability', fontsize=14, fontweight='bold')
    ax.set_title('Geothermal Energy Potential by Drilling Depth\n'
                 'Conterminous United States — Typical Development Scenario (20% of area)',
                 fontsize=16, fontweight='bold', pad=15)
    ax.set_xticks(x_pos)
    ax.set_xticklabels(labels, fontsize=12)
    ax.tick_params(axis='y', labelsize=11)
    ax.set_ylim(0, 65000)
    ax.legend(fontsize=11, loc='upper left')
    ax.grid(axis='y', alpha=0.3, linestyle='--')

    # Add note
    fig.text(0.5, 0.02,
             'Based on superhot geothermal power density (30-40 MW/km²). Each 3 km increase in drilling '
             'depth unlocks thousands of GW. Ultra-deep drilling (>10 km) could access 50,000+ GW.',
             ha='center', fontsize=10, style='italic', color='#555', wrap=True)

    plt.tight_layout(rect=[0, 0.05, 1, 1])
    out = PLOT_DIR / "energy_potential_by_drilling_depth.png"
    plt.savefig(out, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"✅ Saved: {out}")


def create_stacked_capacity_chart():
    """Stacked bar showing capacity contribution by depth bin."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 8))

    # Left: Accessible with frontier drilling (≤10 km)
    bins_accessible = ["4-5 km", "5-6 km", "6-7 km", "7-8 km", "8-10 km"]
    caps_accessible = [CAPACITY_BY_DEPTH[b] for b in bins_accessible]
    colors_accessible = [COLORS[b] for b in bins_accessible]

    # Right: All depths including ultra-deep
    bins_all = bins_accessible + [">10 km"]
    caps_all = [CAPACITY_BY_DEPTH[b] for b in bins_all]
    colors_all = [COLORS[b] for b in bins_all]

    # Create pie charts
    wedges1, texts1, autotexts1 = ax1.pie(caps_accessible, labels=bins_accessible,
                                           colors=colors_accessible,
                                           autopct=lambda pct: f'{pct:.1f}%' if pct > 2 else '',
                                           startangle=90, textprops={'fontsize': 11})

    # Make wedges have black borders
    for w in wedges1:
        w.set_edgecolor('black')
        w.set_linewidth(1.5)

    ax1.set_title('Frontier Drilling (≤10 km)\n10,342 GW Total',
                  fontsize=14, fontweight='bold', pad=10)

    wedges2, texts2, autotexts2 = ax2.pie(caps_all, labels=bins_all,
                                           colors=colors_all,
                                           autopct=lambda pct: f'{pct:.1f}%' if pct > 1 else '',
                                           startangle=90, textprops={'fontsize': 11})

    for w in wedges2:
        w.set_edgecolor('black')
        w.set_linewidth(1.5)

    ax2.set_title('Next-Generation Drilling (≤20 km)\n60,200 GW Total',
                  fontsize=14, fontweight='bold', pad=10)

    fig.suptitle('Geothermal Capacity Distribution by Depth\n'
                 'Conterminous United States',
                 fontsize=16, fontweight='bold', y=0.98)

    fig.text(0.5, 0.02,
             'Ultra-deep drilling (>10 km) accesses 50,000+ GW of additional capacity. '
             'Each depth increment unlocks superhot to supercritical resources (300-450°C).',
             ha='center', fontsize=10, style='italic', color='#555')

    plt.tight_layout(rect=[0, 0.05, 1, 0.95])
    out = PLOT_DIR / "energy_capacity_distribution.png"
    plt.savefig(out, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"✅ Saved: {out}")


def main():
    print("Creating energy generation visualizations...")
    create_cumulative_capacity_chart()
    create_stacked_capacity_chart()
    print("\n✅ All visualizations complete!")

if __name__ == "__main__":
    main()

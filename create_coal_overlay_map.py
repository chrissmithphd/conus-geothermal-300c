#!/usr/bin/env python3
"""
Coal Power Plant Overlay Map

Creates a geothermal depth map with coal plants overlaid, showing:
- Plant locations sized by capacity
- Colors indicating depth category at that location
- Operating vs retired plant status
"""
import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
from scipy.spatial import cKDTree
from pathlib import Path

PLOT_DIR = Path("plots")
PLOT_DIR.mkdir(exist_ok=True)

# Depth bins and colors (EXACTLY matching original geothermal maps)
COLORS = ["#08306B", "#2171B5", "#00B050", "#FFE100", "#FF8C00", "#E31A1C", "#DDDDDD"]
BOUNDARIES = [3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 10.0, 15.0]
CMAP = ListedColormap(COLORS)
CMAP.set_bad((1, 1, 1, 0))
NORM = BoundaryNorm(BOUNDARIES, CMAP.N)

VIEW = dict(x0=-125.4, x1=-66.6, y0=24.2, y1=49.5)
ASPECT = 1.32

BIN_DEPTH = {"≤4 km": 3.5, "4-5 km": 4.5, "5-6 km": 5.5, "6-7 km": 6.5,
             "7-8 km": 7.5, "8-10 km": 9.0, ">10 km": 12.0}

# ============================================================================
# Load Data
# ============================================================================

def load_data():
    """Load geothermal grid, coal plants, and state boundaries."""
    # Geothermal
    geo = pd.read_csv("data/processed/conus_depth_to_300c.csv")
    geo["bin_key"] = geo["depth_bin"].replace({"≤4 km": "<=4 km"})
    geo["depth_num"] = geo["bin_key"].map(BIN_DEPTH)

    # Coal plants (with matched geothermal data)
    coal = pd.read_csv("data/processed/coal_plants_with_geothermal.csv")

    # State boundaries
    states = gpd.read_file("data/raw/boundaries/cb_2023_us_state_20m.shp")
    states = states[~states["STUSPS"].isin({"AK", "HI", "PR", "VI", "GU", "MP", "AS"})]
    states = states.to_crs("EPSG:4326")

    return geo, coal, states

# ============================================================================
# Rasterize Geothermal Background
# ============================================================================

def rasterize_geothermal(df, nx=2000, ny=1000, max_km=6.0):
    """Create nearest-neighbor raster of geothermal depth."""
    xs = np.linspace(VIEW["x0"], VIEW["x1"], nx)
    ys = np.linspace(VIEW["y0"], VIEW["y1"], ny)
    gx, gy = np.meshgrid(xs, ys)

    latref = np.cos(np.radians(df["lat"].mean()))
    tree = cKDTree(np.column_stack([df["lon"].values * latref, df["lat"].values]))
    dist, idx = tree.query(np.column_stack([gx.ravel() * latref, gy.ravel()]), k=1)

    vals = df["depth_num"].values[idx].astype(float)
    vals[dist * 111.0 > max_km] = np.nan
    return vals.reshape(ny, nx), [VIEW["x0"], VIEW["x1"], VIEW["y0"], VIEW["y1"]]

# ============================================================================
# Create Overlay Map
# ============================================================================

def create_coal_overlay_map(geo, coal, states):
    """Main overlay map: geothermal background + coal plants."""
    raster, extent = rasterize_geothermal(geo)

    fig, ax = plt.subplots(figsize=(24, 14))
    fig.subplots_adjust(bottom=0.12, right=0.85)

    # Background: geothermal depth field
    ax.imshow(np.ma.masked_invalid(raster), origin="lower", extent=extent,
              cmap=CMAP, norm=NORM, interpolation="nearest", aspect="auto",
              zorder=10, alpha=0.85)

    # State boundaries
    states.boundary.plot(ax=ax, linewidth=0.6, edgecolor="#2A2A2A", zorder=400, alpha=0.7)

    # Frame
    ax.set_xlim(VIEW["x0"], VIEW["x1"])
    ax.set_ylim(VIEW["y0"], VIEW["y1"])
    ax.set_aspect(ASPECT)
    ax.set_xlabel("Longitude", fontsize=14, fontweight="bold")
    ax.set_ylabel("Latitude", fontsize=14, fontweight="bold")
    ax.set_title("Coal Power Plants & Geothermal Resource Depth\n"
                 "Conterminous United States — coal plants sized by capacity, colored by geothermal depth",
                 fontsize=20, fontweight="bold", pad=14)
    ax.tick_params(labelsize=11.5)
    ax.set_facecolor("white")

    # Plot coal plants
    # Size by capacity (MW → points^2 mapping)
    def capacity_to_size(cap_mw):
        """Map capacity to marker size."""
        if cap_mw < 100:
            return 25
        elif cap_mw < 500:
            return 50
        elif cap_mw < 1000:
            return 100
        elif cap_mw < 2000:
            return 200
        else:
            return 350

    # Color by depth category (EXACTLY matching original maps)
    depth_color_map = {
        "≤4 km": "#08306B", "4-5 km": "#2171B5", "5-6 km": "#00B050",
        "6-7 km": "#FFE100", "7-8 km": "#FF8C00", "8-10 km": "#E31A1C",
        ">10 km": "#DDDDDD"
    }

    # Separate operating vs retired
    operating = coal[coal["status"] == "Operating"]
    retired = coal[coal["status"] == "Retired"]

    # Plot retired first (so operating are on top)
    for _, plant in retired.iterrows():
        size = capacity_to_size(plant["capacity_mw"])
        color = depth_color_map.get(plant["depth_bin"], "#888888")
        ax.scatter(plant["lon"], plant["lat"], s=size, c=color,
                   marker="o", edgecolors="black", linewidths=1.5,
                   alpha=0.7, zorder=500)

    # Plot operating
    for _, plant in operating.iterrows():
        size = capacity_to_size(plant["capacity_mw"])
        color = depth_color_map.get(plant["depth_bin"], "#888888")
        ax.scatter(plant["lon"], plant["lat"], s=size, c=color,
                   marker="^", edgecolors="black", linewidths=2.0,
                   alpha=0.95, zorder=510)

    # Legends
    # 1. Depth categories (color)
    depth_handles = [
        Patch(facecolor=depth_color_map["6-7 km"], edgecolor="black", linewidth=0.7,
              label="6-7 km (proven drilling)"),
        Patch(facecolor=depth_color_map["7-8 km"], edgecolor="black", linewidth=0.7,
              label="7-8 km (advanced drilling)"),
        Patch(facecolor=depth_color_map["8-10 km"], edgecolor="black", linewidth=0.7,
              label="8-10 km (frontier drilling)"),
        Patch(facecolor=depth_color_map[">10 km"], edgecolor="black", linewidth=0.7,
              label=">10 km (ultra-deep drilling)"),
    ]

    # 2. Plant status (marker shape)
    status_handles = [
        Line2D([0], [0], marker="^", color="none", markerfacecolor="gray",
               markeredgecolor="black", markersize=12, linewidth=0,
               label="Operating plant", markeredgewidth=1.5),
        Line2D([0], [0], marker="o", color="none", markerfacecolor="gray",
               markeredgecolor="black", markersize=10, linewidth=0,
               label="Retired plant (2015+)", markeredgewidth=1.5),
    ]

    # 3. Plant capacity (size)
    capacity_handles = [
        Line2D([0], [0], marker="o", color="none", markerfacecolor="gray",
               markeredgecolor="black", markersize=18, linewidth=0,
               label=">2000 MW", markeredgewidth=1),
        Line2D([0], [0], marker="o", color="none", markerfacecolor="gray",
               markeredgecolor="black", markersize=14, linewidth=0,
               label="1000-2000 MW", markeredgewidth=1),
        Line2D([0], [0], marker="o", color="none", markerfacecolor="gray",
               markeredgecolor="black", markersize=10, linewidth=0,
               label="500-1000 MW", markeredgewidth=1),
        Line2D([0], [0], marker="o", color="none", markerfacecolor="gray",
               markeredgecolor="black", markersize=7, linewidth=0,
               label="100-500 MW", markeredgewidth=1),
        Line2D([0], [0], marker="o", color="none", markerfacecolor="gray",
               markeredgecolor="black", markersize=5, linewidth=0,
               label="<100 MW", markeredgewidth=1),
    ]

    # Position legends
    leg1 = ax.legend(handles=depth_handles, loc="upper left",
                     bbox_to_anchor=(1.02, 1.0),
                     title="Geothermal Depth at Plant Site",
                     fontsize=11, title_fontsize=12, frameon=True,
                     framealpha=0.95, edgecolor="black")
    leg1.get_title().set_fontweight("bold")

    leg2 = ax.legend(handles=status_handles, loc="upper left",
                     bbox_to_anchor=(1.02, 0.73),
                     title="Plant Status",
                     fontsize=11, title_fontsize=12, frameon=True,
                     framealpha=0.95, edgecolor="black")
    leg2.get_title().set_fontweight("bold")
    ax.add_artist(leg1)  # Keep first legend

    leg3 = ax.legend(handles=capacity_handles, loc="upper left",
                     bbox_to_anchor=(1.02, 0.53),
                     title="Plant Capacity",
                     fontsize=11, title_fontsize=12, frameon=True,
                     framealpha=0.95, edgecolor="black")
    leg3.get_title().set_fontweight("bold")
    ax.add_artist(leg2)  # Keep second legend

    # Caption
    fig.text(0.5, 0.02,
             "23 of 340 coal plants (7%) sit on proven-to-frontier drilling depths (≤10 km). "
             "22 of those are in the western US. Best candidates: Centralia WA (1,460 MW, 6.2 km), "
             "Huntington UT (1,016 MW, 6.7 km), Boardman OR (642 MW retired, 7.0 km). "
             "317 plants require ultra-deep drilling (>10 km). Data: Stanford Thermal Earth Model (2024) + EIA Form 860 (2025)",
             ha="center", fontsize=10.5, style="italic", color="#555", wrap=True)

    # Save
    outfile = PLOT_DIR / "coal_plants_geothermal_overlay.png"
    plt.savefig(outfile, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"✅ Saved: {outfile}")

# ============================================================================
# Western States Zoom Map
# ============================================================================

def create_western_zoom_map(geo, coal, states):
    """Zoomed map of western states where accessible resources exist."""
    # Western extent
    west_view = dict(x0=-125, x1=-102, y0=31, y1=49)

    # Filter coal plants to western states
    western_states = ["WY", "NM", "UT", "NV", "AZ", "CO", "ID", "MT", "CA", "OR", "WA"]
    coal_west = coal[coal["state"].isin(western_states)]

    fig, ax = plt.subplots(figsize=(18, 14))
    fig.subplots_adjust(bottom=0.10, right=0.82)

    # Rasterize for western view
    xs = np.linspace(west_view["x0"], west_view["x1"], 1500)
    ys = np.linspace(west_view["y0"], west_view["y1"], 1200)
    gx, gy = np.meshgrid(xs, ys)

    latref = np.cos(np.radians(geo["lat"].mean()))
    tree = cKDTree(np.column_stack([geo["lon"].values * latref, geo["lat"].values]))
    dist, idx = tree.query(np.column_stack([gx.ravel() * latref, gy.ravel()]), k=1)

    vals = geo["depth_num"].values[idx].astype(float)
    vals[dist * 111.0 > 6.0] = np.nan
    raster = vals.reshape(len(ys), len(xs))
    extent = [west_view["x0"], west_view["x1"], west_view["y0"], west_view["y1"]]

    # Background
    ax.imshow(np.ma.masked_invalid(raster), origin="lower", extent=extent,
              cmap=CMAP, norm=NORM, interpolation="nearest", aspect="auto",
              zorder=10, alpha=0.85)

    # States
    states.boundary.plot(ax=ax, linewidth=0.8, edgecolor="#2A2A2A", zorder=400, alpha=0.8)

    # Frame
    ax.set_xlim(west_view["x0"], west_view["x1"])
    ax.set_ylim(west_view["y0"], west_view["y1"])
    ax.set_aspect(1.10)
    ax.set_xlabel("Longitude", fontsize=13, fontweight="bold")
    ax.set_ylabel("Latitude", fontsize=13, fontweight="bold")
    ax.set_title("Western US Coal Plants & Geothermal Resources\n"
                 "All accessible sites (≤10 km depth) are in the West",
                 fontsize=18, fontweight="bold", pad=12)
    ax.tick_params(labelsize=11)
    ax.set_facecolor("white")

    # Plot plants with labels for top candidates (matching original colors)
    depth_color_map = {
        "≤4 km": "#08306B", "4-5 km": "#2171B5", "5-6 km": "#00B050",
        "6-7 km": "#FFE100", "7-8 km": "#FF8C00", "8-10 km": "#E31A1C",
        ">10 km": "#DDDDDD"
    }

    def capacity_to_size(cap_mw):
        if cap_mw < 100: return 40
        elif cap_mw < 500: return 80
        elif cap_mw < 1000: return 140
        elif cap_mw < 2000: return 240
        else: return 400

    # Plot all western plants
    for _, plant in coal_west.iterrows():
        size = capacity_to_size(plant["capacity_mw"])
        color = depth_color_map.get(plant["depth_bin"], "#DDDDDD")
        marker = "^" if plant["status"] == "Operating" else "o"
        alpha = 0.95 if plant["status"] == "Operating" else 0.7

        ax.scatter(plant["lon"], plant["lat"], s=size, c=color,
                   marker=marker, edgecolors="black", linewidths=2.0,
                   alpha=alpha, zorder=500)

    # Label top 10 accessible plants
    top_accessible = coal_west[coal_west["depth_bin"] != ">10 km"].nlargest(10, "capacity_mw")
    for _, plant in top_accessible.iterrows():
        ax.annotate(plant["plant_name"].split()[0],  # First word of name
                    xy=(plant["lon"], plant["lat"]),
                    xytext=(5, 5), textcoords="offset points",
                    fontsize=9, fontweight="bold",
                    bbox=dict(boxstyle="round,pad=0.3", facecolor="white",
                              edgecolor="black", alpha=0.8),
                    zorder=600)

    # Simple legend
    handles = [
        Line2D([0], [0], marker="^", color="none", markerfacecolor="#FFE100",
               markeredgecolor="black", markersize=12, linewidth=0,
               label="Operating (6-7 km)", markeredgewidth=1.5),
        Line2D([0], [0], marker="o", color="none", markerfacecolor="#FFE100",
               markeredgecolor="black", markersize=10, linewidth=0,
               label="Retired (6-7 km)", markeredgewidth=1.5),
        Line2D([0], [0], marker="^", color="none", markerfacecolor="#E31A1C",
               markeredgecolor="black", markersize=12, linewidth=0,
               label="Operating (8-10 km)", markeredgewidth=1.5),
        Line2D([0], [0], marker="o", color="none", markerfacecolor="#E31A1C",
               markeredgecolor="black", markersize=10, linewidth=0,
               label="Retired (8-10 km)", markeredgewidth=1.5),
        Line2D([0], [0], marker="o", color="none", markerfacecolor="#DDDDDD",
               markeredgecolor="black", markersize=8, linewidth=0,
               label="Ultra-deep (>10 km)", markeredgewidth=1.5),
    ]

    leg = ax.legend(handles=handles, loc="upper left",
                    bbox_to_anchor=(1.02, 1.0),
                    title="Coal Plants",
                    fontsize=11, title_fontsize=12, frameon=True,
                    framealpha=0.95, edgecolor="black")
    leg.get_title().set_fontweight("bold")

    fig.text(0.5, 0.02,
             "Western coal plants at proven-frontier depths: Centralia WA, Huntington UT, Dave Johnston WY, "
             "Boardman OR (retired), Craig CO, Hayden CO. Major retired plants: Navajo AZ (2,409 MW), San Juan NM (1,848 MW). "
             "Eastern US has 290 plants requiring ultra-deep drilling (>10 km).",
             ha="center", fontsize=10, style="italic", color="#555")

    outfile = PLOT_DIR / "coal_plants_western_zoom.png"
    plt.savefig(outfile, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"✅ Saved: {outfile}")

# ============================================================================
# Main
# ============================================================================

def main():
    print("Creating coal plant overlay maps...")
    geo, coal, states = load_data()

    print(f"\nLoaded:")
    print(f"  {len(geo):,} geothermal grid cells")
    print(f"  {len(coal)} coal plants")
    print(f"  {len(states)} CONUS states")

    create_coal_overlay_map(geo, coal, states)
    create_western_zoom_map(geo, coal, states)

    print("\n✅ Maps complete!")

if __name__ == "__main__":
    main()

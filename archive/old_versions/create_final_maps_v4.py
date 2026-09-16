#!/usr/bin/env python3
"""
Final maps v4 — real US state outlines, no striping, shallow bins preserved, readable legend.

Why v4 exists:
  * The Stanford grid is a PROJECTED (Web Mercator) lattice, so its 2,153 unique
    longitudes do not sit on a uniform degree spacing. Snapping it to a lat/lon
    raster collapsed some columns and left others empty -> the vertical striping.
    v4 rasterises with a KD-tree nearest-neighbour lookup instead, so every display
    pixel takes the value of the closest model cell. No gaps, no stripes, and no
    invented values.
  * Legend is drawn below the map as a horizontal strip, so the 1.3 aspect ratio
    can never clip it.
  * Deep-to-shallow draw order plus a nearest-neighbour raster keeps the rare
    4-5 km and 5-6 km cells at full strength.
"""
import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm
from matplotlib.patches import Patch
from scipy.spatial import cKDTree
from pathlib import Path

PLOT_DIR = Path("plots")
PLOT_DIR.mkdir(exist_ok=True)

BINS = ["<=4 km", "4-5 km", "5-6 km", "6-7 km", "7-8 km", "8-10 km", ">10 km"]
LABELS = ["≤4 km", "4-5 km", "5-6 km", "6-7 km", "7-8 km", "8-10 km", ">10 km"]
BIN_DEPTH = {"<=4 km": 3.5, "4-5 km": 4.5, "5-6 km": 5.5, "6-7 km": 6.5,
             "7-8 km": 7.5, "8-10 km": 9.0, ">10 km": 12.0}

# navy -> blue -> green -> yellow -> orange -> red -> grey
COLORS = ["#062F6F", "#2E7BC4", "#00A94F", "#FFE000", "#FF8A00", "#E02020", "#DCDCDC"]
BOUNDARIES = [3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 10.0, 15.0]
CMAP = ListedColormap(COLORS); CMAP.set_bad((1, 1, 1, 0))
NORM = BoundaryNorm(BOUNDARIES, CMAP.N)

VIEW = dict(x0=-125.4, x1=-66.6, y0=24.2, y1=49.5)
ASPECT = 1.32


def load():
    df = pd.read_csv("data/processed/conus_depth_to_300c.csv")
    df["bin_key"] = df["depth_bin"].replace({"≤4 km": "<=4 km"})
    df["depth_num"] = df["bin_key"].map(BIN_DEPTH)
    st = gpd.read_file("data/raw/boundaries/cb_2023_us_state_20m.shp")
    st = st[~st["STUSPS"].isin({"AK", "HI", "PR", "VI", "GU", "MP", "AS"})]
    return df, st.to_crs("EPSG:4326")


def rasterize(df, nx=2000, ny=1000, max_km=6.0):
    """Nearest-neighbour raster: each pixel = depth of the closest model cell.

    max_km caps how far a pixel may reach, which keeps ocean and offshore blank
    instead of smearing coastal values out to sea.
    """
    xs = np.linspace(VIEW["x0"], VIEW["x1"], nx)
    ys = np.linspace(VIEW["y0"], VIEW["y1"], ny)
    gx, gy = np.meshgrid(xs, ys)

    latref = np.cos(np.radians(df["lat"].mean()))
    # scale longitude so distances are roughly isotropic in km before querying
    tree = cKDTree(np.column_stack([df["lon"].values * latref, df["lat"].values]))
    dist, idx = tree.query(np.column_stack([gx.ravel() * latref, gy.ravel()]), k=1)

    vals = df["depth_num"].values[idx].astype(float)
    vals[dist * 111.0 > max_km] = np.nan
    return vals.reshape(ny, nx), [VIEW["x0"], VIEW["x1"], VIEW["y0"], VIEW["y1"]]


def stats(df):
    n = len(df)
    c = {k: int((df["bin_key"] == k).sum()) for k in BINS}
    return c, {k: 100.0 * c[k] / n for k in BINS}


def legend_below(fig, ax, c, p):
    """Horizontal legend under the axes — immune to aspect-ratio clipping."""
    hs = [Patch(facecolor=col, edgecolor="black", linewidth=0.7,
                label=f"{lab}  {p[k]:.2f}%  ({c[k]:,})")
          for k, lab, col in zip(BINS, LABELS, COLORS)]
    leg = fig.legend(handles=hs, loc="lower center", bbox_to_anchor=(0.5, 0.035),
                     ncol=7, fontsize=12.5, frameon=True, framealpha=1.0,
                     edgecolor="black", handlelength=1.8, handleheight=1.3,
                     columnspacing=1.3, borderpad=0.7,
                     title="Depth required to reach 300 °C   (share of CONUS model cells)",
                     title_fontsize=13.5)
    leg.get_title().set_fontweight("bold")


def frame(ax, st, title, sub):
    st.boundary.plot(ax=ax, linewidth=0.7, edgecolor="#2A2A2A", zorder=400)
    ax.set_xlim(VIEW["x0"], VIEW["x1"]); ax.set_ylim(VIEW["y0"], VIEW["y1"])
    ax.set_aspect(ASPECT)
    ax.set_xlabel("Longitude", fontsize=14, fontweight="bold")
    ax.set_ylabel("Latitude", fontsize=14, fontweight="bold")
    ax.set_title(f"{title}\n{sub}", fontsize=20, fontweight="bold", pad=14)
    ax.tick_params(labelsize=11.5)
    ax.set_facecolor("white")


def save(fig, name):
    out = PLOT_DIR / name
    fig.savefig(out, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  saved {out}")


def make_heatmap(df, st, c, p):
    raster, extent = rasterize(df)
    fig, ax = plt.subplots(figsize=(21, 13))
    fig.subplots_adjust(bottom=0.16)
    ax.imshow(np.ma.masked_invalid(raster), origin="lower", extent=extent,
              cmap=CMAP, norm=NORM, interpolation="nearest", aspect="auto", zorder=50)
    frame(ax, st, "Depth Required to Reach 300 °C",
          "Conterminous United States — continuous field, ~3 km nearest-neighbour raster")
    legend_below(fig, ax, c, p)
    fig.text(0.5, 0.012,
             "Stanford Thermal Earth Model (Aljubran & Horne 2024) 0–7 km + digitized SMU maps "
             "(Blackwell et al. 2011) 7.5–10 km  |  state outlines: US Census TIGER 2023",
             ha="center", fontsize=10.5, style="italic", color="#555")
    save(fig, "depth_to_300c_heatmap.png")

    v = raster[np.isfinite(raster)]
    print("  raster composition:")
    for lo, hi, lab in [(3, 4, "≤4 km"), (4, 5, "4-5 km"), (5, 6, "5-6 km"), (6, 7, "6-7 km"),
                        (7, 8, "7-8 km"), (8, 10, "8-10 km"), (10, 99, ">10 km")]:
        n = int(((v >= lo) & (v < hi)).sum())
        print(f"    {lab:8s}: {n:8,} px ({100.0*n/v.size:5.2f}%)")


def make_points(df, st, c, p):
    size = {"<=4 km": 130, "4-5 km": 130, "5-6 km": 26, "6-7 km": 9,
            "7-8 km": 9, "8-10 km": 5, ">10 km": 3}
    fig, ax = plt.subplots(figsize=(21, 13))
    fig.subplots_adjust(bottom=0.16)
    for k in reversed(BINS):
        sub = df[df["bin_key"] == k]
        if sub.empty:
            continue
        big = size[k] >= 26
        ax.scatter(sub["lon"], sub["lat"], s=size[k], c=COLORS[BINS.index(k)],
                   alpha=0.40 if k == ">10 km" else 0.95,
                   edgecolors="black" if big else "none",
                   linewidths=0.6 if big else 0.0,
                   zorder=100 + (len(BINS) - BINS.index(k)))
    frame(ax, st, "Depth Required to Reach 300 °C",
          "Conterminous United States — all 534,942 model cells, discrete categories")
    legend_below(fig, ax, c, p)
    fig.text(0.5, 0.012,
             "Rare shallow cells (4–5 km, 5–6 km) are drawn larger and last so single cells "
             "stay visible at CONUS scale.",
             ha="center", fontsize=10.5, style="italic", color="#555")
    save(fig, "depth_to_300c_points.png")


def main():
    df, st = load()
    c, p = stats(df)
    print(f"{len(df):,} cells | {len(st)} CONUS states")
    for k, lab in zip(BINS, LABELS):
        print(f"  {lab:8s}: {c[k]:8,} ({p[k]:5.2f}%)")
    print("\nheatmap:");   make_heatmap(df, st, c, p)
    print("\npoint map:"); make_points(df, st, c, p)
    print("\ndone")


if __name__ == "__main__":
    main()

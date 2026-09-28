#!/usr/bin/env python3
"""Map of the accessible-resource regions from the geographic-reference table.

Draws the project depth-to-300 C field (same style as create_heatmap.py) and
overlays, for each of the 7 reference regions, a translucent blob over its
bounding box and a numbered star at its representative lat/lon. Marker numbers
match the README table row order.

Reproducible: region boxes come from build_reference_tables.REGIONS and the star
positions from build_reference(df) (the same rep_lat/rep_lon written to the CSV).
"""
import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.colors import ListedColormap, BoundaryNorm
from matplotlib.path import Path
from matplotlib.patches import PathPatch
from scipy.interpolate import griddata

from build_reference_tables import REGIONS, build_reference

LON_MIN, LON_MAX = -126, -65
LAT_MIN, LAT_MAX = 24, 50.5

# --- data -------------------------------------------------------------------
df = pd.read_parquet("data/processed/conus_depth_to_300c.parquet")
ref = build_reference(df).reset_index(drop=True)

states = gpd.read_file("data/raw/boundaries/cb_2023_us_state_20m.shp")
states = states[~states["STUSPS"].isin({"AK", "HI", "PR", "VI", "GU", "MP", "AS"})]
states = states.to_crs("EPSG:4326")
us_boundary = states.union_all()

# --- depth field background (matches create_heatmap.py) ---------------------
depth_map = {"≤4 km": 3, "4-5 km": 4.5, "5-6 km": 5.5, "6-7 km": 6.5,
             "7-8 km": 7.5, "8-10 km": 9, ">10 km": 12}
df["depth_numeric"] = df["depth_bin"].map(depth_map)

grid_lon = np.linspace(LON_MIN, LON_MAX, 1200)
grid_lat = np.linspace(LAT_MIN, LAT_MAX, 600)
glon, glat = np.meshgrid(grid_lon, grid_lat)
grid_depth = griddata(np.column_stack([df["lon"], df["lat"]]),
                      df["depth_numeric"].values, (glon, glat), method="linear")

colors = ["#0000CC", "#0066FF", "#00CC00", "#FFFF00", "#FF9900", "#FF3300", "#CCCCCC"]
boundaries = [0, 3.5, 5, 6, 7, 8, 10, 15]
cmap = ListedColormap(colors)
norm = BoundaryNorm(boundaries, cmap.N)

fig, ax = plt.subplots(figsize=(20, 11))
ax.set_facecolor("#E8E8E8")
im = ax.contourf(glon, glat, grid_depth, levels=boundaries, cmap=cmap,
                 norm=norm, extend="both", alpha=0.55)

if hasattr(us_boundary, "geoms"):
    paths = [Path(np.asarray(g.exterior.coords)) for g in us_boundary.geoms]
else:
    paths = [Path(np.asarray(us_boundary.exterior.coords))]
clip = PathPatch(Path.make_compound_path(*paths), transform=ax.transData, facecolor="none")
for coll in ax.collections:
    coll.set_clip_path(clip)

states.boundary.plot(ax=ax, linewidth=0.8, edgecolor="white", alpha=0.8, zorder=5)

# --- numbered stars ---------------------------------------------------------
# Stars only: bounding boxes were removed because a lat/lon rectangle does not
# reflect a region's true data footprint (it over-covers empty ground and
# under-covers coherent clusters). The star marks the representative location;
# the depth field itself shows the extent.
for i, (name, typ, st, (la0, la1, lo0, lo1), setting) in enumerate(REGIONS, start=1):
    rlat = float(ref.loc[i - 1, "rep_lat"])
    rlon = float(ref.loc[i - 1, "rep_lon"])
    ax.scatter(rlon, rlat, marker="*", s=900, c="#FFD400",
               edgecolors="#111111", linewidths=1.8, zorder=11)
    ax.text(rlon, rlat, str(i), fontsize=15, fontweight="bold",
            ha="center", va="center", color="#111111", zorder=12,
            path_effects=[pe.withStroke(linewidth=2.5, foreground="white")])

# --- legend keying numbers -> region names ----------------------------------
lines = [f"{i}.  {name}  ({st})" for i, (name, _t, st, _b, _s) in enumerate(REGIONS, 1)]
legend_txt = "Accessible-resource regions\n" + "\n".join(lines)
ax.text(0.985, 0.03, legend_txt, transform=ax.transAxes, fontsize=12.5,
        ha="right", va="bottom", family="monospace", zorder=15,
        bbox=dict(boxstyle="round,pad=0.6", facecolor="white",
                  edgecolor="#333333", alpha=0.92))

# --- styling (matches heatmap) ----------------------------------------------
ax.set_xlabel("Longitude", fontsize=16, fontweight="bold")
ax.set_ylabel("Latitude", fontsize=16, fontweight="bold")
ax.set_title("Suggested accessible 300 °C regions\n"
             "Numbered stars mark each region in the reference table",
             fontsize=20, fontweight="bold", pad=20)
ax.set_xlim(LON_MIN, LON_MAX)
ax.set_ylim(LAT_MIN, LAT_MAX)
ax.set_aspect("equal")

cbar = plt.colorbar(im, ax=ax, orientation="horizontal", pad=0.05,
                    aspect=50, shrink=0.8, ticks=[3, 4.5, 5.5, 6.5, 7.5, 9, 12])
cbar.set_label("Modeled depth to 300 °C (km)", fontsize=14, fontweight="bold")
cbar.ax.set_xticklabels(["≤4", "4-5", "5-6", "6-7", "7-8", "8-10", ">10"], fontsize=11)

ax.text(0.5, -0.08,
        "Data: Stanford Thermal Earth Model (2024) + SMU Geothermal Lab (2011) | "
        "Regions & coordinates: build_reference_tables.py",
        transform=ax.transAxes, fontsize=10, ha="center", style="italic", color="#666")

plt.tight_layout()
out = "plots/accessible_regions_map.png"
plt.savefig(out, dpi=300, bbox_inches="tight", facecolor="white")
plt.close()
print(f"Saved: {out}")

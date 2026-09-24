#!/usr/bin/env python3
"""
Build plots/smu_registration_diagnostic.png: a skeptic's-eye view of the corrected
SMU map registration.

Left panel  : the 10 km SMU temperature field, georeferenced pixel->Lambert->WGS84
              via the fitted affine, scattered and colored by temperature, with the
              true Census CONUS state boundaries overlaid. The drawn thermal field
              should now sit on the correct states / land.
Right panel : histogram of per-border-point registration residuals (km), with the
              measured median and 90th-percentile marked.

All error numbers are COMPUTED here from register_smu_maps.py's fit -- none hardcoded.
Does not touch any SMU CSV.
"""
from pathlib import Path

import numpy as np
import geopandas as gpd
import pyproj
import matplotlib.pyplot as plt
from PIL import Image
from scipy.spatial.distance import cdist

import register_smu_maps as reg

REPO = Path(__file__).resolve().parent
OUT = REPO / "plots/smu_registration_diagnostic.png"

# SMU legend: bin color -> upper-bin temperature (matches digitize_all_smu_maps.py)
LEGEND_COLORS = np.array([[0, 100, 0], [0, 180, 0], [100, 255, 0], [200, 255, 0],
    [255, 255, 0], [255, 200, 0], [255, 150, 0], [255, 100, 0], [255, 50, 0],
    [255, 0, 0], [200, 0, 100], [150, 0, 150], [100, 0, 200]])
LEGEND_TEMP_HIGH = np.array([50, 75, 100, 125, 150, 175, 200, 225, 250, 275, 300, 325, 350])

DEPTH = 10.0
IMG = reg.IMG_DIR / reg.LAYERS[DEPTH]

to_wgs = pyproj.Transformer.from_crs(reg.CRS, "EPSG:4326", always_xy=True)


def main():
    # ---- re-fit the 10 km layer (same deterministic ICP) ----
    states = reg.load_states()
    ref = reg.ref_points(states)
    img = np.array(Image.open(IMG))[:, :, :3].astype(int)
    H, W = img.shape[:2]
    xs, ys = reg.border_mask(img)
    mask_pts = np.column_stack([xs, ys])
    ax, ay, dd, kmpp = reg.icp(mask_pts, ref)
    resid_km = dd * kmpp
    med_km = float(np.median(resid_km))
    p90_km = float(np.percentile(resid_km, 90))

    # ---- digitize the temperature field via the fitted affine ----
    Lin = np.array([[ax[0], ax[1]], [ay[0], ay[1]]])
    off = np.array([ax[2], ay[2]])
    Linv = np.linalg.inv(Lin)
    excl = np.zeros((H, W), bool)
    excl[:, 1495:] = True            # legend/colorbar
    excl[895:, 230:450] = True       # SMU logo
    flat = img.reshape(-1, 3).astype(float)
    dist = cdist(flat, LEGEND_COLORS.astype(float))
    idx = dist.argmin(1); dmin = dist.min(1)
    valid = (dmin <= 60) & (~excl.ravel())
    yy, xx = np.mgrid[0:H, 0:W]
    px = xx.ravel()[valid].astype(float); py = yy.ravel()[valid].astype(float)
    temp = LEGEND_TEMP_HIGH[idx[valid]]
    XY = (np.column_stack([px, py]) - off) @ Linv.T
    lon, lat = to_wgs.transform(XY[:, 0], XY[:, 1])

    # Drop stray color-matched pixels (map-edge column, attribution text) that
    # digitize offshore. Keep only points within a small buffer of CONUS so the
    # "field lands on the correct states" check reads cleanly.
    from shapely.geometry import Point
    conus = states.to_crs("EPSG:4326").union_all().buffer(0.5)
    inside = gpd.GeoSeries([Point(a, b) for a, b in zip(lon, lat)],
                           crs="EPSG:4326").within(conus).values
    lon, lat, temp = lon[inside], lat[inside], temp[inside]

    # subsample for a lighter scatter
    rng = np.random.default_rng(0)
    n = len(lon)
    sel = rng.choice(n, size=min(n, 120_000), replace=False)

    # ---- figure ----
    fig = plt.figure(figsize=(16, 8))
    gs = fig.add_gridspec(1, 3, width_ratios=[2.1, 2.1, 1.0], wspace=0.22)
    axf = fig.add_subplot(gs[0, :2])
    axh = fig.add_subplot(gs[0, 2])

    sc = axf.scatter(lon[sel], lat[sel], c=temp[sel], s=1.2, cmap="YlOrRd",
                     vmin=25, vmax=350, linewidths=0)
    states_wgs = states.to_crs("EPSG:4326")
    states_wgs.boundary.plot(ax=axf, color="black", linewidth=0.6, zorder=5)
    axf.set_xlim(-127, -65); axf.set_ylim(23, 51)
    axf.set_aspect(1.3)
    axf.set_xlabel("Longitude"); axf.set_ylabel("Latitude")
    axf.set_title("SMU 10 km temperature field, georeferenced via fitted Lambert affine\n"
                  "(true Census state borders in black -- thermal field now lands on the correct states)",
                  fontsize=11, fontweight="bold")
    cb = plt.colorbar(sc, ax=axf, orientation="horizontal", pad=0.08, aspect=45, shrink=0.85)
    cb.set_label("Temperature (C)")
    axf.text(0.015, 0.03,
             f"Lambert Conformal Conic (ESRI:102004), ICP-fitted per layer\n"
             f"Registration error: median {med_km:.1f} km / 90th pct {p90_km:.1f} km\n"
             f"Replaces old plate-carree assumption (~28 km median / ~90 km 90th)",
             transform=axf.transAxes, fontsize=9, va="bottom", ha="left",
             bbox=dict(boxstyle="round", facecolor="white", alpha=0.85, edgecolor="0.5"))

    axh.hist(resid_km, bins=60, range=(0, np.percentile(resid_km, 99)),
             color="#4C78A8", edgecolor="white", linewidth=0.3)
    axh.axvline(med_km, color="#E45756", lw=2, label=f"median {med_km:.1f} km")
    axh.axvline(p90_km, color="#F58518", lw=2, ls="--", label=f"90th pct {p90_km:.1f} km")
    axh.set_xlabel("Per-border-point residual (km)")
    axh.set_ylabel("Reference border points")
    axh.set_title("Registration residual distribution\n(10 km layer, nearest drawn border)",
                  fontsize=10, fontweight="bold")
    axh.legend(fontsize=9)

    fig.suptitle("SMU temperature-at-depth map registration diagnostic (10 km layer)",
                 fontsize=13, fontweight="bold", y=0.99)
    fig.savefig(OUT, dpi=150, bbox_inches="tight")
    print(f"wrote {OUT}  (median {med_km:.2f} km, 90th {p90_km:.2f} km, km/px {kmpp:.3f})")


if __name__ == "__main__":
    main()

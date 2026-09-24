#!/usr/bin/env python3
"""
Reproducible georeferencing of the SMU 2011 temperature-at-depth maps (7.5/8.5/10 km).

This is the TRACKED, documented counterpart of the (untracked) smu_registration/
prototype. It re-fits, from the repo root and from first principles, the per-layer
affine transforms that digitize_all_smu_maps.py carries as the frozen constant dict
LAMBERT_AFFINES. Running it regenerates those constants and verifies they reproduce.

================================================================================
THE SEVEN THINGS THIS SCRIPT DOCUMENTS AND IMPLEMENTS
================================================================================

1. SOURCE IMAGE COORDINATE SYSTEM / PROJECTION ASSUMPTION
   The SMU maps are raster images with state and national borders DRAWN on them.
   Those drawn borders are a dense geographic ground truth: if we know the map's
   projection, the relationship (projected coordinate) -> (pixel) is EXACTLY a
   6-parameter affine. We assume the map is a conic projection, specifically
   USA Contiguous Lambert Conformal Conic (ESRI:102004). Why a conic and not
   plate-carree (a linear lat/lon grid): a wrong projection cannot be affine-fit
   to low residual. Plate-carree draws the 49th parallel as a straight line, but
   the SMU map draws it as a curve; forcing an affine onto that mismatch leaves a
   ~28 km median residual. The conic assumption drives the residual down to ~3 km,
   which is how we know it is the correct projection family. (See REPORT.md /
   docs/SMU_REGISTRATION_REPORT.md for the full per-projection residual table.)

2. LAMBERT PROJECTION PARAMETERS
   CRS = "ESRI:102004" = USA Contiguous Lambert Conformal Conic. pyproj resolves
   its standard parallels (33 N and 45 N), central meridian (-96), and datum
   (NAD83) internally from the CRS code, so we do not hand-specify them. At this
   ~3.6 km/pixel resolution with 25 C color bins, Albers Equal Area (EPSG:5070 /
   ESRI:102003) is a STATISTICAL TIE with Lambert (~3 km either way); both are
   conic and indistinguishable here. Lambert is chosen as the marginally lower-
   residual winner and matches the SMU/AAPG conic style.

3. CONTROL POINTS / STATE-BOUNDARY DATA
   Reference truth: U.S. Census cb_2023_us_state_20m state boundaries, dropping the
   non-CONUS territories (AK, HI, PR, VI, GU, MP, AS). We interpolate points along
   every boundary line at SPACING metres to form a dense reference point cloud.
   The map's own drawn borders are extracted as a pixel mask by DESATURATION:
   border lines are gray/black (low saturation) over saturated temperature fill, so
   the mask is (sat < 28) & (25 < val < 200). Logo / colorbar / title-text boxes
   are excluded by pixel-rectangle masks so text strokes are not mistaken for
   borders. These exclusion boxes are per the smu_registration/register_all.py fit
   that produced the frozen constants and must match it exactly to reproduce them.

4. THE AFFINE TRANSFORMATION
   6-parameter affine, projected (X, Y) metres -> pixel (px, py):
       px = ax[0]*X + ax[1]*Y + ax[2]
       py = ay[0]*X + ay[1]*Y + ay[2]
   Fitted by ordinary least squares (np.linalg.lstsq) on matched point pairs.

5. THE ICP / REFINEMENT PROCEDURE
   Trimmed Iterative Closest Point. Initialization: map the reference bounding box
   onto the drawn-mask bounding box (with a Y flip, since projected Y increases up
   but pixel y increases down). Then for ITERS=40 iterations: apply the current
   affine to the reference cloud, find each transformed reference point's nearest
   drawn-mask pixel (cKDTree), keep the best-matching TRIM=0.8 fraction (robust
   rejection of outliers / generalized-coastline mismatches), and re-fit the affine
   by least squares on those pairs. The procedure is fully DETERMINISTIC: fixed
   bbox init, fixed trim, fixed iteration count, plain lstsq, no RNG. That is why
   it reproduces the frozen constants to floating-point closeness.

6. CONVERSION BACK TO WGS84
   pyproj.Transformer.from_crs("ESRI:102004", "EPSG:4326", always_xy=True). To
   georeference a pixel: invert the affine to recover Lambert (X, Y), then transform
   Lambert -> WGS84 lon/lat. always_xy keeps coordinate order as (lon/x, lat/y).

7. RESIDUAL / ERROR CALCULATION
   After the final fit, for each reference border point take its nearest-neighbour
   pixel distance to the drawn-border mask. Convert pixels to km with the fitted
   scale km/pixel = 1 / sqrt(|det(linear part)|) / 1000. Report the MEDIAN and the
   90th PERCENTILE. These are the honest registration errors.

KEY CAVEAT
   This transform is fitted ONLY to the 1665-wide image layout (the 7.5/8.5/10 km
   maps). The 1381-wide shallow maps (3.5-6.5 km) use the same projection but a
   different crop/scale and are NOT digitized here; the Stanford model is
   authoritative at 0-7 km. Do not apply these affines to the 1381-wide layer.

Outputs (provenance only; does NOT touch any SMU CSV):
   data/processed/smu_lambert_affines.json  -- affine coeffs + CRS + residuals
"""
import json
from pathlib import Path

import numpy as np
import geopandas as gpd
import pyproj
from PIL import Image
from scipy.spatial import cKDTree
from shapely.geometry import MultiLineString

# ---------------------------------------------------------------------------
# Configuration (must match smu_registration/register_all.py to reproduce the
# frozen LAMBERT_AFFINES in digitize_all_smu_maps.py)
# ---------------------------------------------------------------------------
CRS = "ESRI:102004"          # USA Contiguous Lambert Conformal Conic
SPACING = 3000               # metres between interpolated reference border points
ICP_ITERS = 40               # ICP iterations (deterministic)
ICP_TRIM = 0.8               # keep best-matching 80% of pairs each iteration

REPO = Path(__file__).resolve().parent
STATE_SHP = REPO / "data/raw/boundaries/cb_2023_us_state_20m.shp"
IMG_DIR = REPO / "data/raw/smu/images"
OUT_JSON = REPO / "data/processed/smu_lambert_affines.json"

LAYERS = {
    7.5: "smu_2011_7point5km_temperature.png",
    8.5: "smu_2011_8point5km_temperature.png",
    10.0: "smu_2011_10km_temperature.png",
}

# The frozen constants currently used by the production pipeline
# (digitize_all_smu_maps.py). We re-fit and assert we reproduce these.
FROZEN_AFFINES = {
    7.5: {"ax": [2.74791908e-04, 2.41211792e-06, 8.20347718e+02],
          "ay": [1.22852193e-06, -2.81582807e-04, 5.81215644e+02]},
    8.5: {"ax": [2.74760464e-04, 2.36986206e-06, 8.20308385e+02],
          "ay": [1.22872771e-06, -2.81566251e-04, 5.81225875e+02]},
    10.0: {"ax": [2.74834460e-04, 2.46452084e-06, 8.20366216e+02],
           "ay": [1.22750341e-06, -2.81562016e-04, 5.81188281e+02]},
}


def load_states():
    """Census CONUS state boundaries, reprojected to the Lambert CRS."""
    states = gpd.read_file(STATE_SHP)
    states = states[~states["STUSPS"].isin({"AK", "HI", "PR", "VI", "GU", "MP", "AS"})]
    return states


def ref_points(states, spacing=SPACING):
    """Dense reference border point cloud in the Lambert CRS (item 3 / item 4 input)."""
    s = states.to_crs(CRS)
    pts = []
    for geom in s.boundary:
        if geom is None:
            continue
        for ls in (geom.geoms if isinstance(geom, MultiLineString) else [geom]):
            if ls.length == 0:
                continue
            n = max(2, int(ls.length / spacing))
            pts += [(p.x, p.y) for p in (ls.interpolate(t)
                    for t in np.linspace(0, ls.length, n))]
    return np.array(pts)


def border_mask(img):
    """Extract the drawn-border pixel cloud by desaturation (item 3).

    Exclusion boxes are IDENTICAL to smu_registration/register_all.py, which
    produced the frozen constants; changing them would change the fit.
    """
    mx = img.max(2); mn = img.min(2)
    sat = mx - mn; val = mx
    b = (sat < 28) & (val < 200) & (val > 25)
    b[:, 1495:] = False           # right legend / colorbar
    b[895:, 230:450] = False      # SMU logo lower-left
    b[995:, 940:1320] = False     # "Blackwell et al" attribution text
    b[230:300, 700:1230] = False  # title text band
    ys, xs = np.where(b)
    return xs.astype(float), ys.astype(float)


def fit_affine(src, dst):
    """Least-squares 6-parameter affine, src(X,Y) -> dst(px,py) (item 4)."""
    M = np.column_stack([src[:, 0], src[:, 1], np.ones(len(src))])
    ax = np.linalg.lstsq(M, dst[:, 0], rcond=None)[0]
    ay = np.linalg.lstsq(M, dst[:, 1], rcond=None)[0]
    return ax, ay


def apply_affine(ax, ay, src):
    M = np.column_stack([src[:, 0], src[:, 1], np.ones(len(src))])
    return np.column_stack([M @ ax, M @ ay])


def icp(mask_pts, ref, iters=ICP_ITERS, trim=ICP_TRIM):
    """Deterministic trimmed ICP fit of projected coords -> pixels (item 5).

    Returns ax, ay (affine), dd (per-ref nearest-pixel distances), kmpp (km/pixel).
    """
    tree = cKDTree(mask_pts)
    xs, ys = mask_pts[:, 0], mask_pts[:, 1]
    rx0, rx1 = ref[:, 0].min(), ref[:, 0].max()
    ry0, ry1 = ref[:, 1].min(), ref[:, 1].max()
    # bbox init: ref bbox -> mask bbox, projected Y up mapped to pixel y down
    sx = (xs.max() - xs.min()) / (rx1 - rx0)
    sy = (ys.max() - ys.min()) / (ry1 - ry0)
    ax = np.array([sx, 0, xs.min() - sx * rx0])
    ay = np.array([0, -sy, ys.max() + sy * ry0])
    for _ in range(iters):
        cur = apply_affine(ax, ay, ref)
        dd, idx = tree.query(cur)
        keep = np.argsort(dd)[:int(len(dd) * trim)]
        ax, ay = fit_affine(ref[keep], mask_pts[idx[keep]])
    dd, _ = tree.query(apply_affine(ax, ay, ref))
    lin = np.array([[ax[0], ax[1]], [ay[0], ay[1]]])
    # km/pixel from the fitted linear part (item 7)
    kmpp = 1.0 / np.sqrt(abs(np.linalg.det(lin))) / 1000.0
    return ax, ay, dd, kmpp


def compare_to_frozen(depth, ax, ay, ref, kmpp):
    """Return (max_coef_diff, max_pixel_disp, max_km_disp) vs frozen constants."""
    fz = FROZEN_AFFINES[depth]
    fax, fay = np.array(fz["ax"]), np.array(fz["ay"])
    max_coef = max(np.max(np.abs(ax - fax)), np.max(np.abs(ay - fay)))
    # geometric equivalent: how far (px, then km) do the two affines disagree on
    # the actual reference cloud?
    p_fit = apply_affine(ax, ay, ref)
    p_frz = apply_affine(fax, fay, ref)
    px_disp = np.hypot(p_fit[:, 0] - p_frz[:, 0], p_fit[:, 1] - p_frz[:, 1])
    return max_coef, px_disp.max(), px_disp.max() * kmpp


def main():
    print("=" * 78)
    print("SMU MAP REGISTRATION -- reproducible ICP-affine fit (ESRI:102004)")
    print("=" * 78)

    states = load_states()
    ref = ref_points(states)
    print(f"Reference border points: {len(ref):,}  (CRS={CRS}, spacing={SPACING} m)")

    results = {"crs": CRS, "spacing_m": SPACING, "icp_iters": ICP_ITERS,
               "icp_trim": ICP_TRIM, "layers": {}}
    max_coef_all = 0.0
    max_km_all = 0.0

    print(f"\n{'layer':>7s} {'mask px':>9s} {'median km':>10s} {'90th km':>9s} "
          f"{'km/px':>7s} {'max coef d':>12s} {'max km d':>9s}")
    print("-" * 78)

    for depth, fn in LAYERS.items():
        img = np.array(Image.open(IMG_DIR / fn))[:, :, :3].astype(int)
        xs, ys = border_mask(img)
        mask_pts = np.column_stack([xs, ys])
        ax, ay, dd, kmpp = icp(mask_pts, ref)

        med_km = float(np.median(dd) * kmpp)
        p90_km = float(np.percentile(dd, 90) * kmpp)
        max_coef, max_px, max_km = compare_to_frozen(depth, ax, ay, ref, kmpp)
        max_coef_all = max(max_coef_all, max_coef)
        max_km_all = max(max_km_all, max_km)

        label = f"{depth:.1f}km"
        print(f"{label:>7s} {len(mask_pts):>9,} {med_km:>10.2f} {p90_km:>9.2f} "
              f"{kmpp:>7.3f} {max_coef:>12.2e} {max_km:>9.4f}")

        results["layers"][f"{depth}"] = {
            "depth_km": depth,
            "ax": ax.tolist(),
            "ay": ay.tolist(),
            "km_per_pixel": kmpp,
            "residual_median_km": med_km,
            "residual_p90_km": p90_km,
            "n_mask_pixels": int(len(mask_pts)),
            "max_coef_diff_vs_frozen": float(max_coef),
            "max_geom_disp_km_vs_frozen": float(max_km),
        }

    # ---- reproduction verdict (item 5 determinism check) ----
    # Tolerance: 1e-6 on a linear coefficient of ~2.7e-4 is a 0.4% scale error;
    # in practice the ICP reproduces to ~1e-9 (coef) / well under 0.01 km.
    COEF_TOL = 1e-6
    KM_TOL = 0.05  # 50 m -- far below the ~3 km registration accuracy
    reproduced = (max_coef_all < COEF_TOL) and (max_km_all < KM_TOL)
    print("-" * 78)
    print(f"Max coefficient difference vs frozen LAMBERT_AFFINES: {max_coef_all:.3e}")
    print(f"Max geometric displacement vs frozen (worst layer)  : {max_km_all:.4f} km")
    print(f"REPRODUCTION: {'PASS -- reproduces frozen affines' if reproduced else 'FAIL -- discrepancy, DO NOT trust'}")
    results["reproduces_frozen"] = bool(reproduced)
    results["max_coef_diff_vs_frozen"] = float(max_coef_all)
    results["max_geom_disp_km_vs_frozen"] = float(max_km_all)

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_JSON, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nProvenance written: {OUT_JSON.relative_to(REPO)}")

    # Hard assert so a broken fit fails loudly rather than silently shipping.
    assert reproduced, (
        f"Fitted affines do not reproduce frozen constants "
        f"(max coef diff {max_coef_all:.3e}, max disp {max_km_all:.4f} km)")


if __name__ == "__main__":
    main()

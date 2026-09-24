# SMU Map Geographic Registration — Report

**Question:** What transformation correctly maps pixels in the original SMU temperature
images to geographic locations, and what error remains after registration?

**Answer:** The SMU maps use a **conic projection** (Lambert Conformal Conic ≈ Albers,
statistically indistinguishable here). Pixel ↔ projected-coordinate is a simple **affine**.
Registration accuracy is **~3 km median / ~9 km at the 90th percentile** (cross-validated).
The production pipeline's earlier error was assuming a **linear lat/lon (plate-carrée) mapping**,
which mis-registers by ~28 km median / ~90 km at the 90th percentile — worst toward the
north (curvature), pushing hot zones offshore.

> **Status: this is now the production registration method.** The digitization pipeline
> (`digitize_all_smu_maps.py`) uses these per-layer Lambert Conformal Conic (ESRI:102004)
> affines as its georeferencing. The fit is reproducible from the repo root via
> **`register_smu_maps.py`**, which re-derives the same affine coefficients from the drawn
> borders and writes them (with per-layer residuals) to
> `data/processed/smu_lambert_affines.json` as a provenance artifact. The earlier
> plate-carrée assumption has been fully replaced.

---

## Method (no interactive clicking required)

The SMU maps have **state and national borders drawn on them** — a dense geographic
ground truth. Instead of hand-clicking a handful of control points (imprecise, and the
failure mode of the earlier attempts), we:

1. Extracted the drawn borders as a pixel mask — desaturated gray/black lines over the
   saturated temperature fill: `(sat < 28) & (25 < val < 200)`, with logo/colorbar/text
   boxes excluded. ~17k border pixels per layer, cleanly isolated.
2. Took the U.S. Census state boundaries (`cb_2023_us_state_20m`) as reference truth.
3. For each candidate projection, transformed the reference borders into that projection
   and fit a **pure affine** (projected X,Y → pixel x,y) via **ICP** (iterative closest
   point, robust-trimmed: 40 iterations, keep best-matching 80% each iteration,
   bbox-based initialization, deterministic — no RNG).
4. The correct projection is the one whose borders lock onto the drawn lines with the
   **lowest affine residual**. A wrong projection (e.g. plate-carrée, whose 49°N is a
   straight line vs. the drawn curve) cannot be affine-fit to low residual.

Key principle: if the source projection is correct, projected-coords → pixels is *exactly*
affine (6 params). Needing a polynomial to force a fit means the projection is wrong — which
is what sank the earlier degree-2 polynomial attempts.

Each of the three 1665-wide layers (7.5/8.5/10 km) is fit **independently** to its own
drawn borders — no shared-template assumption. Because the ICP is deterministic,
`register_smu_maps.py` reproduces the frozen production affines to floating-point
closeness (max coefficient difference ~5e-7; max geometric displacement < 1 m).

## Results

| Projection | Median resid | 90th pct | ≈ Median km | ≈ 90th km |
|---|---|---|---|---|
| WGS84 plate-carrée (EPSG:4326) — *the earlier assumption* | 8.72 px | 28.2 px | ~28 km | ~90 km |
| Albers Equal Area (EPSG:5070 = ESRI:102003) | 0.89 px | 3.13 px | ~3.2 km | ~11 km |
| **Lambert Conformal Conic (ESRI:102004)** | **0.86 px** | **2.64 px** | **~3.1 km** | **~9.5 km** |

Scale: **3.595 km/pixel** (1665×1000 layer). Per-layer residuals as re-fit by
`register_smu_maps.py`: 7.5 km → 3.13/9.12 km, 8.5 km → 3.16/9.31 km, 10 km → 3.10/8.86 km
(median / 90th).

### Cross-validation (Lambert)
- **Random 70/30 hold-out:** median 3.1 km, 90th 9.2 km — genuine whole-map generalization.
- **Independent control point (Four Corners, 36.999 N / -109.045 W)** — never used by the ICP
  fit: predicted pixel (504, 619). Visual overlay confirms the drawn 4-state junction sits at
  the predicted location. (A coarse manual eyeball of 521 disagreed by ~17 px; the overlay
  shows the *transform* is right and the manual pick was the error.)
- **Fit-West / test-East extrapolation:** median 123 km. This is the one caveat — see below.

## Caveats / honest limitations

1. **Albers vs Lambert is a statistical tie** (~3 km; both conic). This resolution + the
   image's ~25 °C color bins can't distinguish them. Either is correct to ~3 km.
2. **A single global affine leaves small conic curvature residual.** Whole-map *interpolation*
   is ~3 km (random hold-out), but *extrapolating* a west-only fit to the east drifts to ~120 km.
   This means the fitted standard parallels aren't exactly SMU's. For production (which covers
   the whole map, interpolating) this is immaterial — 3 km is far below the ~25 °C-bin,
   low-resolution image's meaningful precision. If tighter accuracy is ever needed, do a
   projection-aware fit solving for the exact standard parallels.
3. **Two image layouts exist.** The 7.5/8.5/10 km maps are 1665×1000; the 3.5/4.5/5.5/6.5 km
   maps are 1381×1000. **This transform is fitted to the 1665-wide group only.** The 1381 group
   uses the same projection but a different crop/scale and would need its own affine fit. The
   shallow maps are not digitized — the Stanford model is authoritative at 0–7 km — so this is
   not a gap in the production pipeline, but any code applying one transform across all layers
   would be registering different layouts with identical math.
4. Fine coastline/island detail (Chesapeake, LA delta, Cape Cod) differs by more than 3 km
   because the shapefile coastline is generalized differently from SMU's — irrelevant to
   temperature-field registration.

## Files

**Tracked (production):**
- `register_smu_maps.py` → reproducible per-layer ICP-affine fit; writes
  `data/processed/smu_lambert_affines.json` (affine coefficients + CRS + per-layer residuals).
- `digitize_all_smu_maps.py` → production digitization; carries the fitted affines as
  frozen `LAMBERT_AFFINES` constants and applies pixel → Lambert → WGS84.
- `make_registration_diagnostic.py` → `plots/smu_registration_diagnostic.png` overlay +
  residual-distribution diagnostic figure.

**Untracked prototype (`smu_registration/`, kept for provenance):**
- `build_mask.py` → `border_mask.npy`, `mask_preview.png`
- `reg_test.py` → per-projection residual table, `best_fit.npy`
- `register_all.py` → the original independent per-layer fit that produced the frozen constants
- `validate_overlay.py` → `overlay_full.png`, `overlay_zooms.png`, `lambert_affine.npy`

## Digitization method (now implemented)

The production pipeline maps each pixel → projected coords via the fitted affine → WGS84 via
pyproj (`ESRI:102004` → `EPSG:4326`), per layer. Temperature color→value extraction was left
untouched (it was never the problem). A separate affine for the 1381-wide layers has **not**
been fit, and is not needed: those shallow depths are covered by the Stanford model.

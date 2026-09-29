<div align="center">

# 🌋 Depth to 300 °C

### Exploring where 300°C geothermal resources may be accessible across CONUS

[![Model cells](https://img.shields.io/badge/model_cells-534%2C942-2E7BC4)](#the-grid)
[![Stanford](https://img.shields.io/badge/Stanford-0–7_km-8C1515)](https://data.openei.org/submissions/7669)
[![SMU](https://img.shields.io/badge/SMU-7.5–10_km-0033A0)](https://www.smu.edu/dedman/academics/departments/earth-sciences/research/geothermallab/datamaps/temperaturemaps)
[![License](https://img.shields.io/badge/code-MIT-green)](#license)

**How deep must you drill to hit 300 °C?**
In the Stanford thermal model, roughly **5% of CONUS reaches 300 °C within 7 km** — the best-constrained part of this estimate. Extending the modeled drilling envelope to **10 km** with the digitized SMU maps raises the estimated accessible area to **roughly 26%** (~1.9 million km²); the remaining ~74% would require drilling deeper than 10 km. These are **modeled, exploratory figures — a screening estimate, not a measured resource assessment.**

</div>

---

## The map

![Depth required to reach 300 °C — continuous field](plots/depth_to_300c_heatmap.png)

*Continuous nearest-neighbour field at ~3 km resolution. State outlines are US Census
TIGER 2023 boundaries. Grey regions require >10 km drilling depth.*

**🔍 [Open the interactive, zoomable version →](https://chrissmithphd.github.io/conus-geothermal-300c/)**

![Depth required to reach 300 °C — all cells](plots/depth_to_300c_points.png)

*All 534,942 cells drawn individually. Shallow cells (green = 5–6 km, blue = 4–5 km, navy = ≤4 km) are drawn larger and last to remain visible at CONUS scale — this overemphasizes rare shallow resources to show where they exist.*

---

## Where the models suggest accessible resources may be

The modeled ≤10 km resource is overwhelmingly west of roughly **−100° longitude**, which broadly
tracks the transition between the actively extending, thin-crust West and the cold, thick, stable
craton beneath the eastern two-thirds of the country. Even there it is not one contiguous target: the **2,770 cells
reaching 300 °C within 6 km** cluster in a handful of distinct volcanic and rift settings. The
table below grounds each in coordinates and modeled depth, read straight off the grid
([`data/processed/geographic_reference.csv`](data/processed/geographic_reference.csv)); the
region names and interpretations are labels laid over those cells, not derived from them.

Region depths are the **median of the continuous Stanford cells that reach 300 °C within 7 km**
(the accessible signature — a box-wide median would be dragged down by surrounding deep cells),
with the shallowest cell in parentheses; coordinates are the median location of that shallow tier.

![Numbered map of the suggested accessible-resource regions](plots/accessible_regions_map.png)

*Each numbered star marks the representative location of the correspondingly numbered region
below; the depth field itself shows each region's extent.*

| # | Region / site | State(s) | Rep. lat, lon | Depth to 300 °C | Cells ≤6 / ≤7 / ≤10 km | Coherence | Setting |
|---:|---|---|---|---:|---:|---|---|
| **1** | **Cascades** (OR/WA/N. CA axis) | OR · WA · CA | 41.96, −121.50 | 6.6 km (min 4.7) | 595 / 5,101 / 14,045 | large coherent belt | Volcanic arc; the shallowest cells in the whole analysis sit on the Cascade crest |
| **2** | **Salton Trough / Imperial Valley** | CA | 33.20, −115.75 | 6.7 km (min 6.1) | 0 / 470 / 734 | large coherent zone | Active spreading center; among the hottest-shallow settings in CONUS |
| **3** | **Snake River Plain / Yellowstone** | ID · WY · MT | 43.45, −112.56 | 6.5 km (min 5.0) | 738 / 5,212 / 10,408 | large coherent belt | Hotspot track arcing NE toward the caldera |
| **4** | **Northern Nevada** (NW corner) | NV | 41.46, −118.58 | 6.7 km (min 4.4) | 100 / 1,048 / 3,304 | large coherent zone | Edge-of-Basin & Range extension, *not* statewide (Black Rock, Surprise Valley) |
| **5** | **Roosevelt Hot Springs / Utah FORGE** | UT | 38.42, −112.83 | 6.2 km (min 4.1) | 54 / 139 / 168 | compact, coherent | DOE EGS field site; small, well-characterized shallow anomaly |
| **6** | **Aspen–Salida / Upper Arkansas** | CO | 38.88, −106.26 | 6.4 km (min 5.3) | 87 / 351 / 504 | coherent cluster | Northern reach of the Rio Grande rift; densest shallow cluster in the interior Rockies |
| **7** | **Rio Grande Rift** (New Mexico) | NM | 34.03, −106.94 | 6.6 km (min 4.4) | 44 / 579 / 2,757 | large coherent zone | Extensional rift; Valles/Jemez, Socorro, Rio Grande corridor |
| **8** | **The Geysers / Clear Lake** | CA | 38.81, −122.76 | 6.0 km (min 4.4) | 222 / 411 / 413 | dense, coherent zone | Clear Lake volcanic field; world's largest operating geothermal complex — shallowest CA cells outside the Salton Trough |
| **9** | **Coso / Owens Valley** | CA | 36.09, −117.37 | 6.5 km (min 5.0) | 28 / 149 / 396 | coherent cluster | Coso Volcanic Field on the eastern Sierra front; operating flash-steam field at China Lake |

*Cell counts are grid cells inside each region's bounding box reaching 300 °C within 6, 7 and
10 km. The boxes are geographic and do not tile CONUS, so they are subsets of — and won't sum
to — the 2,770-cell ≤6 km total. Interiors of Nevada and Utah are mostly 7–10 km; the genuinely
shallow cells sit at the province edges and in the volcanic/rift cores above.*

*This is modeled temperature-at-depth only — not a statement about reservoir quality, fluid, or
whether a well here could produce power. For the coal-plant view of the resource, see
[Coal infrastructure and modeled geothermal potential](#coal-infrastructure-and-modeled-geothermal-potential).*

---

## Accessible area by drilling depth (with an illustrative generation scenario)

The directly supported result here is the **area reaching 300 °C at each drilling depth** — the
cumulative column below. On Stanford's continuous 0–7 km model, roughly **4.70 % of CONUS reaches
300 °C within 7 km**; carrying the estimate into the exploratory SMU layers raises it to
**26.30 % by 10 km**. That area-vs-depth relationship is the robust finding. The **Capacity (GW)**
column is a downstream *scenario* layered on top of it — the same area multiplied by an assumed
power density and development fraction — so it inherits every uncertainty in the area estimate and
adds its own. Treat the ~13,371 GW figure as an order-of-magnitude illustration, not a resource or
generation forecast.

The **Data source** column marks where the estimate stops being Stanford's continuous model
(≤ 7 km) and becomes the coarser, digitized SMU extension (7.5–10 km).

![Geothermal metrics by depth](plots/geothermal_metrics_by_depth.png)

| Depth | Data source | Area (km²) | % CONUS | Cum. % reaching 300 °C (≤ depth) | Capacity (GW) | × US Total |
|---|---|---:|---:|---:|---:|---:|
| ≤4 km | Stanford | 0 | 0.00 | 0.00 | 0 | 0.0 |
| 4–5 km | Stanford | 867 | 0.01 | 0.01 | 5.2 | 0.0 |
| 5–6 km | Stanford | 36,014 | 0.50 | 0.51 | 252 | 0.2 |
| 6–7 km | Stanford | 304,350 | 4.19 | **4.70** | 2,130 | 1.7 |
| 7–8 km | SMU | 197,784 | 2.72 | 7.42 | 1,384 | 1.1 |
| 8–10 km | SMU | 1,371,312 | 18.88 | **26.30** | 9,599 | 7.5 |
| **>10 km** | — | **5,353,343** | **73.70** | *unresolved* | **—** | **—** |
| **≤10 km** | Stanford + SMU | **1,910,326** | **26.30** | **26.30** | **13,371** | **10.4** |
| *Total* | — | *7,263,669* | *100.00* | — | *13,371** | *10.4** |

Area is **latitude-weighted** (`A = R² · cos φ · Δφ · Δλ`). The cumulative column is the share of
CONUS reaching 300 °C within each depth; the **>10 km** row is the share whose depth to 300 °C is
deeper than the mapped 10 km range — *not* a claim that 300 °C is unreachable there. Superhot and
EGS drilling programs target ~15–20 km; this data simply does not resolve the crossing depth past
10 km, so the row carries no cumulative-reach or capacity value. Capacity values
show the scale implied by an assumed 35 MW/km² power density (superhot geothermal, 300–400 °C) and
20 % development; IDDP-2 demonstrated 45 MW/well at 427 °C. US total installed capacity for
comparison: **1,287 GW** (coal: 180 GW). See
[`research/ENERGY_GENERATION_RESEARCH.md`](research/ENERGY_GENERATION_RESEARCH.md) for details.

---

## Methodology

Two independent thermal datasets feed two **separate pipelines**; they are combined only at the
final binning step. Stanford supplies a continuous crossing depth to 7 km; the digitized SMU maps
extend the screen categorically to 10 km.

```
Stanford GeoJSON (0–7 km)               SMU PNG maps (7.5–10 km)
        │                                       │
        │ 8 depth layers, exact °C per cell     │ colour → temperature class (pixel classification)
        │ layers aligned by (lat, lon)          │ georeference: Lambert Conformal Conic
        ▼                                       │ (ESRI:102004) affine, ICP-fit to drawn
  linear interpolation                          │ state borders (~3 km median error)
  T(z) → depth where T = 300 °C                 ▼
        │                              SMU 7.5 / 8.5 / 10 km temperature grids
        ├── crossing found ≤ 7 km → depth_300_km (continuous)
        │
        └── not reached by 7 km ──→ nearest-neighbour match to SMU points,
                                    Haversine ≤ 50 km filter, first layer ≥ 300 °C
                                    → categorical depth bound, else > 10 km
```

### Stanford pipeline — continuous, 0–7 km

The Stanford JSON layers do not share a guaranteed row order, so all eight are **sorted by
`(lat, lon)` and checked to agree to < 1e-6°** before any vertical profile is built — temperatures
are never spliced across locations. For each of the 534,942 cells, the eight modelled temperatures
are linearly interpolated to find where the profile crosses 300 °C:

```python
# Find first adjacent depth pair that brackets 300°C
for i in range(len(temperatures) - 1):
    if temperatures[i] <= 300 < temperatures[i+1]:
        t_low, t_high = temperatures[i], temperatures[i+1]
        d_low, d_high = depths[i], depths[i+1]
        return d_low + (300 - t_low) / (t_high - t_low) * (d_high - d_low)
return np.nan  # 300 °C not reached within 0–7 km
```

Worked example — 250 °C at 6 km, 320 °C at 7 km: `6 + (300 − 250)/(320 − 250) × 1 =` **6.71 km**.
This gives a genuine continuous depth. Result: **25,448 cells (4.8 %)** cross 300 °C within 7 km.

### SMU pipeline — categorical, 7.5–10 km

The three deep SMU maps are published only as rendered PNGs, so they are **digitized** (legend
colours matched to 25 °C temperature classes, each pixel classified by nearest colour) and then
**georegistered projection-aware**: each layer is placed with a **Lambert Conformal Conic
(ESRI:102004) affine fitted by ICP against the maps' own drawn state borders**, then reprojected to
WGS 84. Positional accuracy is **~3 km median / ~9 km at the 90th percentile**. This corrects an
earlier plate-carrée assumption (a linear lat/lon stretch to the CONUS box) that mis-registered the
maps by ~28 km median and pushed hot zones offshore.

For the 509,494 cells that do **not** cross 300 °C inside Stanford's range, the pipeline takes the
**nearest-neighbour SMU point** and then applies a **Haversine ≤ 50 km distance filter**; the first
SMU layer (7.5, 8.5 or 10 km) at ≥ 300 °C is reported as a **categorical depth bound**. This
recovers **116,499** more cells; the remaining **392,995** are classified `> 10 km`. The full
digitization + registration is reproducible from tracked code:
[`digitize_all_smu_maps.py`](digitize_all_smu_maps.py) is self-contained (the fitted Lambert affines
are embedded), and [`register_smu_maps.py`](register_smu_maps.py) re-derives and verifies those
affines from the source maps (see the [registration report](docs/SMU_REGISTRATION_REPORT.md)).

### Combine, bin, area-weight

Continuous Stanford depths and categorical SMU bounds are assigned to the seven project depth bins,
each cell weighted by its true latitude-corrected surface area (`A = R² · cos φ · Δφ · Δλ`), and
tabulated.

### Stanford vs SMU precision

The two sources differ in kind, and the difference is preserved end to end:

- **Stanford** — continuous depth estimate (e.g. "300 °C at 6.37 km").
- **SMU** — categorical upper bound (e.g. "≥ 300 °C by 8.5 km" → the crossing lies in the
  7.5–8.5 km range). Both assume linear, monotonic temperature increase between sampled depths.

![Stanford–SMU overlap comparison](plots/cross_validation_stanford_smu.png)

*Stanford 7.0 km vs SMU 7.5 km — the shallowest depths the two sources share: r = 0.690,
RMSE = 53 °C across 532,455 matched locations (Stanford runs ~39 °C warmer than the digitized SMU
estimates). Neither dataset is ground truth for the other — this shows how far two independent
models agree where they overlap, not a validation of one against the other. Horizontal banding in
the SMU values is the 25 °C class quantization, not noise.*

**Coverage** (of 534,942 cells) — *within 7 km:* 4.8 % of cells / 4.7 % of CONUS area (Stanford);
*within 10 km:* 26.5 % of cells / 26.3 % of CONUS area (Stanford + SMU). Area-weighted percentages
run lower because they down-weight the smaller ground footprint of high-latitude cells; the area
figures are the ones used in the headline and generation table.

**[→ Regional sanity checks (Montana/Yellowstone) and the grid-alignment debugging history](VALIDATION.md)**

---

## Coal infrastructure and modeled geothermal potential

![Coal plants and geothermal overlay](plots/coal_plants_geothermal_overlay.png)

*Coal power plants sized by capacity, colored by geothermal depth. Triangles = operating, circles = retired since 2015.*

### Summary

**335 in-coverage US coal plants analyzed** (5 Alaska plants excluded — they lie outside the CONUS grid domain):
- 25 plants (7%) at ≤10 km depth — only **one** shallower than 8 km
- 20 of those in western US
- 310 plants (93%) at >10 km depth

Apart from a single 62 MW cogeneration plant at 6–7 km, every coal plant sitting on ≤10 km of depth-to-300 °C is in the **8–10 km frontier band**, where 300 °C is only reached at the deepest SMU layer.

### Coal sites worth further screening

All 25 in-coverage coal plants sitting on ≤10 km of depth-to-300 °C, shallowest first then by capacity. Depth shown is the SMU layer where 300 °C is first met.

| Plant | State | Capacity | Status | Depth to 300 °C |
|-------|-------|----------|--------|-----------------|
| Argus Cogen | CA | 62 MW | Operating | 6.8 km |
| Springerville | AZ | 1,766 MW | Operating | 8.5 km |
| Intermountain Power | UT | 1,640 MW | Retired 2025 | 8.5 km |
| North Valmy | NV | 290 MW | Operating | 8.5 km |
| Kennecott Power Plant | UT | 182 MW | Retired 2019 | 8.5 km |
| Martin Lake | TX | 2,380 MW | Operating | 10.0 km |
| Welsh | TX | 1,674 MW | Operating | 10.0 km |
| Comanche | CO | 1,635 MW | Operating | 10.0 km |
| Craig | CO | 1,428 MW | Operating | 10.0 km |
| Huntington | UT | 1,016 MW | Operating | 10.0 km |
| Coronado | AZ | 822 MW | Operating | 10.0 km |
| Pirkey | TX | 721 MW | Retired 2023 | 10.0 km |
| Dolet Hills | LA | 721 MW | Retired 2021 | 10.0 km |
| Boardman | OR | 642 MW | Retired 2020 | 10.0 km |
| Coleto Creek | TX | 622 MW | Operating | 10.0 km |
| Hayden | CO | 465 MW | Operating | 10.0 km |
| Reid Gardner | NV | 295 MW | Retired 2017 | 10.0 km |
| Escalante | NM | 257 MW | Retired 2020 | 10.0 km |
| TS Power Plant | NV | 242 MW | Operating | 10.0 km |
| Ray D Nixon | CO | 207 MW | Operating | 10.0 km |
| Apache Station | AZ | 204 MW | Operating | 10.0 km |
| Valmont | CO | 192 MW | Retired 2017 | 10.0 km |
| Cherokee | CO | 170 MW | Retired 2015 | 10.0 km |
| South Plant | CO | 125 MW | Retired 2022 | 10.0 km |
| Trinidad | CO | 4 MW | Retired 2017 | 10.0 km |

![Western coal plants zoom](plots/coal_plants_western_zoom.png)

*Western states showing locations where existing coal infrastructure overlaps modeled geothermal potential.*

These sites represent interesting coincidences worth investigating further, not conversion feasibility assessments. Factors not considered here include reservoir permeability, water availability, formation chemistry, local geology, grid interconnection constraints, and retrofit economics.

### Geographic Distribution

**Western US:** 20 of 50 plants (40%) at ≤10 km modeled depth  
**Rest of US:** 5 of 285 plants (~2%) at ≤10 km — four in the East Texas Basin / NW Louisiana (Martin Lake, Welsh, Pirkey, Dolet Hills) plus the Gulf-coastal-plain Coleto Creek. **All five are pinned to exactly 10.0 km — the bottom edge of the 8–10 km frontier band, not a shallow resource.** On the map they read as isolated red dots in an otherwise gray (>10 km) East Texas surround; nothing in Texas is genuinely shallow.

**States (all plants at ≤10 km):** Nevada (3/3), California (1/1), Oregon (1/1). Colorado 8/11, Arizona 3/5, Utah 3/7, Texas 4/18, Louisiana 1/4.

**Data:** EIA Form 860 (2025) + Stanford Thermal Earth Model (2024) + SMU (2011). See [`research/COAL_GEOTHERMAL_ANALYSIS.md`](research/COAL_GEOTHERMAL_ANALYSIS.md) for detailed analysis.

---

## Why 300 °C

Supercritical and superhot geothermal systems are the step change the industry is chasing:

- **~5–10× the energy per well** of a conventional 150–200 °C hydrothermal system
- **Far smaller surface footprint** per installed megawatt
- **Baseload, dispatchable, zero-carbon** — the profile the grid is short of
- An explicit **US DOE Geothermal Technologies Office** target

The reason it isn't everywhere already is the subject of this repository: the heat is real,
but it is *deep*.

---

## Data sources

### Primary — Stanford Thermal Earth Model (2024) · 0–7 km

**Aljubran & Horne (2024)**, *Geothermal Energy* 12(1) · DOI [10.1186/s40517-024-00304-7](https://doi.org/10.1186/s40517-024-00304-7)
Dataset: [OEDI submission 7669](https://data.openei.org/submissions/7669) · Live model: [stm.stanford.edu](https://stm.stanford.edu/)

<a name="the-grid"></a>

| | |
|---|---|
| Depth levels | 0, 1, 2, 3, 4, 5, 6, 7 km |
| Cells | 534,942 per level (~4 km spacing, ~18 km² per cell) |
| Method | Physics-informed graph neural network on bottom-hole temperatures |
| Reported error | **MAE 4.8 °C** |
| Coverage | 24.54–49.37 °N, −124.74 to −66.97 °W · complete CONUS |
| Missing values | **zero** |

**Access note:** the published bulk file is a 5.7 GB CSV. This project instead pulled the
per-depth **ArcGIS FeatureServer** layers, which return the same predictions as paginated
GeoJSON — one clean file per depth, ~132–145 MB each. See [`download_stanford.py`](download_stanford.py).

### Secondary — SMU Geothermal Laboratory (2011) · 7.5–10 km

**Blackwell et al. (2011)** · [SMU Geothermal Lab temperature maps](https://www.smu.edu/dedman/academics/departments/earth-sciences/research/geothermallab/datamaps/temperaturemaps)

Only **rendered PNG maps** are public; the underlying grids are sold, not published. To get
numbers beyond Stanford's 7 km ceiling, the published maps were **digitised**: legend colours
were matched to their temperature classes, map pixels classified by nearest colour, and the
result georeferenced to the CONUS extent.

| | |
|---|---|
| Depth levels | **7.5, 8.5, 10** km |
| Points recovered | 1,648,523 (~547–551 k per level) |
| Temperature resolution | **±12.5 °C** (25 °C legend classes; upper bin edge assigned) |
| Classification rate | ~44 % of pixels (remainder is ocean, borders, legend, text) |
| Positional accuracy | ~3 km median / ~9 km 90th pct (Lambert affine fitted by ICP against drawn state borders) |

<details>
<summary><b>Digitisation validation</b> — reconstructed fields at all three depths (click to expand)</summary>

<br>

![All SMU depths](plots/smu_digitized_all_depths.png)

Reconstructed temperature fields at 7.5, 8.5 and 10 km. Major thermal patterns visible in
the source figures are retained after georeferencing, and hot zones fall on land, consistent
with the drawn state boundaries.

![SMU registration diagnostic](plots/smu_registration_diagnostic.png)

*Registration diagnostic: the digitized SMU 10 km field reprojected to WGS 84 with US Census
state boundaries overlaid. The drawn thermal field and true state outlines align after the
Lambert Conformal Conic (ESRI:102004) ICP fit; measured residual is ~3 km median / ~9 km at
the 90th percentile. The fit is fully reproducible from
[`register_smu_maps.py`](register_smu_maps.py).*

</details>

> ⚠️ **This is an approximate re-digitisation of published figures, not the original SMU
> model.** It is used only to bin depths *beyond* Stanford's validated range, never to
> override Stanford where both exist.

---

## Results file

[`data/processed/conus_depth_to_300c.csv`](data/processed) (also Parquet)

| column | meaning |
|---|---|
| `lat`, `lon` | cell centre, WGS 84 decimal degrees |
| `depth_300_km` | interpolated crossing depth; `NaN` where 300 °C is not reached by 10 km |
| `depth_bin` | one of the seven categories |
| `source` | `Stanford` (continuous interpolation) or `SMU digitized` (binned) |

The `source` column matters: Stanford rows carry a genuine continuous depth estimate, SMU
rows carry only a bin. Filter on it before doing anything quantitative with `depth_300_km`.

The region reference table above is regenerated from this grid by
[`build_reference_tables.py`](build_reference_tables.py) into
[`geographic_reference.csv`](data/processed/geographic_reference.csv).

---

## Reproduce it

```bash
python -m venv .venv && source .venv/bin/activate
pip install numpy pandas matplotlib scipy pillow pyarrow geopandas plotly

python download_stanford.py             # ~1 GB from ArcGIS FeatureServer
python digitize_all_smu_maps.py         # PNG maps → 1.65 M georeferenced points (self-contained)
python calculate_depth_to_300c.py       # interpolate + bin + area-weight; writes stats CSVs

# figures + interactive map (read the CSVs above; no numbers are hardcoded)
python create_heatmap.py                # depth_to_300c_heatmap.png
python create_final_map.py              # points map + interactive Leaflet index.html
python create_montana_validation.py     # regional validation plots
python analyze_coal_geothermal_overlay.py && python create_coal_overlay_map.py
python calculate_energy_potential.py && python create_energy_visualizations.py && python create_combined_metrics_plot.py
python build_reference_tables.py        # geographic-reference CSV (region depths + coordinates)
```

`digitize_all_smu_maps.py` is self-contained: the fitted Lambert affines are embedded, so a
single run produces correctly georeferenced output — no separate registration step.

State outlines come from the US Census cartographic boundary file `cb_2023_us_state_20m`,
downloaded into `data/raw/boundaries/`.

---

## Limitations — read before citing

| Issue | Consequence |
|---|---|
| **Stanford stops at 7 km** | Everything deeper leans on the coarser digitised SMU layers |
| **SMU is binned to 25 °C** | ±12.5 °C → roughly **±400 m** of depth uncertainty at a 30 °C/km gradient |
| **SMU digitisation is approximate** | A cell shown as 287.5 °C could genuinely be at 300 °C. Some cells binned 5–7 km here may in truth be shallower. |
| **SMU vintage is 2011** | 13 years older than Stanford; less well data behind it |
| **Linear T(z) between layers** | Real profiles curve; expect ~10–20 % depth error where the gradient changes with depth |
| **~4 km cells** | Sub-grid thermal anomalies are smoothed away |
| **Single 300 °C threshold** | Superhot/supercritical conditions depend on pressure; water becomes supercritical at ~374°C. The 300°C threshold used here is a screening value |
| **No extrapolation performed** | By design. Cells beyond 10 km are reported as `> 10 km`, never as an invented number. |

---

## Repository layout

```
├── README.md
├── index.html                          # interactive map landing page
├── download_stanford.py                # Stanford ArcGIS → GeoJSON
├── digitize_all_smu_maps.py            # SMU PNG → 1.65M georeferenced points (7.5/8.5/10 km)
├── explore_stanford_data.py            # exploratory data analysis
├── calculate_depth_to_300c.py          # main depth-to-300C analysis
├── create_final_map.py                 # interactive + static maps
├── create_montana_validation.py        # regional validation plots
├── data/
│   ├── raw/{stanford,smu,boundaries}/  # untouched source data + manifests
│   └── processed/                      # digitised SMU + final depth grid
├── plots/
└── docs/
    ├── DATA_ACQUISITION_REPORT.md
    ├── DATASET_SUMMARY.md
    └── SMU_DIGITIZATION_REPORT.md
```

Large source and derived data files are gitignored; the manifests in
`data/raw/*/manifest.json` record exactly what was fetched, from where, and when.

---

## References

1. **Aljubran, M. J. & Horne, R. N.** (2024). Thermal Earth model for the conterminous
   United States using an interpolative physics-informed graph neural network.
   *Geothermal Energy* **12**(1). DOI [10.1186/s40517-024-00304-7](https://doi.org/10.1186/s40517-024-00304-7) · [arXiv:2403.09961](https://arxiv.org/abs/2403.09961)
2. **Blackwell, D. D., Richards, M., Frone, Z., et al.** (2011). Temperature-at-depth maps
   for the conterminous US and geothermal resource estimates. *GRC Transactions* **35**.
3. **US Census Bureau** (2023). Cartographic Boundary Files — States (1:20,000,000).
4. **OpenEI / NREL** — [Geothermal Data Repository](https://gdr.openei.org)

---

## License

Code: **MIT**. Analysis, figures and documentation: **CC BY 4.0**.
Stanford model data is public (DOE-funded). SMU map images remain the property of the SMU
Geothermal Laboratory and are reproduced here only to validate the digitisation.

## Acknowledgments

Data sources: Stanford Geothermal Program · SMU Geothermal Laboratory · US DOE Geothermal Technologies Office · OpenEI / NREL · US Census Bureau

Analysis and documentation prepared with [Claude Code](https://claude.ai/code) by Anthropic.

---

<div align="center">

**Christopher Smith** · [@chrissmithphd](https://github.com/chrissmithphd)

*Last updated 2026-09-29*

</div>

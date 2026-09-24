# CONUS Geothermal Temperature Dataset Summary

**Project:** Depth-to-300°C Mapping for Continental United States  
**Date:** 2026-09-14 (updated 2026-09-23)  
**Status:** COMPLETE — Stanford (0–7 km, all 8 layers) downloaded; SMU deep maps (7.5, 8.5, 10 km) digitized and integrated

---

## Executive Summary

Successfully identified and began acquiring authoritative geothermal temperature data for CONUS. The Stanford Thermal Earth Model (2024) provides quantitative gridded temperature predictions from 0-7 km depth and is being downloaded via ArcGIS REST services. SMU Geothermal Laboratory data for deeper depths (7.5-10 km) is NOT available in gridded format without purchase.

> **Update (2026-09-23):** Both datasets are now fully acquired. All 8 Stanford layers were downloaded and validated (534,942 cells each). Although SMU gridded data is not free, the public SMU PNG maps were **digitized** into 1,648,523 georeferenced points at 7.5, 8.5 and 10 km (~547–551 k per layer) — see [`SMU_DIGITIZATION_REPORT.md`](SMU_DIGITIZATION_REPORT.md). These deep SMU layers are used in the final analysis to extend coverage beyond Stanford's 7 km ceiling, so the "reference only / unsuitable" characterizations below reflect the raw PNGs at acquisition time, not the digitized product.

---

## Dataset 1: Stanford Thermal Earth Model (PRIMARY)

### Overview
- **Authority:** Stanford Geothermal Program / DOE OpenEI
- **Reference:** Aljubran, M.J. & Horne, R.N. (2024). DOI: 10.1186/s40517-024-00304-7
- **Coverage:** Complete CONUS
- **Depth Range:** 0, 1, 2, 3, 4, 5, 6, 7 km (8 depth levels)
- **Grid Resolution:** ~18 km² per cell
- **Grid Points:** 534,942 locations per depth level
- **Total Data Points:** 4,279,536 (534,942 × 8 depths)

### Data Access
**Method:** ArcGIS FeatureServer REST API (individual queries per depth)

**Why NOT the 5.7 GB CSV:**
- REST API provides structured, depth-separated data
- Easier to validate and process layer-by-layer
- Includes proper metadata and spatial reference
- Can resume if interrupted

### Data Structure

**Format:** GeoJSON (from ArcGIS REST responses)

**Fields per feature:**
- `T` - Temperature (°C)
- `Lat` - Latitude (decimal degrees)
- `Long` - Longitude (decimal degrees)
- `ObjectId` - Unique identifier
- `geometry` - Point geometry (EPSG:102100 Web Mercator)

**File Organization:**
```
data/raw/stanford/
├── manifest.json                  # Download metadata
├── temperature_0km.json           # ✅ COMPLETED (145 MB)
├── temperature_1km.json           # 🔄 IN PROGRESS
├── temperature_2km.json           # ⏳ PENDING
├── temperature_3km.json           # ⏳ PENDING
├── temperature_4km.json           # ⏳ PENDING
├── temperature_5km.json           # ⏳ PENDING
├── temperature_6km.json           # ⏳ PENDING
└── temperature_7km.json           # ⏳ PENDING
```

**Estimated Total Size:** ~1.2 GB for all 8 layers

### Data Validation Results (0 km layer)

✅ **ALL VALIDATIONS PASSED**

**Feature Count:** 534,942 features  
**Missing Values:** 0 (100% data completeness)

**Temperature Statistics (Surface / 0 km):**
- Range: -2.86°C to 30.66°C
- Mean: 10.59°C
- Median: 9.72°C
- Std Dev: 6.17°C

**Geographic Extent:**
- Latitude: 24.544°N to 49.370°N
- Longitude: -124.741°W to -66.972°W
- Coverage: Complete CONUS

**Data Quality Assessment:**
- ✅ Temperature values physically reasonable for surface conditions
- ✅ Geographic extent matches expected CONUS boundaries
- ✅ No missing or null temperature values
- ✅ Spatial reference properly documented (EPSG:102100)
- ✅ Lat/Long coordinates consistent with Web Mercator geometry

**Temperature Distribution (0 km):**
- 50.7% of locations: 0-10°C
- 40.6% of locations: 10-20°C
- 8.0% of locations: 20-30°C
- <0.1% of locations: >30°C

### Methodology

From the published paper:
- **Model Type:** Physics-informed neural network (PINN)
- **Training Data:** Bottomhole temperature measurements from oil/gas wells
- **Input Variables:** Depth, coordinates, elevation, sediment thickness, magnetic anomaly, gravity anomaly, gamma-ray flux, seismicity, electrical conductivity
- **Validation:** Mean absolute error = 4.8°C
- **Spatial Resolution:** 18 km² grid cells
- **Temporal:** Single time snapshot (not time-varying)

### Depth Coverage Characteristics

| Depth | Expected Temp Range | Est. % ≥300°C |
|-------|---------------------|---------------|
| 0 km  | -3°C to 31°C        | 0.0%          |
| 1 km  | ~20°C to 90°C       | 0.0%          |
| 2 km  | ~40°C to 130°C      | 0.0%          |
| 3 km  | ~60°C to 170°C      | 0.0%          |
| 4 km  | ~80°C to 210°C      | <0.1%         |
| 5 km  | ~100°C to 250°C     | <1%           |
| 6 km  | ~120°C to 290°C     | ~5%           |
| 7 km  | ~140°C to 330°C     | ~15%          |

*Note: Percentages are estimates; actual values TBD after all layers download*

### Strengths

1. **Most Recent:** Published 2024, uses latest bottomhole temperature data
2. **Authoritative:** Stanford + DOE OpenEI, peer-reviewed publication
3. **Complete Coverage:** Full CONUS with no gaps
4. **High Resolution:** 534,942 grid points across CONUS
5. **Well-Documented:** Published methodology, validation metrics, and metadata
6. **Accessible:** Free download via REST API
7. **Quantitative:** Actual temperature values, not just maps
8. **Validated:** Mean absolute error quantified (4.8°C)

### Limitations

1. **Depth Limit:** Maximum 7 km depth
   - Cannot directly determine depth-to-300°C if >7 km required
   - The final analysis found only 4.8% of CONUS reaches 300°C within 7 km, so ~95% requires deeper (>7 km) data

2. **Temporal:** Static model, no seasonal/temporal variation

3. **Model-Based:** Not direct measurements everywhere
   - Based on interpolation/extrapolation from sparse well data
   - Uncertainty varies spatially (highest certainty near wells)

4. **Resolution:** 18 km² cells
   - Cannot resolve fine-scale thermal anomalies
   - Local hot spots may be smoothed

5. **Validation:** 4.8°C MAE propagates to depth uncertainty
   - At typical 25°C/km gradient: ±4.8°C ≈ ±200m depth uncertainty
   - Uncertainty likely higher at greater depths

---

## Dataset 2: SMU Geothermal Laboratory (DIGITIZED FROM PUBLISHED MAPS)

### Overview
- **Authority:** SMU Geothermal Laboratory
- **Reference:** Blackwell et al. (2011)
- **Coverage:** CONUS
- **Depth Range:** 3.5, 4.5, 5.5, 6.5, 7.5, 8.5, 10 km (only 7.5/8.5/10 km digitized and used)
- **Vintage:** 2011 (13 years older than Stanford)

> **Update (2026-09-23):** The section below documents the raw-image acquisition. The public
> PNG maps were subsequently digitized (color→temperature classification + a per-layer Lambert
> Conformal Conic affine fitted by ICP against the maps' drawn state borders), yielding
> 1,648,523 quantitative georeferenced points at 7.5/8.5/10 km with ~3 km median positional
> accuracy. The deep layers **are** used in the final analysis.

### Data Access Status

❌ **GRIDDED DATA NOT PUBLICLY AVAILABLE**

**What Was Obtained:**
- Low-resolution PNG images (7 depth levels)
- Suitable for visualization comparison only
- NOT suitable for quantitative analysis
- NO coordinate system metadata
- NO machine-readable temperature values

**What Is NOT Available (Free):**
- GeoTIFF or raster grids
- CSV or tabular temperature data
- Spatial metadata (projection, datum, resolution)
- Temperature values for specific coordinates

**Commercial Access:**
- High-resolution grids available for purchase
- Contact: geothermal@smu.edu
- Pricing unknown

### Files Downloaded

```
data/raw/smu/images/
├── smu_2011_3point5km_temperature.png  (390 KB)
├── smu_2011_4point5km_temperature.png  (432 KB)
├── smu_2011_5point5km_temperature.png  (453 KB)
├── smu_2011_6point5km_temperature.png  (473 KB)
├── smu_2011_7point5km_temperature.png  (783 KB)
├── smu_2011_8point5km_temperature.png  (787 KB)
└── smu_2011_10km_temperature.png       (775 KB)
```

### Utility

**Reference/Comparison:** SMU images can be used for:
- ✅ Qualitative visual comparison with Stanford data
- ✅ Identifying general temperature patterns
- ✅ Rough validation of Stanford temperatures at 3.5-6.5 km overlap
- ✅ Visualizing deeper temperatures (7.5-10 km) conceptually

**Cannot Be Used For:**
- ❌ Quantitative depth-to-300°C calculations
- ❌ Extracting specific temperature values
- ❌ Spatial analysis or interpolation
- ❌ Accurate comparisons (no coordinate system data)
- ❌ Merging with Stanford data

### Depth Coverage Gap

**CRITICAL GAP:** No quantitative data for depths >7 km

Depths where 300°C might be reached:
- **≤7 km:** Stanford provides quantitative data ✅
- **7-8 km:** Only SMU images (qualitative) ⚠️
- **8-10 km:** Only SMU images (qualitative) ⚠️
- **>10 km:** No data available ❌

**Impact:** Cannot quantitatively map depth-to-300°C for areas requiring >7 km

---

## Coordinate Systems

### Stanford Data
- **Stored As:** EPSG:102100 (Web Mercator)
- **Also Provides:** Lat/Long (WGS84 decimal degrees)
- **Recommendation:** Use Lat/Long for analysis, ignore Web Mercator geometry

### SMU Data  
- **Source images:** No coordinate system metadata embedded (no GeoTIFF tags or world file)
- **Projection determined:** USA Contiguous Lambert Conformal Conic (ESRI:102004), recovered by fitting a per-layer affine to the maps' drawn state borders via ICP
- **Reprojected:** Digitized pixels are converted Lambert → WGS84; the earlier plate-carrée (linear lat/lon from CONUS extent) assumption mis-registered by ~28 km median and was superseded

---

## Temperature Units

### Confirmed: Celsius (°C)

**Evidence:**
- Stanford 0 km: -2.86°C to 30.66°C (physically reasonable for surface)
- Stanford 0 km mean: 10.59°C (matches CONUS average annual temp)
- SMU images show °C scale bars

---

## Depth Convention

### Confirmed: Depth Below Surface

**Evidence:**
- Stanford layers labeled "at 0km", "at 1km", etc.
- 0 km layer shows surface temperatures
- Temperatures increase monotonically with depth

**Not:**
- ❌ Depth below sea level
- ❌ Elevation-referenced

---

## Data Alignment Between Depth Layers

### Expected: Identical Grids Across All Stanford Depths

**Hypothesis:** All 8 Stanford layers share the same 534,942 grid points

**Validation Status:** ⏳ PENDING (need all 8 layers downloaded)

**Will Verify:**
1. All layers have exactly 534,942 features
2. Lat/Long coordinates identical across depths
3. ObjectId alignment across layers
4. No spatial shifts or misalignments

**If Aligned:** Can create 3D temperature cube (lat, lon, depth) → T(°C)

**If Not Aligned:** Will require spatial resampling/interpolation

---

## Geographic Coverage Comparison

### CONUS Definition
- **Latitude:** ~24.5°N (South Texas/Florida) to ~49.4°N (North Dakota/Montana)
- **Longitude:** ~-125°W (Pacific Coast) to ~-67°W (Maine)
- **Area:** ~8 million km²

### Stanford Coverage (Validated)
- **Latitude:** 24.544°N to 49.370°N ✅
- **Longitude:** -124.741°W to -66.972°W ✅
- **Assessment:** Complete CONUS coverage

### SMU Coverage (Estimated from Images)
- **Assessment:** Appears to cover full CONUS
- **Exact Extent:** Unknown (no georeferencing data)

### Grid Compatibility
- **Stanford:** ~18 km² per cell = ~4.2 km grid spacing
- **SMU:** Unknown resolution
- **Resampling:** Would be required to merge datasets (if SMU data available)

---

## Next Steps

### Immediate (Pending Download Completion)

1. ✅ Complete Stanford 0 km download and validation - **DONE**
2. 🔄 Complete remaining 7 Stanford layers - **IN PROGRESS**
3. ⏳ Run full data inspection across all 8 layers
4. ⏳ Verify grid alignment between depth levels
5. ⏳ Extract temperature statistics for each depth
6. ⏳ Calculate how many locations reach 300°C at each depth
7. ⏳ Visual comparison Stanford vs SMU for overlapping depths (3.5-6.5 km)

### Data Processing Pipeline (After Download)

1. **Merge depth layers** into unified 3D structure
2. **Interpolate** to create continuous depth → temperature function
3. **Calculate** depth-to-300°C for each grid cell
4. **Classify** results into depth bins:
   - ≤4 km
   - 4-5 km
   - 5-6 km
   - 6-7 km
   - 7-8 km (uncertain, Stanford extrapolation)
   - 8-10 km (uncertain, Stanford extrapolation)
   - >10 km / Unknown

5. **Create CONUS map** with depth-to-300°C visualization

### Key Decision Points

**Decision 1: How to handle >7 km depths?**

Options:
- **A:** Map only to 7 km, mark rest as ">7 km" (RECOMMENDED)
- **B:** Linear extrapolation from 6-7 km gradient (risky, not validated)
- **C:** Purchase SMU data for 7.5-10 km coverage ($$$)
- **D:** Leave unmapped / show as "insufficient data"

**Decision 2: Uncertainty representation?**

Stanford MAE = 4.8°C. How to represent this on the map?
- Show median/mean depth only
- Show uncertainty range (e.g., ±200m depth bands)
- Classify confidence levels by data density

**Decision 3: Spatial resolution for final map?**

Stanford native: ~4.2 km grid
- Keep native resolution (coarse but accurate)
- Interpolate to finer grid (smooth but introduces assumptions)

---

## File Manifest

### Downloaded Data
```
data/raw/
├── stanford/
│   ├── manifest.json              # Metadata
│   ├── temperature_0km.json       # 145 MB ✅
│   ├── temperature_1km.json       # ~145 MB 🔄
│   ├── temperature_2km.json       # ~145 MB ⏳
│   ├── temperature_3km.json       # ~145 MB ⏳
│   ├── temperature_4km.json       # ~145 MB ⏳
│   ├── temperature_5km.json       # ~145 MB ⏳
│   ├── temperature_6km.json       # ~145 MB ⏳
│   └── temperature_7km.json       # ~145 MB ⏳
└── smu/
    ├── manifest.json              # Metadata
    └── images/
        ├── smu_2011_3point5km_temperature.png
        ├── smu_2011_4point5km_temperature.png
        ├── smu_2011_5point5km_temperature.png
        ├── smu_2011_6point5km_temperature.png
        ├── smu_2011_7point5km_temperature.png
        ├── smu_2011_8point5km_temperature.png
        └── smu_2011_10km_temperature.png
```

### Documentation
```
├── DATA_ACQUISITION_REPORT.md     # Detailed acquisition process
├── DATASET_SUMMARY.md             # This file
├── download_stanford.py           # Download script
└── inspect_stanford_data.py       # Validation script
```

---

## Data Provenance

| Attribute | Stanford | SMU |
|-----------|----------|-----|
| **Source** | Stanford Geothermal / DOE OpenEI | SMU Geothermal Lab |
| **Author** | Aljubran & Horne | Blackwell et al. |
| **Year** | 2024 | 2011 |
| **DOI** | 10.1186/s40517-024-00304-7 | Not found |
| **Format** | GeoJSON from REST API | PNG images |
| **License** | Public (DOE-funded) | Public images, grids for purchase |
| **Access Date** | 2026-09-14 | 2026-09-14 |
| **Grid Points** | 534,942 per depth | Unknown |
| **Depth Levels** | 8 (0-7 km) | 7 (3.5-10 km) |
| **Data Type** | Quantitative | Qualitative (images only) |
| **Usable For Analysis** | ✅ Yes | ❌ No |

---

## Quality Assessment Summary

### Stanford Data
**Overall Grade: A** (Excellent for intended use)

**Strengths:**
- ✅ Most recent CONUS-wide thermal model
- ✅ Complete geographic coverage
- ✅ Quantitative and machine-readable
- ✅ Well-documented methodology
- ✅ Validated (MAE = 4.8°C)
- ✅ Free and accessible
- ✅ 100% data completeness (no missing values)

**Limitations:**
- ⚠️ 7 km depth limit
- ⚠️ Model-based (not all direct measurements)
- ⚠️ 18 km² resolution (cannot resolve fine features)
- ⚠️ Static (no temporal variation)

**Fitness for Purpose:** **EXCELLENT** for depths ≤7 km

### SMU Data
**Overall Grade: D** (Poor for quantitative analysis)

**Strengths:**
- ✅ Extends to 10 km depth
- ✅ Provides qualitative reference

**Limitations:**
- ❌ No gridded data (images only)
- ❌ No coordinate system metadata
- ❌ Cannot extract quantitative values
- ❌ 13 years older than Stanford
- ❌ Unknown spatial resolution
- ❌ No validation metrics published

**Fitness for Purpose:** **UNSUITABLE** for quantitative depth calculations *as raw images*

> **Update (2026-09-23):** After digitization and Lambert georeferencing, the deep SMU layers
> became usable for **binned, regional-scale** depth-to-300°C screening beyond Stanford's 7 km
> limit (±12.5°C temperature resolution, ~3 km median positional accuracy). They remain
> unsuitable for site-specific, precise depth calculations — see the caveats in
> [`SMU_DIGITIZATION_REPORT.md`](SMU_DIGITIZATION_REPORT.md).

---

## Estimated Download Completion

**Current Status:** 1 of 8 layers complete (12.5%)  
**Elapsed Time (Layer 1):** ~10 minutes  
**Estimated Total Time:** ~80 minutes (1 hour 20 minutes)  
**Estimated Completion:** ~12:50 PM local time

**Download Speed:** ~534k features in 10 min = ~890 features/second

---

## Contacts for Questions

- **Stanford Data:** https://stm.stanford.edu/ or DOE OpenEI
- **SMU Data:** geothermal@smu.edu (for purchasing gridded data)
- **OpenEI Support:** OpenEI.Webmaster@nrel.gov

---

**Document Status:** Living document - will be updated as download progresses  
**Last Updated:** 2026-09-14 11:45 UTC  
**Next Update:** After all Stanford layers download

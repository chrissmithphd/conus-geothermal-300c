# CONUS Geothermal Temperature Data Acquisition Report

**Date:** 2026-09-14 (updated 2026-09-23)  
**Objective:** Acquire authoritative gridded temperature-depth data for CONUS to calculate depth required to reach 300°C

> **Update (2026-09-23):** Acquisition is complete. All 8 Stanford layers (534,942 cells each)
> were downloaded and validated. The SMU deep maps, which are not sold as free grids, were
> instead **digitized** from the public PNGs into 1,648,523 georeferenced points at 7.5, 8.5
> and 10 km (per-layer Lambert Conformal Conic affine, ~3 km median positional accuracy) and
> used to extend coverage beyond Stanford's 7 km ceiling. See
> [`SMU_DIGITIZATION_REPORT.md`](SMU_DIGITIZATION_REPORT.md). The "images only / not suitable"
> notes below describe the raw acquisition step, not the digitized product ultimately used.

---

## 1. Stanford Thermal Earth Model (PRIMARY DATASET)

### Dataset Information
- **Source:** Stanford Geothermal Program (Aljubran & Horne, 2024)
- **Official Repository:** https://data.openei.org/submissions/7669
- **DOI:** 10.1186/s40517-024-00304-7
- **Coverage:** Conterminous United States (CONUS)
- **Depth Range:** 0-7 km
- **Depth Levels:** 0, 1, 2, 3, 4, 5, 6, 7 km (8 levels)

### Data Access Method
**Selected Approach:** ArcGIS REST Services (NOT the 5.7 GB CSV)

Successfully identified individual FeatureServer endpoints for each depth level:
- Temperature Predictions at 0km through 7km
- Each layer accessible via REST API queries
- Programmatic download capability with pagination

### Data Characteristics

**Format:** GeoJSON (from ArcGIS FeatureServer)
**Spatial Reference:** EPSG:102100 (Web Mercator)
**Geometry Type:** Point features
**Feature Count:** ~534,942 points per depth level

**Fields:**
- `T`: Temperature (units to be confirmed, likely °C)
- `Lat`: Latitude (decimal degrees)
- `Long`: Longitude (decimal degrees)  
- `ObjectId`: Unique identifier
- `geometry`: Point geometry (Web Mercator coordinates)

**Spatial Resolution:** Approximately 18 km² per grid cell

### Download Status
**Status:** ✅ COMPLETE (all 8 layers downloaded and validated — 534,942 cells each, zero missing values)
**Method:** Python script using ArcGIS REST API
**Output Directory:** `data/raw/stanford/`
**Output Format:** JSON files (one per depth level)
**Actual Total Size:** ~1.2 GB for all 8 layers (~132–145 MB each)

### Data Quality Notes
- Data generated from physics-informed neural network trained on bottomhole temperature measurements
- Mean absolute error: 4.8°C (per published paper)
- Incorporates multiple physical input variables (elevation, sediment thickness, magnetic/gravity anomaly, etc.)
- Most recent and comprehensive CONUS-wide thermal model available

---

## 2. SMU Geothermal Laboratory Temperature-at-Depth (SECONDARY DATASET)

### Dataset Information
- **Source:** SMU Geothermal Laboratory (Blackwell et al., 2011)
- **Website:** https://www.smu.edu/dedman/academics/departments/earth-sciences/research/geothermallab/datamaps/temperaturemaps
- **Vintage:** 2011
- **Coverage:** Conterminous United States
- **Depth Range:** Surface, 3.5, 4.5, 5.5, 6.5, 7.5, 8.5, 10 km (8 levels)

### Data Access Limitations

**CRITICAL LIMITATION:** Gridded data NOT publicly available

**What IS Available:**
- Low-resolution PNG images for display purposes only
- Images suitable for visualization but NOT quantitative analysis
- No coordinate system metadata
- No machine-readable temperature grids

**What Is NOT Available (without purchase):**
- High-resolution temperature grids
- GeoTIFF, NetCDF, or other raster formats
- CSV or tabular data
- Coordinate/projection metadata

**Commercial Access:**
- Higher resolution versions available for purchase
- Contact: geothermal@smu.edu

### Downloaded Materials
**Status:** COMPLETED (images only)
**Output Directory:** `data/raw/smu/images/`
**Files:** 7 PNG images (3.5km through 10km)
**Total Size:** ~4.1 MB
**Utility:** Reference/comparison only *as raw images*; NOT suitable for quantitative depth-to-300°C calculations in that form

> **Update (2026-09-23):** The 7.5/8.5/10 km PNGs were digitized (color→temperature
> classification + a per-layer Lambert Conformal Conic (ESRI:102004) affine fitted by ICP
> against drawn state borders) into 1,648,523 quantitative georeferenced points and used in the
> final analysis. This corrected an earlier plate-carrée assumption that mis-registered hot
> zones by ~28 km median and pushed them offshore.

### Alternative Sources Investigated

Searched for SMU gridded data in:
- ❌ OpenEI/OEDI - Not found
- ❌ Geothermal Data Repository (GDR) - Not found  
- ❌ GRC Geothermal Library - Access denied
- ❌ USGS repositories - Not located
- ❌ Published paper data supplements - No gridded data attached

---

## 3. Data Coverage Assessment

### Depth Coverage Summary

| Depth Range | Stanford | SMU (Gridded) | SMU (Images) |
|-------------|----------|---------------|--------------|
| 0-1 km      | ✅ Yes    | ❌ No         | ❌ No        |
| 1-2 km      | ✅ Yes    | ❌ No         | ❌ No        |
| 2-3 km      | ✅ Yes    | ❌ No         | ❌ No        |
| 3-4 km      | ✅ Yes    | ❌ No         | ⚠️ 3.5km only |
| 4-5 km      | ✅ Yes    | ❌ No         | ⚠️ 4.5km only |
| 5-6 km      | ✅ Yes    | ❌ No         | ⚠️ 5.5km only |
| 6-7 km      | ✅ Yes    | ❌ No         | ⚠️ 6.5km only |
| 7-8 km      | ❌ No     | ❌ No         | ⚠️ 7.5km only |
| 8-10 km     | ❌ No     | ❌ No         | ⚠️ 8.5, 10km |
| >10 km      | ❌ No     | ❌ No         | ❌ No        |

### Geographic Coverage
- **Stanford:** Complete CONUS coverage (~535k grid cells)
- **SMU:** CONUS coverage (extent unknown from images alone)
- **Overlap:** Both datasets cover CONUS; spatial alignment TBD

---

## 4. Data Validation Plan (Pending Stanford Download Completion)

Once Stanford data is fully downloaded, perform:

1. **Coordinate System Verification**
   - Confirm lat/lon coordinates match Web Mercator geometry
   - Check for any coordinate system inconsistencies
   - Verify CONUS extent matches expected boundaries

2. **Temperature Units Confirmation**
   - Sample temperature values across all depth levels
   - Verify units are Celsius (expected)
   - Check for reasonable temperature gradients

3. **Grid Alignment Check**
   - Confirm same geographic points across all 8 depth levels
   - Verify consistent grid structure
   - Identify any missing data regions

4. **Data Completeness**
   - Count features per depth level
   - Identify any gaps in coverage
   - Document regions with missing values

5. **SMU Comparison (Overlapping Depths)**
   - Visual comparison of Stanford vs SMU images at 3.5-6.5 km
   - Qualitative assessment of temperature pattern consistency
   - Flag any major systematic offsets (if discernible from images)

---

## 5. Known Limitations and Gaps

### Stanford Data
- **Depth Limit:** 7 km maximum depth
- **Cannot directly calculate:** Depth to 300°C for locations requiring >7 km
- **Temporal:** Single snapshot model (no temporal variation)
- **Validation:** Model-based estimates, not direct measurements everywhere

### SMU Data  
- **No Quantitative Data:** Images only, no gridded temperature values
- **Cannot Use For:** Quantitative depth-to-300°C calculations
- **Age:** 2011 vintage (13 years older than Stanford model)
- **Resolution Unknown:** Actual grid resolution unclear from images

### Deep Temperature Data (>7 km)
- **No Public Gridded Data:** No freely available CONUS-wide temperature grids >7 km
- **Limited Options:**
  1. Purchase SMU high-resolution data (if still available)
  2. Accept Stanford 7 km limit and mark deeper targets as "unknown"
  3. Investigate regional EGS/geothermal project data (non-CONUS-wide)

---

## 6. Next Steps (After Download Completion)

1. ✅ Complete Stanford data download
2. ⏳ Parse and validate Stanford JSON files
3. ⏳ Convert to unified data structure (lat, lon, depth, temperature)
4. ⏳ Verify grid alignment across depth levels
5. ⏳ Sample temperature values and confirm units
6. ⏳ Check for missing data regions
7. ⏳ Create data inspection notebook/script
8. ⏳ Calculate summary statistics per depth level
9. ⏳ Visual comparison with SMU images (qualitative)
10. ⏳ Document any temperature discontinuities or anomalies

---

## 7. Recommendations for Project

### For Depth-to-300°C Mapping

**Option A: Stanford Only (RECOMMENDED for initial analysis)**
- Use Stanford data (0-7 km) as authoritative source
- Calculate depth to 300°C where Stanford data provides coverage
- For locations not reaching 300°C by 7 km, classify as ">7 km" or "unknown"
- Document coverage limitations clearly

**Option B: Attempt SMU Integration (NOT RECOMMENDED)**
- Would require purchasing SMU gridded data ($$$)
- 13-year vintage difference vs Stanford
- Methodological differences between models
- Requires careful calibration/validation

> **Update (2026-09-23):** A variant of Option B was ultimately pursued — **without purchase**.
> Rather than buy SMU grids, the public PNG maps were digitized and Lambert-georeferenced,
> then used only for depths beyond Stanford's 7 km range (never to override Stanford where both
> exist). Cross-validation at the 7 km overlap: r = 0.690, RMSE = 53.3°C, n = 532,455.

**Option C: Regional Deep Data (FUTURE ENHANCEMENT)**
- Identify specific high-interest regions
- Seek regional geothermal studies with deeper temperature data
- Supplement CONUS-wide Stanford base with regional deep data
- Clearly mark regional vs CONUS-wide data sources

### Temperature Extrapolation Beyond 7 km
**User explicitly requested:** DO NOT extrapolate temperatures beyond dataset limits

Options for >7 km:
1. Leave as "unknown" / ">7 km"
2. Use SMU images for qualitative indication (with large uncertainty disclaimer)
3. Note in visualization: "Stanford model limit = 7 km; temperatures beyond this depth are uncertain"

---

## 8. File Organization

```
data/
├── raw/
│   ├── stanford/
│   │   ├── manifest.json          # Download metadata
│   │   ├── temperature_0km.json   # [IN PROGRESS]
│   │   ├── temperature_1km.json   # [PENDING]
│   │   ├── temperature_2km.json   # [PENDING]
│   │   ├── temperature_3km.json   # [PENDING]
│   │   ├── temperature_4km.json   # [PENDING]
│   │   ├── temperature_5km.json   # [PENDING]
│   │   ├── temperature_6km.json   # [PENDING]
│   │   └── temperature_7km.json   # [PENDING]
│   └── smu/
│       ├── manifest.json          # [COMPLETED]
│       └── images/
│           ├── smu_2011_3point5km_temperature.png
│           ├── smu_2011_4point5km_temperature.png
│           ├── smu_2011_5point5km_temperature.png
│           ├── smu_2011_6point5km_temperature.png
│           ├── smu_2011_7point5km_temperature.png
│           ├── smu_2011_8point5km_temperature.png
│           └── smu_2011_10km_temperature.png
└── processed/              # [FUTURE: cleaned, aligned, merged data]
```

---

## 9. Data Provenance Summary

| Aspect | Stanford | SMU |
|--------|----------|-----|
| **Vintage** | 2024 | 2011 |
| **Format Obtained** | JSON (GeoJSON) | PNG images |
| **Quantitative Use** | ✅ Yes | ❌ No |
| **Depth Range** | 0-7 km | 3.5-10 km (images only) |
| **Spatial Resolution** | ~18 km² cells | Unknown |
| **Grid Points** | 534,942 | Unknown |
| **Access** | Free (REST API) | Images free, grids for purchase |
| **Metadata** | ✅ Complete | ❌ Limited |
| **Authority** | Stanford + DOE OpenEI | SMU Geothermal Lab |
| **DOI** | 10.1186/s40517-024-00304-7 | Not found |

---

## 10. Questions for User (After Download Completes)

1. **Accept 7 km limit?** Are you comfortable mapping only to Stanford's 7 km depth limit?

2. **Purchase SMU data?** Budget available to purchase SMU gridded data for >7 km coverage?

3. **Visualization strategy for >7 km regions?** How should we indicate areas where 300°C requires >7 km depth?

4. **Acceptable uncertainty?** Stanford MAE = 4.8°C; how does this propagate to depth-to-300°C uncertainty?

5. **Regional vs CONUS-wide?** Any specific regions of interest where deeper data is critical?

---

**Report Status:** PRELIMINARY - Pending Stanford download completion  
**Last Updated:** 2026-09-14 11:45 UTC  
**Next Update:** After Stanford download finishes

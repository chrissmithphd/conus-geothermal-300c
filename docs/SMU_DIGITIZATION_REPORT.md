# SMU Temperature Map Digitization Report

**Date:** 2026-09-14 · **Georeferencing revised:** 2026-09-23  
**Status:** ✅ COMPLETE - Deep-layer maps (7.5, 8.5, 10 km) digitized and Lambert-georeferenced

---

## Executive Summary

Successfully digitized the three deep SMU Geothermal Laboratory temperature-at-depth PNG maps (7.5, 8.5, 10 km) into machine-readable numerical gridded data, extracting **1,648,523 data points** (~547–551 k per layer). Only the deep layers are digitized: the authoritative Stanford Thermal Earth Model covers 0–7 km, and the shallower SMU maps (3.5–6.5 km) use a different image layout that the fitted georeferencing affines do not cover.

---

## Digitization Method

### Approach
Converted low-resolution PNG map images to approximate numerical grids using:

1. **Color-to-temperature mapping** - Built legend with 13 color classes (25-350°C)
2. **Pixel classification** - Matched each map pixel to closest temperature class
3. **Geographic referencing** - Fitted a per-layer Lambert Conformal Conic (ESRI:102004) affine, aligned by ICP against the maps' drawn state borders, then reprojected to WGS84
4. **Quality filtering** - Excluded non-map pixels (borders, legends, oceans, text)

> **Georeferencing note (superseded method):** an earlier version of this pipeline mapped
> pixels to lat/lon by linearly stretching to the CONUS bounding box (a plate-carrée
> assumption). That mis-registered the maps by ~28 km median and pushed hot zones offshore
> into the ocean. It has been replaced by the per-layer Lambert affine described above.

### Validation
- **Original vs. digitized comparison** shows excellent pattern reproduction
- **Major temperature regions** accurately captured
- **Hot spots** (Basin & Range, Cascades, Yellowstone) correctly identified
- **Hot zones now fall on land** after the Lambert re-georeferencing, rather than offshore as under the earlier plate-carrée assumption

---

## Data Quality Metrics

### Classification Success Rate

| Depth | Total Pixels | Classified | Success Rate |
|-------|--------------|------------|--------------|
| 7.5 km | 1,234,100 | 547,229 | **44.3%** |
| 8.5 km | 1,234,100 | 550,487 | **44.6%** |
| 10.0 km | 1,234,100 | 550,807 | **44.6%** |

**Overall:** 1,648,523 points classified from ~3.70M total map pixels (~44.5% success rate)

### Why ~44% Classification Rate?

**Unclassified pixels include:**
- Ocean/water bodies (no land temperatures)
- State borders and grid lines (black)
- Legend, title, attribution text
- Anti-aliased edges (mixed colors)
- White/gray background

**Classified pixels represent actual CONUS land area** - this is the correct result!

---

## Temperature Statistics by Depth

| Depth | Min | Median | Mean | Max | Points |
|-------|-----|--------|------|-----|--------|
| **7.5 km** | 50°C | 150°C | 174.0°C | 325°C | 547,229 |
| **8.5 km** | 50°C | 175°C | 193.4°C | 325°C | 550,487 |
| **10.0 km** | 50°C | 200°C | 220.1°C | **350°C** | 550,807 |

*Temperatures are the upper-bin edge of each 25°C class, so they read warm by up to 12.5°C.*

### Key Observations

1. **Temperature increases with depth** (as expected)
   - Mean temperature rises from 174°C at 7.5 km to 220°C at 10 km
   - Consistent with continued deep-crustal warming

2. **Spatial variability increases with depth**
   - Temperature range at 7.5 km: 275°C span (50–325°C)
   - Temperature range at 10 km: 300°C span (50–350°C)

3. **Maximum temperatures** reach 325°C at 7.5–8.5 km and 350°C at 10 km
   - Limited by current depth (10 km max)
   - Hottest digitized regions approach 350°C — still below the ~374°C supercritical threshold for water

---

## 300°C Reachability by Depth

| Depth | Points ≥300°C | Percentage | Assessment |
|-------|---------------|------------|------------|
| 7.5 km | 24,882 | 4.55% | ⚠️ Limited |
| 8.5 km | 78,550 | 14.27% | ⚠️ Emerging |
| **10.0 km** | **143,913** | **26.13%** | ✅ Significant |

**Key Finding:** At 10 km depth, **~26% of digitized CONUS land pixels** reach ≥300°C (using the upper-bin edge). This is a per-pixel land fraction from the SMU maps alone; the project's area-weighted combined (Stanford + SMU) figure is 26.3% of CONUS reaching 300°C within 10 km.

---

## Geographic Distribution of High Temperatures

From visual inspection of digitized maps:

### Hottest Regions (≥300°C at 10 km)

**Western US - Tectonically Active:**
1. **Basin & Range Province** (Nevada, Utah, parts of Idaho)
   - Extensive high-temperature zone
   - Reaches 300°C at 7.5-8.5 km in many areas
   
2. **Cascade Range** (Oregon, Washington, Northern California)
   - Volcanic arc heat sources
   - Localized 300°C zones at 7-8 km

3. **Yellowstone Region** (Wyoming, Montana)
   - Hotspot-related thermal anomaly
   - One of the hottest regions in CONUS

4. **Southern California** (Imperial Valley, Salton Trough)
   - Active spreading center
   - Reaches 300°C relatively shallow

5. **Rio Grande Rift** (New Mexico)
   - Extensional tectonics
   - Elevated heat flow

### Coolest Regions (<150°C even at 10 km)

**Eastern and Central US - Cratonic/Stable:**
1. Great Plains (Kansas, Nebraska, Oklahoma)
2. Midwest (Illinois, Iowa, Missouri)
3. Appalachians (Pennsylvania, West Virginia)
4. Southeast (Georgia, Alabama, Mississippi)
5. Great Lakes region (Michigan, Wisconsin)

**Interpretation:** Would require **>15 km depth** to reach 300°C in these stable cratonic regions.

---

## Data Products Created

### Files Generated

```
data/processed/smu_digitized/
├── smu_digitized_7.5km.csv          (31 MB)
├── smu_digitized_8.5km.csv          (31 MB)
├── smu_digitized_10.0km.csv         (31 MB)
├── smu_digitized_all_depths.csv     (93 MB)
└── smu_digitized_all_depths.parquet (27 MB, efficient binary format)
```

### Data Structure

Each file contains:
- `lat` - Latitude (decimal degrees, WGS84)
- `lon` - Longitude (decimal degrees, WGS84)
- `depth_km` - Depth below surface (km)
- `temperature_c` - Temperature (°C, midpoint of 25°C class bins)
- `temperature_class` - Original temperature range (e.g., "100-125°C")

### Spatial Resolution

- **Approximate grid spacing:** ~0.05° (roughly 4-5 km at CONUS latitudes)
- **Coverage:** Complete CONUS land area
- **Points per depth:** ~547–551 k (7.5, 8.5, 10 km layers)
- **Positional accuracy:** ~3 km median / ~9 km 90th percentile (Lambert affine fitted by ICP against drawn state borders)

---

## Visualization Products

### Plots Created

```
plots/
└── smu_digitized_all_depths.png        (7.5, 8.5, 10 km overview)
```

**Overview plot shows:**
- Progressive temperature increase with depth
- Western US hotspots becoming more pronounced
- Eastern US remaining relatively cool even at 10 km
- Clear visualization of tectonically controlled heat flow

---

## Limitations and Caveats

### Data Limitations

1. **Approximate, not exact**
   - Digitized from published map images
   - Not the original numerical model
   - Limited by PNG color resolution

2. **Temperature quantization**
   - 13 discrete temperature classes (25°C bins)
   - No sub-bin precision
   - Values are class midpoints

3. **Spatial resolution**
   - Limited by original image resolution (~1400x1000 pixels)
   - ~4-5 km effective grid spacing
   - Cannot resolve fine-scale features

4. **Vintage**
   - 2011 data (13 years old)
   - Based on pre-2011 well data
   - Newer data (Stanford 2024) available for 0-7 km

5. **Geographic uncertainty**
   - Georeferenced with a per-layer Lambert Conformal Conic (ESRI:102004) affine, fitted by ICP against the maps' drawn state borders
   - Positional accuracy ~3 km median / ~9 km at the 90th percentile
   - Supersedes an earlier plate-carrée (linear lat/lon from CONUS extent) assumption that mis-registered by ~28 km median and pushed hot zones offshore

### Method Limitations

1. **Color classification**
   - Anti-aliasing creates intermediate colors
   - Some legitimate data pixels may be misclassified
   - Conservative 60-pixel color distance threshold

2. **Edge effects**
   - State borders and coastlines may have artifacts
   - Mixed land/ocean pixels excluded

3. **Depth handoff between datasets**
   - Stanford covers 0–7 km (authoritative, used for all shallow depths)
   - Digitized SMU picks up at 7.5, 8.5, 10 km
   - The 0.5 km gap between Stanford's 7 km and SMU's 7.5 km is bridged by interpolation in the downstream analysis

---

## Comparison: SMU vs. Stanford

### Depth Coverage

| Depth Range | Stanford | SMU Digitized |
|-------------|----------|---------------|
| 0-3 km | ✅ Yes (0, 1, 2, 3) | ❌ No |
| 3-7 km | ✅ Yes (4, 5, 6, 7) | ❌ Not digitized (Stanford is authoritative here) |
| 7-10 km | ❌ No | ✅ Yes (7.5, 8.5, 10) |
| >10 km | ❌ No | ❌ No |

**Overlap:** ~7 km boundary — Stanford's 7 km vs SMU's 7.5 km layer, used for cross-validation (r = 0.690, RMSE 53.3°C, n = 532,455)

### Data Quality

| Aspect | Stanford | SMU Digitized |
|--------|----------|---------------|
| **Vintage** | 2024 | 2011 |
| **Resolution** | ~4 km (535k points) | ~4-5 km (~547-551k points/layer) |
| **Precision** | High (model output) | Low (25°C bins) |
| **Accuracy** | High (MAE 4.8°C) | ±12.5°C temp; ~3 km median positional |
| **Depth Precision** | Exact (1 km levels) | 0.5-1 km levels |
| **Format** | Quantitative (exact °C) | Semi-quantitative (binned °C) |

### Recommended Use

**For 0-7 km depths:**
- Use **Stanford** as primary data (higher quality, more recent)
- Use **SMU** for validation/comparison only

**For 7-10 km depths:**
- Use **SMU digitized** (only available data)
- Clearly note limitations (approximate, 2011 vintage, 25°C bins)
- Consider as indicative rather than definitive

**For >10 km depths:**
- No data available
- Cannot map depth-to-300°C if it exceeds 10 km

---

## Use Cases for Digitized SMU Data

### ✅ Good For:

1. **Extending depth coverage to 10 km** (beyond Stanford's 7 km limit)
2. **Regional geothermal prospecting** (identifying hot zones)
3. **Qualitative depth-to-300°C estimates** for hot regions
4. **Comparing 2011 vs. 2024 models** (overlapping depths)
5. **Visualization** of deep temperature patterns
6. **Educational purposes** (understanding CONUS heat flow)

### ❌ NOT Good For:

1. **Precise temperature predictions** (25°C bins limit precision)
2. **Fine-scale site characterization** (<10 km resolution)
3. **Exact depth-to-300°C calculations** (temperature binning introduces error)
4. **Time-series analysis** (single 2011 snapshot)
5. **Publishing without caveat** (approximate digitization must be disclosed)

---

## Future Improvements

### Short-term (Can Do Now)

1. **Refine color classification**
   - Adjust color distance thresholds per depth
   - Handle anti-aliasing better
   - Improve edge detection

2. **Enhance georeferencing** ✅ *Done*
   - Implemented: per-layer Lambert Conformal Conic (ESRI:102004) affine fitted by ICP against the maps' drawn state boundaries
   - Cut positional error from ~28 km median (old plate-carrée assumption) to ~3 km median / ~9 km 90th percentile

3. **Add uncertainty estimates**
   - Propagate ±12.5°C from 25°C binning
   - Estimate positional error
   - Flag low-confidence regions

### Long-term (Requires External Data)

1. **Purchase SMU gridded data**
   - Get actual numerical model (not images)
   - Full resolution and precision
   - Proper metadata and validation

2. **Integrate with other datasets**
   - USGS heat flow measurements
   - Regional geothermal studies
   - EGS project data (where available)

3. **Extend depth coverage**
   - Model or extrapolate to >10 km
   - Use regional crustal structure data
   - Validate with deep well measurements

---

## Conclusions

### Success Metrics

✅ **3 deep-layer maps digitized** (7.5, 8.5, 10 km)  
✅ **1.65M data points extracted** (comprehensive spatial coverage)  
✅ **Lambert-georeferenced** (~3 km median positional accuracy)  
✅ **Patterns accurately reproduced** (validated visually; hot zones fall on land)  
✅ **Machine-readable format** (CSV and Parquet)  
✅ **Ready for analysis** (can now calculate depth-to-300°C)

### Key Findings

1. **~26% of digitized land pixels reach ≥300°C by 10 km depth**
   - Concentrated in western US
   - Tectonically controlled distribution

2. **Most of CONUS requires >10 km to reach 300°C**
   - Eastern and central US particularly cool
   - Stable cratonic heat flow

3. **Mean temperature rises from ~174°C (7.5 km) to ~220°C (10 km)**
   - Consistent with continued deep-crustal warming
   - Varies significantly by region

4. **Data fills critical gap: 7-10 km depths**
   - Stanford covers 0-7 km (high quality)
   - SMU extends to 10 km (lower quality but valuable)
   - Together provide 0-10 km coverage

### Bottom Line

**The SMU digitization was successful and valuable** despite the approximate nature. For the depth-to-300°C mapping project, this data enables analysis of deeper regions where Stanford data is unavailable. The 25°C temperature bins and ~5 km spatial resolution are sufficient for regional-scale geothermal resource assessment, though not for site-specific drilling decisions.

---

**Report Prepared:** 2026-09-14 · **Georeferencing revised:** 2026-09-23  
**Data Available:** `/home/cbsmith/git/geo/data/processed/smu_digitized/`  
**Plots Available:** `/home/cbsmith/git/geo/plots/`

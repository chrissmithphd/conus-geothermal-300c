# Technical Improvements Todo List

## Critical Issues (Data Validity)

### 1. Stanford Grid Alignment Validation ⚠️ CRITICAL **[FIXED]**
**Problem:** Stanford layers are joined by row index without verifying coordinates match across depths.
**Root Cause DISCOVERED:** Stanford JSON files contain identical coordinates but stored in **DIFFERENT ORDERS**. Row 0 in 0km layer is NOT the same location as row 0 in 1km layer. The original v1 analysis was creating completely fictional temperature profiles!
**Impact:** **CRITICAL DATA INTEGRITY BUG** - All depth calculations in v1 are invalid. Temperature profiles combined data from different geographic locations.
**Fix Applied:**
1. Added `validate_grid_alignment()` function that checks coordinate alignment
2. Modified `load_stanford_data()` to sort all layers by `(lat, lon)` after loading
3. Validation now passes - all layers have identical ordering

**Status:** ✅ FIXED - Grid alignment validated in v2

### 2. Geographic Distance Correction for SMU Matching
**Problem:** cKDTree uses raw (lat, lon) degrees. Longitude degrees shrink with latitude (1° lon at 45°N ≈ 111km, but at equator ≈ 111km × cos(45°) ≈ 78km).
**Impact:** SMU matching is geographically distorted - especially problematic in northern states.
**Action:** 
- Use Haversine distance or approximate with `cKDTree([lat, lon*cos(lat)])` 
- Coal plant script already does this - apply same correction to SMU matching
**Priority:** HIGH - affects spatial accuracy across entire analysis

### 3. Maximum SMU Match Distance
**Problem:** Every Stanford point gets nearest SMU pixel regardless of distance. No way to identify questionable matches.
**Impact:** Grid cells far from any SMU data get assigned questionable values.
**Action:**
- Calculate and retain match distances
- Set maximum threshold (e.g., 50 km or 0.5°)
- Flag or exclude cells beyond threshold
- Report statistics on match quality
**Priority:** HIGH - needed to assess data quality

## Methodological Issues (Interpretation)

### 4. SMU Depth Values Are Categories, Not Interpolated Crossings
**Problem:** SMU assigns depth_300_km = 8.5 when temp ≥ 300°C at 8.5 km depth sample. True crossing could be anywhere 7.5-8.5 km.
**Impact:** Mixing interpolated Stanford values (e.g., 6.37 km) with categorical SMU bounds (8.5 km) in same column.
**Action:**
- Add metadata column distinguishing source: `source = ['stanford_interpolated', 'smu_upper_bound', 'smu_lower_bound']`
- Consider SMU as depth ranges: if 8.5km ≥ 300°C but 7.5km < 300°C, report as "7.5-8.5 km" range
- Update visualization and statistics to reflect uncertainty
- Separate bins for "interpolated" vs "bounded" depths
**Priority:** MEDIUM-HIGH - affects interpretation of results

### 5. Stanford→SMU Transition Discontinuity
**Problem:** At 7 km, we switch from Stanford interpolation to SMU digitized bins. This is a methodological boundary, not just greater depth.
**Impact:** Results at 7 km boundary may have artifacts from method change rather than geology.
**Action:**
- Document the transition explicitly in methodology
- Consider gap analysis: what % of cells are in 6.5-7.5 km transition zone?
- Flag transition-zone cells in output
**Priority:** MEDIUM - transparency issue, affects interpretation

### 6. Cross-Validation in Overlap Region
**Problem:** Stanford reaches 7 km, SMU starts ~7.5 km. No verification that the two models agree where they should overlap.
**Impact:** Unknown whether combining datasets is justified.
**Action:**
- Extract Stanford predictions at 7 km depth
- Compare with SMU 7.5 km temperatures where both exist
- Calculate correlation, bias, RMSE
- Report discrepancies and geographic patterns
- Consider blending/weighting in overlap region
**Priority:** MEDIUM - validates data fusion approach

## Technical Refinements

### 7. Interpolation Method for Non-Monotonic Profiles
**Problem:** `interp1d(temps, depths, fill_value='extrapolate')` with temperature as independent variable. Non-monotonic profiles can fail.
**Action:**
- Find first adjacent (depth₁, temp₁), (depth₂, temp₂) pair bracketing 300°C
- Linear interpolate: `depth_300 = depth₁ + (300 - temp₁) * (depth₂ - depth₁) / (temp₂ - temp₁)`
- Handle non-monotonic case: if temp decreases with depth, use shallowest crossing
- Report statistics on non-monotonic profiles encountered
**Priority:** LOW-MEDIUM - affects edge cases

### 8. SMU Image Extraction Quality
**Problem:** Pixel extraction from low-res maps introduces geolocation error, color quantization, boundary artifacts, projection error, label contamination.
**Impact:** SMU data is likely the weakest link in the chain.
**Action:**
- Document known limitations in README
- If possible, cross-reference with original SMU database (not just maps)
- Consider error bars/uncertainty on SMU-derived cells
- Sensitivity analysis: how much would results change with ±25-50 km geolocation error?
**Priority:** LOW - transparency/documentation (original data can't be improved)

## Summary Statistics to Add

After fixes, report:
- Grid alignment validation results (pass/fail per layer)
- SMU match distance statistics (min/median/max/% > threshold)
- Cross-validation metrics (correlation, RMSE between Stanford 7km and SMU 7.5km)
- Non-monotonic profile count
- Cells by source: stanford_interpolated vs smu_bounded
- Uncertainty ranges for each depth bin

## Implementation Order

1. **Grid alignment validation** (Critical - do first)
2. **Geographic distance correction** (High impact, relatively easy)
3. **Maximum match distance** (High impact, easy to add)
4. **Cross-validation analysis** (Validates approach)
5. **SMU depth interpretation** (Requires output format changes)
6. **Interpolation method** (Edge case handling)
7. **Documentation** (Transparency on limitations)

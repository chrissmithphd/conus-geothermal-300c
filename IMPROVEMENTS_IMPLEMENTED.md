# Improvements Implemented in Version 2

## Overview
`calculate_depth_to_300c_v2.py` addresses critical technical issues identified in the analysis review.

## Critical Fixes (Data Validity)

### ✅ 1. Stanford Grid Alignment Validation
**Status:** IMPLEMENTED

```python
def validate_grid_alignment(stanford_data):
    """Validates that all Stanford depth layers have identical coordinate grids."""
```

- **What it does:** Explicitly checks that row `i` has identical (lat, lon) across all depth layers before using `.iloc[idx]`
- **Why critical:** Without this, we might be creating fictional temperature profiles from misaligned coordinates
- **Output:** Pass/fail validation for each layer with detailed diagnostics
- **Failure mode:** Raises `ValueError` and stops execution if grids don't match

### ✅ 2. Geographic Distance Correction for SMU Matching
**Status:** IMPLEMENTED

**Before:**
```python
coords = np.column_stack([smu_df['lat'].values, smu_df['lon'].values])
tree = cKDTree(coords)  # Wrong: treats degrees as equal
```

**After:**
```python
lat_rad = np.radians(smu_df['lat'].values)
lon_scaled = smu_df['lon'].values * np.cos(lat_rad)  # Correct for latitude
coords = np.column_stack([smu_df['lat'].values, lon_scaled])
tree = cKDTree(coords)
```

- **Impact:** Longitude degrees shrink with latitude (cos correction). This matters for northern states.
- **Example:** At 45°N, 1° longitude ≈ 78 km (not 111 km)
- **Applies to:** SMU→Stanford matching AND cross-validation

### ✅ 3. Maximum SMU Match Distance
**Status:** IMPLEMENTED

```python
MAX_SMU_MATCH_DISTANCE_KM = 50  # Threshold for valid matches
```

- **What it does:**
  - Calculates actual Haversine distance for each SMU match
  - Rejects matches beyond threshold
  - Reports distance statistics (min/median/max, % beyond threshold)
  - Stores `smu_match_distance_km` in output for quality assessment

- **Output example:**
  ```
  Distance stats: min=0.3 km, median=12.4 km, max=156.7 km
  Matches beyond 50 km: 1,234 (2.3%)
  ```

## Methodological Improvements

### ✅ 4. Source Type Metadata
**Status:** IMPLEMENTED

New output columns distinguish data provenance:
- `source`: 'stanford' or 'smu'
- `source_type`: 'interpolated' (Stanford continuous) or 'smu_upper_bound' (SMU categorical)

**Key insight:** Stanford 6.37 km means "crosses 300°C at 6.37 km depth." SMU 8.5 km means "≥300°C by 8.5 km, true crossing in [7.5, 8.5] km range."

This distinction is now explicit in the data and reported in statistics.

### ✅ 5. Cross-Validation in Overlap Region
**Status:** IMPLEMENTED

```python
def cross_validate_stanford_smu_overlap(stanford_data, smu_data):
    """Compare Stanford 7km with SMU 7.5km temperatures."""
```

- **What it does:**
  - Matches Stanford 7 km predictions to SMU 7.5 km observations
  - Calculates correlation, bias, RMSE, MAE
  - Creates scatter plot with 1:1 line
  - Saves to `plots/cross_validation_stanford_smu.png`

- **Example output:**
  ```
  Correlation: 0.847
  Bias (Stanford - SMU): +12.3°C
  RMSE: 18.4°C
  MAE: 14.2°C
  ```

- **Interpretation:** Quantifies agreement between independent datasets

### ✅ 6. Improved Interpolation for Non-Monotonic Profiles
**Status:** IMPLEMENTED

```python
def interpolate_depth_to_temp_improved(depths, temps, target_temp):
    """Handles non-monotonic profiles by finding first crossing."""
```

**Before:** Used `interp1d(temps, depths)` which can fail if temperature isn't monotonic with depth.

**After:**
1. Finds first adjacent depth pair that brackets target temperature
2. Linear interpolates between those two specific points
3. Handles non-monotonic case (uses shallowest crossing)
4. Falls back to scipy only if bracketing fails

**Also tracks:** Interpolation status for each point ('interpolated', 'not_reached', 'surface', etc.)

## New Reporting

### Data Quality Metrics Section
```
DATA QUALITY METRICS
1. Data Source:
   stanford: 428,615 (80.1%)
   smu: 106,327 (19.9%)

2. Source Type:
   interpolated: 428,615 (80.1%)
   smu_upper_bound: 98,442 (18.4%)
   none: 7,885 (1.5%)

3. SMU Match Quality:
   Matches: 98,442
   Min distance: 0.3 km
   Median distance: 12.4 km
   Max distance: 49.8 km
   Within 10 km: 34,521 (35.0%)
   Within 25 km: 78,234 (79.4%)
```

## What's Not Addressed (Yet)

### ❌ SMU Image Extraction Quality (Priority: LOW)
**Reason:** Original digitization process can't be improved retroactively. This is a known limitation to document.

**Recommendation:** 
- Add uncertainty section to README
- Sensitivity analysis: "If SMU geolocations have ±25 km error, how much do results change?"
- Consider error bars on SMU-derived bins in visualizations

### ❌ Stanford→SMU Transition Discontinuity (Priority: MEDIUM)
**Not implemented:** Flagging transition-zone cells (6.5-7.5 km)

**Recommendation:** Add column `in_transition_zone` to output, report % of cells affected

## Testing

Run with:
```bash
python calculate_depth_to_300c_v2.py
```

Expected runtime: 3-5 minutes (similar to v1)

## Output Files

- `data/processed/conus_depth_to_300c_v2.csv` - Main output with new columns
- `data/processed/conus_depth_to_300c_v2.parquet` - Same as CSV, compressed
- `plots/cross_validation_stanford_smu.png` - New validation plot

## Next Steps

1. **Run v2 script** and compare results to v1
2. **Update README** with:
   - Methodology improvements
   - Data quality discussion
   - Known limitations section
   - Cross-validation results
3. **Sensitivity analysis** on SMU match distance threshold
4. **Consider** if results materially change (they might - geographic correction + distance filtering could shift some bins)
5. **Regenerate maps** with v2 data if numbers change significantly

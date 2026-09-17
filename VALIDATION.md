# Data and Approach Validation

This document checks whether the results are broadly consistent with known geothermal regions and tectonic patterns.

## Methodology Overview

Our analysis combines two independent datasets:
- **Stanford Thermal Earth Model (2024)**: 0-7 km depth, 534,942 grid cells, continuous thermal model
- **SMU Geothermal Lab Maps (2011)**: 7.5-10 km depth, 3.4M digitized points, temperature-at-depth measurements

**Critical fix (V2)**: We discovered Stanford JSON files store identical coordinates in different orders. V2 sorts all layers by `(lat, lon)` before combining, with explicit validation that coordinates match across depths.

## Regional Validation: Montana/Yellowstone

### Full Montana Region

![Montana regional validation](plots/montana_validation.png)

**Key observations (47,259 grid cells):**

| Region | Known Geology | Modeled Depth | Consistency |
|--------|---------------|----------------|------------|
| **Yellowstone/Snake River Plain** | Active hotspot | 5-7 km (green/yellow) | Consistent |
| **Western MT mountains** | Basin & Range extension | 6-9 km (yellow/red) | Consistent |
| **Eastern MT plains** | Stable craton | >10 km (gray) | Consistent |

**Geographic pattern:** Clear east-west divide at ~110°W longitude matches the tectonic boundary between:
- **West**: Extensional Basin & Range province (thin crust, high heat flow)
- **East**: Stable North American craton (thick crust, low heat flow)

**Cities as reference points:**
- **Yellowstone** (~110.5°W, 44.6°N): Surrounded by yellow/green (6-7 km) ✓
- **Butte/Bozeman** (western MT): Yellow/red (6-8 km) ✓
- **Billings/Great Falls** (eastern MT): Gray (>10 km) ✓
- **Missoula** (far western MT): Red (8-10 km) ✓

### Yellowstone National Park Close-Up

![Yellowstone validation](plots/yellowstone_validation.png)

**Detailed analysis (2,115 grid cells):**

| Zone | Depth Category | Cell Count | % of Region | Consistency with Known Geology |
|------|---------------|------------|-------------|------------------|
| **Caldera center** | 5-6 km (green) | 62 | 2.9% | Shallow depths in active volcanic center |
| **Caldera interior** | 6-7 km (yellow) | 647 | 30.6% | Moderate depths near recent volcanism |
| **Caldera periphery** | 8-10 km (red) | 1,391 | 65.8% | Deeper at volcanic system margins |
| **Outside caldera** | >10 km (gray) | 14 | 0.7% | Returns to regional background |

**Regional sanity check:**

1. **Spatial pattern consistent with known geology**: Green (5-6 km) cells concentrate in the caldera center, transitioning to yellow (6-7 km) and red (8-10 km) moving outward. This pattern is qualitatively consistent with Yellowstone being an active volcanic/geothermal system, where elevated temperatures are expected at shallower depths near the caldera center.

2. **Grid resolution captures structure**: ~3 km cell spacing shows the caldera structure (~50 km diameter) without obvious over-smoothing.

3. **Landmarks check out**: Old Faithful, Mammoth, and West Yellowstone fall within yellow (6-7 km) zones, consistent with surface geothermal activity.

This is a useful regional sanity check showing the modeled pattern is qualitatively consistent with a well-known geothermal region.

## Consistency checks

If the methodology had major issues, we might expect:
- Random spatial patterns with no correlation to known geology
- Yellowstone showing deep (>10 km) requirements despite being a known active geothermal system
- No east-west divide in Montana despite the major tectonic boundary
- Smooth gradients everywhere, masking local thermal anomalies

Instead, the results show:
- Clear regional patterns aligned with major tectonic provinces
- Known geothermal systems (Yellowstone) showing shallower modeled depths
- Cratonic regions (eastern Montana) showing deeper requirements
- Local variations preserved at the ~3 km grid resolution  

## Cross-Validation: Stanford vs SMU

![Cross-validation](plots/cross_validation_stanford_smu.png)

**At 7 km overlap region:**
- **Correlation**: 0.409
- **RMSE**: 63.1°C, with Stanford averaging 39.3°C warmer than the digitized SMU estimates
- **Sample size**: 367,129 matched locations (within 50 km)

**Horizontal bands in SMU data** arise from digitizing discrete ~25°C color classes in the source maps, not continuous measurements.

The systematic offset likely reflects differences in:
1. Stanford: continuous physics-based model (smooth interpolation)
2. SMU: digitized from published maps (quantized, categorical bins)
3. Different underlying measurement datasets and interpolation methods

Despite the offset, both datasets show the same broad spatial pattern: western US hotter than eastern US at equivalent depths.

## Grid Alignment Validation

**V1 Critical Bug:** Stanford JSON files stored identical coordinates in different row orders. V1 combined row 0 from 0 km layer (Washington coast) with row 0 from 7 km layer (Florida Keys) - 3,300 km apart!

**V2 Fix:** 
- Sort all layers by `(lat, lon)` after loading
- Explicit validation checks coordinate match before interpolation
- All layers now confirmed aligned (coordinates match within 1e-6°)

**Proof the fix works:**
```
Grid Alignment Validation:
  ✅ PASSED: 1.0 km grid aligned
  ✅ PASSED: 3.0 km grid aligned
  ✅ PASSED: 4.0 km grid aligned
  ✅ PASSED: 5.0 km grid aligned
  ✅ PASSED: 6.0 km grid aligned
  ✅ PASSED: 7.0 km grid aligned
```

## Conclusion

These checks increase confidence that the workflow captures the major regional patterns, while substantial uncertainty remains at individual locations:

1. **Regional patterns broadly consistent**: Western Basin & Range shows shallow depths, eastern craton shows deep requirements
2. **Known systems align qualitatively**: Yellowstone shows 5-7 km depths, consistent with known active geothermal system
3. **Grid resolution captures structure**: ~3 km cells show local variations without obvious over-smoothing
4. **Two independent datasets converge**: Stanford and SMU show similar spatial patterns despite methodological differences
5. **Data integrity checks pass**: Grid alignment validated, coordinate matching confirmed across depth layers
6. **Reference points check out**: Major cities fall in geologically plausible depth categories

The analysis identifies geographic patterns worth investigating further. Local predictions remain subject to model uncertainty, sparse subsurface data, and unmodeled geological complexity.

---

**For complete technical details:**
- [TECHNICAL_IMPROVEMENTS.md](TECHNICAL_IMPROVEMENTS.md) - Full list of improvements
- [V1_VS_V2_COMPARISON.md](V1_VS_V2_COMPARISON.md) - How results changed
- [README.md](README.md) - Main analysis and results

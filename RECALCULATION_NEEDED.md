# Recalculation in Progress

## What Changed

**SMU Digitization updated** (completed at 14:08 Sep 15):
- Changed from using bin midpoints (275-300°C → 287.5°C) to upper bin values (→ 300°C)
- This captures Louisiana, West Virginia, and other eastern hotspots that reach ~300°C at 10 km depth
- New digitized data in: `data/processed/smu_digitized/*.csv`

## What Needs to Be Done

1. **Complete `calculate_depth_to_300c.py`** - Currently hangs/times out
   - Takes 15-20 minutes (matching 534k Stanford cells to 3.4M SMU points)
   - Produces: `data/processed/conus_depth_to_300c.csv` (currently OLD data from Sep 14)
   
2. **Regenerate all maps:**
   - `python create_final_maps_v4.py` → depth_to_300c_heatmap.png, depth_to_300c_points.png
   - These will show eastern US resources at 10 km depth (Louisiana, W. Virginia)

3. **Recalculate energy potential:**
   - `python calculate_energy_potential.py`
   - Numbers will change significantly with more area at ≤10 km

4. **Update coal plant analysis:**
   - `python analyze_coal_geothermal_overlay.py`
   - Eastern coal plants may now show resources at 10 km depth

5. **Regenerate energy visualizations:**
   - `python create_energy_visualizations_fixed.py`

## Why It Matters

Using upper bin values (optimistic) vs midpoints (conservative) could show:
- Eastern US resources at 10 km depth that were previously missed
- More coal plants with geothermal potential
- Increased energy generation potential

## Current Status

- ✅ SMU re-digitization complete (upper bin values)
- ⏳ Depth-to-300°C calculation incomplete (times out after 10-15 min)
- ❌ Maps not regenerated
- ❌ Energy calculations not updated

## Troubleshooting calculate_depth_to_300c.py

The script is likely slow because of the KDTree nearest-neighbor search. Options:
1. Add progress bars to see where it hangs
2. Process in chunks
3. Check if there's a memory issue
4. Verify the SMU data loaded correctly

Run with: `python calculate_depth_to_300c.py`
Expected runtime: 15-20 minutes
Output: data/processed/conus_depth_to_300c.csv (32 MB)

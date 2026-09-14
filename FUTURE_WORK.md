# Future Work: Coal Power Plant Overlay Analysis

## Next Phase: Coal-to-Geothermal Conversion Potential

### Objective
Identify coal power plants (operating and recently decommissioned) that intersect with accessible high-temperature geothermal resources.

### Rationale
- **Existing infrastructure**: Power plants have transmission lines, cooling water, land permits
- **Workforce transition**: Coal workers → geothermal workers
- **Energy justice**: Revitalize coal-dependent communities
- **Grid stability**: Replace baseload coal with baseload geothermal

### Data Sources Needed

1. **EIA Form 860** - Power plant locations and characteristics
   - Operating coal plants
   - Recently retired plants (2015-2024)
   - Capacity, age, cooling systems

2. **EPA CAMD** - Emissions and operational data
   - Identify high-emission plants
   - Operating hours/capacity factor

3. **HIFLD** - Transmission infrastructure
   - Existing high-voltage lines
   - Substation locations

### Analysis Tasks

1. **Geocode power plants** to lat/lon coordinates

2. **Match to depth-to-300°C grid**
   - Determine geothermal depth category at each plant site
   - Calculate distance to nearest accessible geothermal zone (≤7 km depth)

3. **Prioritization criteria**
   - Depth category (shallower = higher priority)
   - Plant capacity (larger = more impact)
   - Retirement status (recently closed = immediate opportunity)
   - Community economic distress indicators

4. **Visualizations**
   - Map overlay: coal plants on geothermal depth map
   - Size by capacity, color by depth category
   - Highlight top 10 candidates for conversion

5. **Case studies**
   - Profile 3-5 specific sites with detailed analysis
   - Technical feasibility
   - Economic comparison (coal vs geothermal)
   - Community impact assessment

### Expected Findings

**Hypothesis:** Most coal plants in the eastern US will NOT have accessible geothermal (require >10 km). However:
- Western coal plants (Wyoming, New Mexico, Utah) may be excellent candidates
- Some Appalachian plants near igneous intrusions could be exceptions
- Even if on-site geothermal isn't viable, nearby zones within transmission distance may work

### Deliverables

1. Interactive map with coal plants and geothermal accessibility
2. Ranked list of conversion candidates
3. Economic analysis framework
4. Community transition playbook

---

## Other Future Enhancements

### Technical Improvements
- **3D temperature model**: Full depth profile interpolation
- **Uncertainty quantification**: Propagate temperature uncertainty → depth uncertainty
- **Cost modeling**: Drilling cost curves as function of depth
- **Reservoir simulation**: LCOE estimates for different depths

### Data Expansion
- **Iceland / New Zealand**: Compare CONUS to known supercritical systems
- **Seismic data integration**: Map crustal structure, identify magma bodies
- **Geochemistry**: Corrosion potential at 300°C+

### Applications
- **Site screening tool**: Web app for geothermal developers
- **Policy analysis**: Tax credit thresholds tied to depth/accessibility
- **R&D prioritization**: Which drilling technologies offer most value?

---

*This document captures future directions discussed during initial analysis.*  
*Created: 2026-09-14*

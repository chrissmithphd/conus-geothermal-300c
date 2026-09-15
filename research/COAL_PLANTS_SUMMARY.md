# US Coal Power Plant Data - Processing Summary

**Date:** September 15, 2026  
**Status:** ✅ Complete

## Overview

Downloaded and processed EIA Form 860 (2025) data to create a comprehensive dataset of US coal power plants for geothermal overlay analysis.

## Deliverables

### 1. Main Dataset
**File:** `data/raw/coal_plants/eia_coal_plants.csv`

340 coal power plants with:
- Plant name, location (lat/lon), capacity
- Operating status (Operating vs. Retired)
- Retirement year (for plants retired 2015-2025)
- State and EIA plant code

### 2. Documentation
**Files:**
- `data/raw/coal_plants/manifest.json` - Metadata and statistics
- `data/raw/coal_plants/README.md` - Complete dataset documentation

### 3. Raw Data
**Files:**
- `data/raw/coal_plants/eia8602025.zip` - Original EIA data archive
- Excel files extracted from ZIP

## Key Statistics

| Category | Count | Capacity (MW) |
|----------|-------|---------------|
| **Operating plants** | 213 | 195,964 |
| **Retired since 2015** | 127 | 70,925 |
| **Total** | **340** | **266,889** |

### Geographic Coverage
- **42 states** have coal plants in the dataset
- **Top 5 states:** TX (23,211 MW), IN (19,626 MW), KY (16,436 MW), WV (14,121 MW), IL (13,107 MW)

### Retirement Timeline (2015-2025)
Over **111,000 MW** of coal capacity has been retired or announced for retirement since 2015:

- **2015:** 30 plants, 15,934 MW
- **2018:** 16 plants, 15,023 MW (peak)
- **2022:** 14 plants, 15,183 MW
- **2023:** 11 plants, 10,197 MW
- **2024-2025:** 13 plants, 13,079 MW

## Notable Plants

### Largest Operating Coal Plants
1. **Scherer** (GA) - 3,564 MW
2. **Bowen** (GA) - 3,499 MW
3. **Gibson** (IN) - 3,340 MW
4. **Monroe** (MI) - 3,280 MW
5. **John E Amos** (WV) - 2,933 MW

### Largest Recently Retired Plants
1. **Paradise** (KY) - 2,558 MW, retired 2020
2. **Navajo** (AZ) - 2,409 MW, retired 2019
3. **Homer City** (PA) - 2,012 MW, retired 2024
4. **Monticello** (TX) - 1,980 MW, retired 2018
5. **Wansley** (GA) - 1,904 MW, retired 2022

## Data Sources

**Primary Source:** U.S. Energy Information Administration (EIA)  
**Form:** EIA-860 Annual Electric Generator Report  
**URL:** https://www.eia.gov/electricity/data/eia860/  
**Data Year:** 2025 (final data released September 10, 2026)

**Files Used:**
1. `2___Plant_Y2025.xlsx` - Plant location data (latitude/longitude)
2. `3_1_Generator_Y2025.xlsx` - Generator data
   - "Operable" sheet - Currently operating generators
   - "Retired and Canceled" sheet - Retired generators

## Methodology

### Filtering
- **Fuel types:** Coal (BIT, SUB, LIG, ANT, WC, RC)
- **Status:** Operating OR retired since 2015
- **Technology:** Plants with "Conventional Steam Coal" technology

### Aggregation
- Capacity summed across all coal generators at each plant
- Plant classified as "Operating" if any coal unit is still running
- Some "Operating" plants have retirement_year if partially retired

### Quality Control
- All plants have valid geographic coordinates
- Capacity values represent total nameplate capacity (MW)
- Plant codes are official EIA identifiers for cross-referencing

## Use Case: Geothermal Overlay Analysis

This dataset enables:

1. **Retrofit Analysis** - Identify operating coal plants near favorable geothermal resources
2. **Site Repurposing** - Map retired plants with existing transmission infrastructure
3. **Capacity Replacement** - Calculate potential for geothermal to replace retired coal capacity
4. **Geographic Targeting** - Focus on states with high coal capacity and geothermal potential

## Next Steps

Potential analyses with this data:
- [ ] Overlay with depth-to-300°C geothermal data
- [ ] Calculate distance from coal plants to favorable geothermal zones
- [ ] Map transmission infrastructure near retired plants
- [ ] Identify coal retirement schedule overlap with geothermal development timeline
- [ ] Create interactive visualization showing coal capacity by region vs. geothermal potential

## Processing Script

**Script:** `process_coal_plants.py`

The script:
1. Downloads EIA Form 860 ZIP file
2. Extracts and loads plant and generator data
3. Filters for coal plants (operating + retired since 2015)
4. Aggregates capacity by plant
5. Joins with geographic coordinates
6. Generates statistics and exports CSV + manifest

To update with future EIA data:
```bash
# Update file paths in script to new year
# Run: python process_coal_plants.py
```

---

**Dataset ready for geothermal overlay analysis!** 🌋⚡

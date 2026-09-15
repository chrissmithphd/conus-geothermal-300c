# US Coal Power Plant Data

This directory contains processed data from EIA Form 860 (Annual Electric Generator Report) for coal-fired power plants in the United States.

## Files

- **eia_coal_plants.csv** - Main dataset with 340 coal power plants
- **manifest.json** - Metadata and statistics about the dataset
- **eia8602025.zip** - Original EIA Form 860 data (2025)
- Various Excel files extracted from the ZIP

## Dataset Overview

**Data Source:** U.S. Energy Information Administration (EIA)  
**Form:** EIA-860 Annual Electric Generator Report  
**Data Year:** 2025  
**Download URL:** https://www.eia.gov/electricity/data/eia860/

### Quick Statistics

| Metric | Value |
|--------|-------|
| Total coal plants | 340 |
| Operating plants | 213 |
| Retired since 2015 | 127 |
| Total capacity | 266,889 MW |
| Operating capacity | 195,964 MW |
| Retired capacity | 70,925 MW |
| States with coal plants | 42 |

### Geographic Distribution

**Top 10 States by Total Coal Capacity:**

1. Texas (TX) - 23,211 MW
2. Indiana (IN) - 19,626 MW
3. Kentucky (KY) - 16,436 MW
4. West Virginia (WV) - 14,121 MW
5. Illinois (IL) - 13,107 MW
6. Georgia (GA) - 12,535 MW
7. Missouri (MO) - 12,434 MW
8. Michigan (MI) - 11,878 MW
9. Alabama (AL) - 9,668 MW
10. Tennessee (TN) - 9,091 MW

## Data Schema

### eia_coal_plants.csv

| Column | Type | Description |
|--------|------|-------------|
| plant_name | string | Official name of the power plant |
| lat | float | Latitude (decimal degrees) |
| lon | float | Longitude (decimal degrees) |
| capacity_mw | float | Total nameplate capacity in megawatts (MW) |
| status | string | "Operating" or "Retired" |
| retirement_year | float | Year of retirement (if applicable, null for operating) |
| state | string | Two-letter state code |
| plant_code | int | EIA plant identification code |

**Note:** Some plants marked as "Operating" may have a retirement_year if they have partially retired (some units closed, others still operating).

## Data Processing

### Source Files
- `2___Plant_Y2025.xlsx` - Plant location data (lat/lon)
- `3_1_Generator_Y2025.xlsx` - Generator data with fuel types and capacities
  - "Operable" sheet - Currently operating generators
  - "Retired and Canceled" sheet - Retired generators

### Filtering Criteria

**Coal Fuel Types (EIA Energy Source Codes):**
- BIT - Bituminous Coal
- SUB - Subbituminous Coal
- LIG - Lignite Coal
- ANT - Anthracite Coal
- WC - Waste/Other Coal
- RC - Refined Coal

**Inclusion Criteria:**
- Operating coal plants (any active coal generator as of 2025)
- Coal plants retired between 2015 and 2025

**Aggregation:**
- Capacity is summed across all coal generators at each plant
- Plant status is "Operating" if any coal unit is still running
- Coordinates from EIA plant-level data

## Intended Use

This dataset is prepared for geothermal overlay analysis - specifically to identify coal power plants that could potentially be retrofitted with or replaced by geothermal energy systems. The dataset includes:

1. **Operating plants** - Potential candidates for geothermal retrofit or co-location
2. **Recently retired plants** - Sites with existing transmission infrastructure that could be repurposed for geothermal development

## Data Limitations

- Capacity values represent total nameplate capacity (maximum rated output), not actual generation
- Plants with mixed fuel sources (coal + other fuels) are included if coal is a primary fuel
- Coordinates are for the plant site; actual generating units may be spread across a larger area
- "Operating" status is as of the 2025 EIA survey date
- No coordinate validation performed beyond excluding null values

## Updates

The EIA typically releases final Form 860 data in September each year for the previous year. To update this dataset:

1. Download the latest year's data from https://www.eia.gov/electricity/data/eia860/
2. Run the processing script with updated file names
3. Update the manifest with new statistics

## Contact

For questions about the EIA data itself, contact: infoelectric@eia.gov

---

*Dataset processed: 2026-09-15*

#!/usr/bin/env python3
"""
Process EIA Form 860 data to extract coal power plant information.
Creates a CSV with operating and recently retired coal plants.
"""

import pandas as pd
import json
from datetime import datetime

# File paths
plant_file = "data/raw/coal_plants/2___Plant_Y2025.xlsx"
generator_file = "data/raw/coal_plants/3_1_Generator_Y2025.xlsx"
output_file = "data/raw/coal_plants/eia_coal_plants.csv"
manifest_file = "data/raw/coal_plants/manifest.json"

print("Loading EIA Form 860 data...")
print("=" * 80)

# Load plant data (has lat/lon)
print("\n1. Loading plant location data...")
plant_df = pd.read_excel(plant_file, sheet_name='Plant', header=1)
print(f"   Loaded {len(plant_df):,} plants")

# Keep only needed columns
plant_df = plant_df[['Plant Code', 'Plant Name', 'State', 'Latitude', 'Longitude']]

# Load operable generator data
print("\n2. Loading operable generator data...")
operable_df = pd.read_excel(generator_file, sheet_name='Operable', header=1)
print(f"   Loaded {len(operable_df):,} operable generators")

# Load retired generator data
print("\n3. Loading retired generator data...")
retired_df = pd.read_excel(generator_file, sheet_name='Retired and Canceled', header=1)
print(f"   Loaded {len(retired_df):,} retired/canceled generators")

# Define coal-related codes
# Energy Source codes for coal:
# BIT = Bituminous Coal
# SUB = Subbituminous Coal
# LIG = Lignite Coal
# ANT = Anthracite Coal
# WC = Waste/Other Coal
# RC = Refined Coal
coal_energy_sources = ['BIT', 'SUB', 'LIG', 'ANT', 'WC', 'RC']

print("\n4. Filtering for coal plants...")

# Filter operable generators for coal
operable_coal = operable_df[
    (operable_df['Energy Source 1'].isin(coal_energy_sources)) |
    (operable_df['Technology'].str.contains('Coal', na=False, case=False))
].copy()
operable_coal['status'] = 'Operating'
operable_coal['retirement_year'] = None
print(f"   Found {len(operable_coal):,} operating coal generators")

# Filter retired generators for coal (retired since 2015)
# Convert Retirement Year to numeric first
retired_df['Retirement Year'] = pd.to_numeric(retired_df['Retirement Year'], errors='coerce')

retired_coal = retired_df[
    ((retired_df['Energy Source 1'].isin(coal_energy_sources)) |
     (retired_df['Technology'].str.contains('Coal', na=False, case=False))) &
    (retired_df['Retirement Year'] >= 2015)
].copy()
retired_coal['status'] = 'Retired'
retired_coal['retirement_year'] = retired_coal['Retirement Year']
print(f"   Found {len(retired_coal):,} coal generators retired since 2015")

# Combine operable and retired
all_coal = pd.concat([operable_coal, retired_coal], ignore_index=True)
print(f"   Total: {len(all_coal):,} coal generators")

# Select relevant columns and aggregate by plant
print("\n5. Aggregating by plant...")
all_coal_subset = all_coal[[
    'Plant Code', 'Plant Name', 'State',
    'Nameplate Capacity (MW)', 'status', 'retirement_year'
]]

# Group by plant and aggregate
plant_agg = all_coal_subset.groupby(['Plant Code', 'Plant Name', 'State']).agg({
    'Nameplate Capacity (MW)': 'sum',
    'status': lambda x: 'Operating' if 'Operating' in x.values else 'Retired',
    'retirement_year': lambda x: x.dropna().max() if x.notna().any() else None
}).reset_index()

# Rename columns
plant_agg.columns = ['Plant Code', 'Plant Name', 'State', 'capacity_mw', 'status', 'retirement_year']

print(f"   Aggregated to {len(plant_agg):,} unique plants")

# Merge with location data
print("\n6. Adding geographic coordinates...")
coal_plants = plant_agg.merge(
    plant_df[['Plant Code', 'Latitude', 'Longitude']],
    on='Plant Code',
    how='left'
)

# Drop plants without coordinates
before_drop = len(coal_plants)
coal_plants = coal_plants.dropna(subset=['Latitude', 'Longitude'])
print(f"   Dropped {before_drop - len(coal_plants)} plants without coordinates")

# Reorder and rename columns
coal_plants = coal_plants[[
    'Plant Name', 'Latitude', 'Longitude', 'capacity_mw', 'status', 'retirement_year', 'State', 'Plant Code'
]]
coal_plants.columns = ['plant_name', 'lat', 'lon', 'capacity_mw', 'status', 'retirement_year', 'state', 'plant_code']

# Round numeric columns
coal_plants['lat'] = coal_plants['lat'].round(6)
coal_plants['lon'] = coal_plants['lon'].round(6)
coal_plants['capacity_mw'] = coal_plants['capacity_mw'].round(2)

# Sort by capacity (largest first)
coal_plants = coal_plants.sort_values('capacity_mw', ascending=False).reset_index(drop=True)

# Save to CSV
print(f"\n7. Saving to {output_file}...")
coal_plants.to_csv(output_file, index=False)
print(f"   Saved {len(coal_plants):,} coal plants")

# Generate statistics
print("\n" + "=" * 80)
print("COAL PLANT STATISTICS")
print("=" * 80)

operating = coal_plants[coal_plants['status'] == 'Operating']
retired = coal_plants[coal_plants['status'] == 'Retired']

stats = {
    'total_plants': len(coal_plants),
    'operating_plants': len(operating),
    'retired_plants_since_2015': len(retired),
    'total_capacity_mw': float(coal_plants['capacity_mw'].sum()),
    'operating_capacity_mw': float(operating['capacity_mw'].sum()),
    'retired_capacity_mw': float(retired['capacity_mw'].sum()),
    'states_with_coal': coal_plants['state'].nunique(),
    'top_states': coal_plants.groupby('state')['capacity_mw'].sum().sort_values(ascending=False).head(10).to_dict()
}

print(f"\nTotal plants: {stats['total_plants']:,}")
print(f"  - Operating: {stats['operating_plants']:,}")
print(f"  - Retired since 2015: {stats['retired_plants_since_2015']:,}")

print(f"\nTotal capacity: {stats['total_capacity_mw']:,.1f} MW")
print(f"  - Operating: {stats['operating_capacity_mw']:,.1f} MW")
print(f"  - Retired: {stats['retired_capacity_mw']:,.1f} MW")

print(f"\nGeographic distribution:")
print(f"  - States with coal plants: {stats['states_with_coal']}")
print(f"\n  Top 10 states by capacity:")
for state, capacity in list(stats['top_states'].items()):
    print(f"    {state}: {capacity:,.1f} MW")

# Create manifest
print(f"\n8. Creating manifest at {manifest_file}...")
manifest = {
    'source': 'EIA Form 860 - Annual Electric Generator Report',
    'url': 'https://www.eia.gov/electricity/data/eia860/',
    'data_year': 2025,
    'download_date': datetime.now().isoformat(),
    'files_used': [
        '2___Plant_Y2025.xlsx (Plant location data)',
        '3_1_Generator_Y2025.xlsx (Generator data - Operable and Retired sheets)'
    ],
    'filter_criteria': {
        'fuel_types': coal_energy_sources,
        'status': ['Operating', 'Retired since 2015'],
        'retirement_cutoff_year': 2015
    },
    'statistics': stats,
    'notes': [
        'Capacity aggregated by plant (sum of all coal generators at each plant)',
        'Plants classified as Operating if any coal generator is still operating',
        'Coordinates from EIA plant location data',
        'Plants without coordinates excluded'
    ]
}

with open(manifest_file, 'w') as f:
    json.dump(manifest, f, indent=2)

print("\n" + "=" * 80)
print("COMPLETE!")
print("=" * 80)
print(f"\nOutput files:")
print(f"  - Data: {output_file}")
print(f"  - Manifest: {manifest_file}")

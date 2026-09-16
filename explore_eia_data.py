#!/usr/bin/env python3
"""
Explore EIA Form 860 data structure - corrected version with proper header handling.
"""

import pandas as pd

# File paths
plant_file = "data/raw/coal_plants/2___Plant_Y2025.xlsx"
generator_file = "data/raw/coal_plants/3_1_Generator_Y2025.xlsx"

print("=" * 80)
print("EXPLORING PLANT DATA")
print("=" * 80)

# Load plant data with header in row 1
plant_df = pd.read_excel(plant_file, sheet_name='Plant', header=1, nrows=10)
print(f"\nPlant data columns ({len(plant_df.columns)} total):")
for i, col in enumerate(plant_df.columns):
    print(f"  {i+1:3d}. {col}")

print(f"\nFirst row of plant data:")
print(plant_df.iloc[0])

# Look for coal-related columns
print(f"\n\nSample plant names and locations:")
if 'Plant Name' in plant_df.columns:
    for idx in range(min(5, len(plant_df))):
        print(f"  {plant_df.iloc[idx]['Plant Name']} - {plant_df.iloc[idx].get('State', 'N/A')}")

print("\n" + "=" * 80)
print("EXPLORING GENERATOR DATA - OPERABLE")
print("=" * 80)

# Load operable generator data with header in row 1
gen_df = pd.read_excel(generator_file, sheet_name='Operable', header=1, nrows=20)
print(f"\nOperable generator columns ({len(gen_df.columns)} total):")
for i, col in enumerate(gen_df.columns):
    print(f"  {i+1:3d}. {col}")

# Check for coal plants
if 'Technology' in gen_df.columns or 'Energy Source 1' in gen_df.columns:
    print(f"\nSample technologies/energy sources:")
    tech_col = 'Technology' if 'Technology' in gen_df.columns else 'Energy Source 1'
    print(gen_df[tech_col].value_counts().head(10))

print("\n" + "=" * 80)
print("EXPLORING GENERATOR DATA - RETIRED")
print("=" * 80)

# Load retired generator data
retired_df = pd.read_excel(generator_file, sheet_name='Retired and Canceled', header=1, nrows=20)
print(f"\nRetired generator columns ({len(retired_df.columns)} total):")
for i, col in enumerate(retired_df.columns):
    print(f"  {i+1:3d}. {col}")

print(f"\nFirst row of retired data:")
print(retired_df.iloc[0])

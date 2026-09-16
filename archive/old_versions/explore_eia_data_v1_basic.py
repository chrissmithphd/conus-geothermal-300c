#!/usr/bin/env python3
"""
Explore EIA Form 860 data structure to understand the columns and sheets.
"""

import pandas as pd
import sys

# File paths
plant_file = "data/raw/coal_plants/2___Plant_Y2025.xlsx"
generator_file = "data/raw/coal_plants/3_1_Generator_Y2025.xlsx"

print("=" * 80)
print("EXPLORING PLANT DATA")
print("=" * 80)

# Check what sheets are in the plant file
plant_sheets = pd.ExcelFile(plant_file).sheet_names
print(f"\nSheets in Plant file: {plant_sheets}")

# Load plant data (usually in first sheet)
plant_df = pd.read_excel(plant_file, sheet_name=plant_sheets[0], nrows=5)
print(f"\nPlant data columns ({len(plant_df.columns)} total):")
for i, col in enumerate(plant_df.columns):
    print(f"  {i+1:3d}. {col}")

print(f"\nFirst few rows of plant data:")
print(plant_df.head(2))

print("\n" + "=" * 80)
print("EXPLORING GENERATOR DATA")
print("=" * 80)

# Check what sheets are in the generator file
gen_sheets = pd.ExcelFile(generator_file).sheet_names
print(f"\nSheets in Generator file: {gen_sheets}")

# Load generator data (check each sheet)
for sheet in gen_sheets:
    print(f"\n--- Sheet: {sheet} ---")
    gen_df = pd.read_excel(generator_file, sheet_name=sheet, nrows=5)
    print(f"Columns ({len(gen_df.columns)} total):")
    for i, col in enumerate(gen_df.columns[:20]):  # First 20 columns
        print(f"  {i+1:3d}. {col}")
    if len(gen_df.columns) > 20:
        print(f"  ... and {len(gen_df.columns) - 20} more columns")
    print(f"\nFirst row:")
    print(gen_df.iloc[0])

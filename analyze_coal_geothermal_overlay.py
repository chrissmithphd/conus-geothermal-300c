#!/usr/bin/env python3
"""
Coal Power Plant + Geothermal Depth Overlay Analysis

Matches US coal plants (operating + retired since 2015) to the depth-to-300°C
geothermal grid to identify conversion/retrofit opportunities.
"""
import numpy as np
import pandas as pd
from scipy.spatial import cKDTree
from pathlib import Path

# The depth grid is spaced ~3-4 km. Any plant whose nearest grid cell is farther
# than this is outside the modeled CONUS domain (e.g. Alaska, Hawaii) and must be
# excluded — otherwise it gets matched to a random edge cell hundreds of km away
# and contaminates the depth categories and candidate ranking.
MAX_COVERAGE_DISTANCE_KM = 50

# ============================================================================
# Load Data
# ============================================================================

def load_coal_plants():
    """Load EIA coal plant data."""
    df = pd.read_csv("data/raw/coal_plants/eia_coal_plants.csv")
    print(f"Loaded {len(df)} coal plants:")
    print(f"  Operating: {(df['status'] == 'Operating').sum()}")
    print(f"  Retired:   {(df['status'] == 'Retired').sum()}")
    return df

def load_geothermal_grid():
    """Load depth-to-300°C geothermal grid."""
    df = pd.read_csv("data/processed/conus_depth_to_300c.csv")
    # Normalize bin labels
    df["bin_key"] = df["depth_bin"].replace({"≤4 km": "<=4 km"})
    print(f"\nLoaded {len(df):,} geothermal grid cells")
    return df

# ============================================================================
# Spatial Matching
# ============================================================================

def match_plants_to_grid(plants, grid):
    """
    For each coal plant, find the nearest geothermal grid cell and assign
    its depth-to-300°C category.

    Uses KD-tree for fast nearest-neighbor lookup with latitude correction.
    """
    print("\nMatching plants to geothermal grid...")

    # Latitude correction for longitude spacing (approximate)
    latref = np.cos(np.radians(grid["lat"].mean()))

    # Build KD-tree from geothermal grid
    tree_coords = np.column_stack([
        grid["lon"].values * latref,
        grid["lat"].values
    ])
    tree = cKDTree(tree_coords)

    # Query nearest grid cell for each plant
    plant_coords = np.column_stack([
        plants["lon"].values * latref,
        plants["lat"].values
    ])
    distances, indices = tree.query(plant_coords, k=1)

    # Convert distances to km (roughly)
    distances_km = distances * 111.0

    # Assign geothermal properties to plants
    plants = plants.copy()
    plants["nearest_grid_idx"] = indices
    plants["grid_distance_km"] = distances_km
    plants["depth_bin"] = grid.loc[indices, "depth_bin"].values
    plants["depth_300_km"] = grid.loc[indices, "depth_300_km"].values

    # Drop plants outside the modeled CONUS domain (nearest cell too far away).
    n_before = len(plants)
    out_of_coverage = plants["grid_distance_km"] > MAX_COVERAGE_DISTANCE_KM
    if out_of_coverage.any():
        dropped = plants[out_of_coverage]
        print(f"  Excluded {out_of_coverage.sum()} plants outside CONUS grid coverage "
              f"(>{MAX_COVERAGE_DISTANCE_KM} km from nearest cell):")
        for _, row in dropped.iterrows():
            print(f"    {row['plant_name']:35s} {row['state']:2s}  "
                  f"{row['grid_distance_km']:6,.0f} km")
    plants = plants[~out_of_coverage].reset_index(drop=True)

    print(f"  Matched {len(plants)}/{n_before} plants (mean distance: "
          f"{plants['grid_distance_km'].mean():.1f} km)")
    return plants

# ============================================================================
# Analysis
# ============================================================================

def analyze_by_depth_category(plants):
    """Analyze coal plant distribution across geothermal depth categories."""
    print("\n" + "="*70)
    print("COAL PLANT DISTRIBUTION BY GEOTHERMAL DEPTH CATEGORY")
    print("="*70)

    # Normalize bin names
    bins = ["≤4 km", "4-5 km", "5-6 km", "6-7 km", "7-8 km", "8-10 km", ">10 km"]

    for bin_name in bins:
        subset = plants[plants["depth_bin"] == bin_name]
        if len(subset) == 0:
            continue

        total_cap = subset["capacity_mw"].sum()
        operating = subset[subset["status"] == "Operating"]
        retired = subset[subset["status"] == "Retired"]

        print(f"\n{bin_name}:")
        print(f"  Total plants:    {len(subset):3d}  ({total_cap:7,.0f} MW)")
        print(f"  Operating:       {len(operating):3d}  ({operating['capacity_mw'].sum():7,.0f} MW)")
        print(f"  Retired:         {len(retired):3d}  ({retired['capacity_mw'].sum():7,.0f} MW)")

        if len(subset) <= 10 and bin_name != ">10 km":
            print(f"  Plants:")
            for _, row in subset.nlargest(10, "capacity_mw").iterrows():
                status_symbol = "●" if row["status"] == "Operating" else "○"
                print(f"    {status_symbol} {row['plant_name']:30s} {row['state']:2s}  {row['capacity_mw']:6,.0f} MW")

def top_candidates(plants, n=20):
    """Identify top coal-to-geothermal conversion candidates."""
    print("\n" + "="*70)
    print(f"TOP {n} COAL-TO-GEOTHERMAL CONVERSION CANDIDATES")
    print("="*70)
    print("(Sorted by: 1) Depth category (shallower = better)")
    print("           2) Capacity (larger = more impact)")
    print("           3) Status (recently retired = immediate opportunity)")

    # Define depth score (lower = shallower = better)
    depth_scores = {
        "≤4 km": 1, "4-5 km": 2, "5-6 km": 3, "6-7 km": 4,
        "7-8 km": 5, "8-10 km": 6, ">10 km": 10
    }
    plants["depth_score"] = plants["depth_bin"].map(depth_scores)

    # Status score (retired = opportunity, operating = potential)
    plants["status_score"] = plants["status"].map({"Retired": 1, "Operating": 2})

    # Multi-level sort
    candidates = plants.sort_values(
        by=["depth_score", "status_score", "capacity_mw"],
        ascending=[True, True, False]
    )

    print(f"\n{'Rank':<5} {'Plant Name':<35} {'State':<5} {'Capacity':<10} {'Status':<12} {'Depth Bin':<10} {'Depth (km)'}")
    print("-" * 120)

    for i, (_, row) in enumerate(candidates.head(n).iterrows(), 1):
        depth_str = f"{row['depth_300_km']:.1f}" if pd.notna(row['depth_300_km']) else ">10"
        print(f"{i:<5} {row['plant_name']:<35} {row['state']:<5} {row['capacity_mw']:>7,.0f} MW  "
              f"{row['status']:<12} {row['depth_bin']:<10} {depth_str}")

    return candidates.head(n)

def geographic_summary(plants):
    """Summarize coal plants by state, highlighting western states."""
    print("\n" + "="*70)
    print("COAL PLANTS BY STATE (Western states with geothermal potential)")
    print("="*70)

    # Western states likely to have favorable geothermal
    western_states = ["WY", "NM", "UT", "NV", "AZ", "CO", "ID", "MT", "CA", "OR", "WA"]

    state_summary = plants.groupby("state").agg({
        "plant_name": "count",
        "capacity_mw": "sum",
        "depth_bin": lambda x: (x != ">10 km").sum()  # count of accessible plants
    }).rename(columns={
        "plant_name": "total_plants",
        "capacity_mw": "total_capacity_mw",
        "depth_bin": "accessible_plants"
    })

    state_summary["pct_accessible"] = 100 * state_summary["accessible_plants"] / state_summary["total_plants"]
    state_summary = state_summary.sort_values("accessible_plants", ascending=False)

    print("\nWestern States:")
    print(f"{'State':<8} {'Plants':<8} {'Accessible':<12} {'% Accessible':<14} {'Total MW'}")
    print("-" * 70)

    for state in western_states:
        if state in state_summary.index:
            row = state_summary.loc[state]
            print(f"{state:<8} {row['total_plants']:<8.0f} {row['accessible_plants']:<12.0f} "
                  f"{row['pct_accessible']:>12.1f}%  {row['total_capacity_mw']:>12,.0f}")

    # Count total western capacity vs eastern
    western_plants = plants[plants["state"].isin(western_states)]
    eastern_plants = plants[~plants["state"].isin(western_states)]

    print(f"\n{'Region':<20} {'Plants':<10} {'Capacity (MW)':<15} {'Accessible ≤10km'}")
    print("-" * 70)
    print(f"{'Western US':<20} {len(western_plants):<10} {western_plants['capacity_mw'].sum():>13,.0f}  "
          f"{(western_plants['depth_bin'] != '>10 km').sum()}")
    print(f"{'Eastern US':<20} {len(eastern_plants):<10} {eastern_plants['capacity_mw'].sum():>13,.0f}  "
          f"{(eastern_plants['depth_bin'] != '>10 km').sum()}")

# ============================================================================
# Export Results
# ============================================================================

def save_results(plants):
    """Save matched coal plant + geothermal data."""
    outdir = Path("data/processed")
    outdir.mkdir(exist_ok=True, parents=True)

    outfile = outdir / "coal_plants_with_geothermal.csv"
    plants.to_csv(outfile, index=False)
    print(f"\n✅ Saved matched data to: {outfile}")

    # Also save top candidates
    candidates_file = outdir / "coal_geothermal_top_candidates.csv"
    depth_scores = {
        "≤4 km": 1, "4-5 km": 2, "5-6 km": 3, "6-7 km": 4,
        "7-8 km": 5, "8-10 km": 6, ">10 km": 10
    }
    plants["depth_score"] = plants["depth_bin"].map(depth_scores)
    plants["status_score"] = plants["status"].map({"Retired": 1, "Operating": 2})

    candidates = plants.sort_values(
        by=["depth_score", "status_score", "capacity_mw"],
        ascending=[True, True, False]
    ).head(50)

    candidates.to_csv(candidates_file, index=False)
    print(f"✅ Saved top 50 candidates to: {candidates_file}")

# ============================================================================
# Main
# ============================================================================

def main():
    print("="*70)
    print("COAL PLANT + GEOTHERMAL OVERLAY ANALYSIS")
    print("="*70)

    # Load data
    coal_plants = load_coal_plants()
    geothermal_grid = load_geothermal_grid()

    # Match plants to grid
    matched = match_plants_to_grid(coal_plants, geothermal_grid)

    # Analysis
    analyze_by_depth_category(matched)
    top_candidates(matched, n=20)
    geographic_summary(matched)

    # Save results
    save_results(matched)

    print("\n" + "="*70)
    print("Analysis complete! Ready for visualization.")
    print("="*70)

if __name__ == "__main__":
    main()

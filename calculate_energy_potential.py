#!/usr/bin/env python3
"""
Calculate geothermal energy generation potential for CONUS.

Uses research data on power density (MW/km²) at different temperatures to
estimate the total developable capacity in each depth category.
"""
import pandas as pd
import numpy as np

# ============================================================================
# Constants from Research
# ============================================================================

# Power density by temperature (MW/km²)
# Based on ENERGY_GENERATION_RESEARCH.md findings
POWER_DENSITY = {
    "conventional": {  # 150-200°C
        "conservative": 10,
        "typical": 12.5,
        "optimistic": 15
    },
    "superhot": {  # 300-400°C
        "conservative": 30,
        "typical": 35,
        "optimistic": 40
    },
    "supercritical": {  # >374°C
        "conservative": 25,
        "typical": 30,
        "optimistic": 35
    }
}

# Assumed temperature at each depth bin
DEPTH_TEMPERATURE = {
    "≤4 km": 400,     # Supercritical likely
    "4-5 km": 380,    # Supercritical boundary
    "5-6 km": 350,    # Superhot
    "6-7 km": 325,    # Superhot
    "7-8 km": 325,    # Superhot
    "8-10 km": 325,   # Superhot
    ">10 km": 300,    # Minimum superhot (but not accessible)
}

# Map temperature to system type
def get_system_type(temp_c):
    if temp_c >= 374:
        return "supercritical"
    elif temp_c >= 300:
        return "superhot"
    else:
        return "conventional"

# Development factors (what fraction of area is actually developable?)
DEVELOPMENT_FACTORS = {
    "conservative": 0.10,  # 10% of area (environmental, economic, technical limits)
    "typical": 0.20,       # 20% of area
    "optimistic": 0.40,    # 40% of area (aggressive development)
}

# ============================================================================
# Area Statistics (from depth analysis)
# ============================================================================

# Area in km² by depth bin (from calculate_depth_to_300c.py Sep 15 2026)
AREA_BY_DEPTH = {
    "≤4 km": 0,
    "4-5 km": 46,
    "5-6 km": 16_285,
    "6-7 km": 412_296,
    "7-8 km": 217_321,
    "8-10 km": 1_546_782,
    ">10 km": 6_407_277,
}

CUMULATIVE_ACCESSIBLE = {
    "≤7 km": 428_627,    # Current proven drilling envelope
    "≤8 km": 645_948,    # Advanced drilling
    "≤10 km": 2_192_730,  # Frontier drilling
}

# ============================================================================
# Capacity Calculations
# ============================================================================

def calculate_capacity(area_km2, temp_c, scenario="typical"):
    """
    Calculate potential electrical capacity for a given area and temperature.

    Args:
        area_km2: Total area in km²
        temp_c: Temperature at that depth in °C
        scenario: "conservative", "typical", or "optimistic"

    Returns:
        capacity_mw: Estimated electrical capacity in MW
    """
    system_type = get_system_type(temp_c)
    power_density = POWER_DENSITY[system_type][scenario]
    development_factor = DEVELOPMENT_FACTORS[scenario]

    developable_area = area_km2 * development_factor
    capacity_mw = developable_area * power_density

    return capacity_mw

def main():
    print("="*80)
    print("GEOTHERMAL ENERGY GENERATION POTENTIAL - CONUS")
    print("="*80)

    print("\nBased on research findings:")
    print("  Conventional (150-200°C): 10-15 MW/km² (e.g., The Geysers)")
    print("  Superhot (300-400°C):     30-40 MW/km² (estimated)")
    print("  Supercritical (>374°C):   25-35 MW/km² (IDDP-2 demonstrated)")

    print("\nDevelopment factors:")
    print("  Conservative: 10% of area developed")
    print("  Typical:      20% of area developed")
    print("  Optimistic:   40% of area developed")

    # Individual depth bins
    print("\n" + "="*80)
    print("CAPACITY POTENTIAL BY DEPTH BIN")
    print("="*80)

    results = []
    for depth_bin, area_km2 in AREA_BY_DEPTH.items():
        if area_km2 == 0:
            continue

        temp = DEPTH_TEMPERATURE[depth_bin]
        system_type = get_system_type(temp)

        cap_cons = calculate_capacity(area_km2, temp, "conservative")
        cap_typ = calculate_capacity(area_km2, temp, "typical")
        cap_opt = calculate_capacity(area_km2, temp, "optimistic")

        results.append({
            "depth_bin": depth_bin,
            "area_km2": area_km2,
            "temp_c": temp,
            "system_type": system_type,
            "capacity_conservative_mw": cap_cons,
            "capacity_typical_mw": cap_typ,
            "capacity_optimistic_mw": cap_opt,
        })

        print(f"\n{depth_bin}:")
        print(f"  Area:              {area_km2:>12,} km²")
        print(f"  Temperature:       {temp:>12} °C ({system_type})")
        print(f"  Capacity (Cons):   {cap_cons/1000:>12,.1f} GW")
        print(f"  Capacity (Typ):    {cap_typ/1000:>12,.1f} GW")
        print(f"  Capacity (Opt):    {cap_opt/1000:>12,.1f} GW")

    # Cumulative by drilling depth capability
    print("\n" + "="*80)
    print("CUMULATIVE CAPACITY BY DRILLING DEPTH CAPABILITY")
    print("="*80)

    drilling_scenarios = {
        "≤7 km (Proven today)": ["4-5 km", "5-6 km", "6-7 km"],
        "≤8 km (Advanced)": ["4-5 km", "5-6 km", "6-7 km", "7-8 km"],
        "≤10 km (Frontier)": ["4-5 km", "5-6 km", "6-7 km", "7-8 km", "8-10 km"],
    }

    for scenario_name, bins in drilling_scenarios.items():
        total_area = sum(AREA_BY_DEPTH[b] for b in bins)

        # Calculate capacity using typical scenario
        total_cap_cons = sum(
            calculate_capacity(AREA_BY_DEPTH[b], DEPTH_TEMPERATURE[b], "conservative")
            for b in bins
        )
        total_cap_typ = sum(
            calculate_capacity(AREA_BY_DEPTH[b], DEPTH_TEMPERATURE[b], "typical")
            for b in bins
        )
        total_cap_opt = sum(
            calculate_capacity(AREA_BY_DEPTH[b], DEPTH_TEMPERATURE[b], "optimistic")
            for b in bins
        )

        print(f"\n{scenario_name}:")
        print(f"  Total area:        {total_area:>12,} km²")
        print(f"  Capacity (Cons):   {total_cap_cons/1000:>12,.0f} GW")
        print(f"  Capacity (Typ):    {total_cap_typ/1000:>12,.0f} GW")
        print(f"  Capacity (Opt):    {total_cap_opt/1000:>12,.0f} GW")

    # Context: US electricity generation
    print("\n" + "="*80)
    print("CONTEXT: US ELECTRICITY GENERATION")
    print("="*80)

    us_total_capacity = 1_287_000  # MW (2024 estimate)
    us_coal_capacity = 180_000     # MW remaining coal in 2024
    us_natural_gas_capacity = 516_000  # MW

    print(f"\nUS Total Generation Capacity:     ~{us_total_capacity/1000:,.0f} GW")
    print(f"US Coal Capacity (2024):          ~{us_coal_capacity/1000:,.0f} GW")
    print(f"US Natural Gas Capacity (2024):   ~{us_natural_gas_capacity/1000:,.0f} GW")

    # Compare scenarios
    cap_7km = sum(calculate_capacity(AREA_BY_DEPTH[b], DEPTH_TEMPERATURE[b], "typical")
                  for b in drilling_scenarios["≤7 km (Proven today)"]) / 1000
    cap_10km = sum(calculate_capacity(AREA_BY_DEPTH[b], DEPTH_TEMPERATURE[b], "typical")
                   for b in drilling_scenarios["≤10 km (Frontier)"]) / 1000

    print(f"\nGeothermal potential (typical dev):")
    print(f"  ≤7 km depth:  {cap_7km:>6,.0f} GW  ({100*cap_7km/us_total_capacity:>5.1f}% of US total)")
    print(f"  ≤10 km depth: {cap_10km:>6,.0f} GW  ({100*cap_10km/us_total_capacity:>5.1f}% of US total)")
    print(f"\nIncrease from 7km → 10km drilling: {cap_10km/cap_7km:>5.1f}x capacity")

    # Export table
    df = pd.DataFrame(results)
    df.to_csv("data/processed/energy_generation_potential.csv", index=False)
    print("\n✅ Saved detailed results to: data/processed/energy_generation_potential.csv")

    # Create summary table for README
    print("\n" + "="*80)
    print("SUMMARY TABLE FOR README")
    print("="*80)
    print("\n| Depth Bin | Area (km²) | Temp (°C) | Type | Capacity (Typical) | % of US Total |")
    print("|-----------|------------|-----------|------|--------------------|----|")

    for _, row in df.iterrows():
        if row["depth_bin"] == ">10 km":
            continue  # Not accessible
        cap_gw = row["capacity_typical_mw"] / 1000
        pct_us = 100 * cap_gw / (us_total_capacity/1000)
        print(f"| {row['depth_bin']:<9} | {row['area_km2']:>10,} | {row['temp_c']:>9} | "
              f"{row['system_type']:<13} | {cap_gw:>8,.0f} GW | {pct_us:>4.1f}% |")

    # Cumulative summary
    print("\n| Drilling Depth | Cumulative Area | Cumulative Capacity | % of US Total |")
    print("|----------------|-----------------|---------------------|---------------|")
    for scenario_name, bins in drilling_scenarios.items():
        total_area = sum(AREA_BY_DEPTH[b] for b in bins)
        total_cap = sum(
            calculate_capacity(AREA_BY_DEPTH[b], DEPTH_TEMPERATURE[b], "typical")
            for b in bins
        ) / 1000
        pct_us = 100 * total_cap / (us_total_capacity/1000)
        print(f"| {scenario_name:<14} | {total_area:>15,} | {total_cap:>9,.0f} GW | {pct_us:>11.1f}% |")

    print("\n" + "="*80)

if __name__ == "__main__":
    main()

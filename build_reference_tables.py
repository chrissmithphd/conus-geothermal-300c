#!/usr/bin/env python3
"""Build the geographic-reference table for the README from the frozen grid.

Reproducible from the canonical grid alone:
  - data/processed/conus_depth_to_300c.parquet   (534,942 cells)

Writes data/processed/geographic_reference.csv and prints the Markdown block
used in the README's "Where the models suggest accessible resources may be"
section.

What is COMPUTED here (fully reproducible): cell counts by depth tier,
representative coordinates, and the modeled-depth values. What is CURATED
(interpretive, defined in REGIONS below): the geographic/tectonic NAMES and the
one-line settings. The reproducible numbers are never hand-entered.
"""
import numpy as np
import pandas as pd

GRID = "data/processed/conus_depth_to_300c.parquet"
OUT_REF = "data/processed/geographic_reference.csv"

# Curated bounding boxes + names + setting. Everything numeric inside a box
# (center, depth, counts) is computed from the cells it holds.
REGIONS = [
    ("Cascades (OR/WA/N.CA axis)", "geothermal region", "OR·WA·CA",
     (40.0, 49.0, -123.0, -120.0),
     "Volcanic arc; shallowest cells in the analysis sit on the Cascade crest."),
    ("Salton Trough / Imperial Valley", "geothermal region", "CA",
     (32.5, 34.0, -116.3, -115.3),
     "Active spreading center; among the hottest-shallow settings in CONUS."),
    ("Snake River Plain / Yellowstone", "geothermal region", "ID·WY·MT",
     (42.0, 45.2, -115.0, -109.5),
     "Hotspot track; shallow cells arc NE toward the Yellowstone caldera."),
    ("Northern Nevada (NW corner)", "geothermal region", "NV",
     (40.0, 42.0, -119.5, -117.0),
     "Edge-of-Basin&Range extension, not statewide; Black Rock / Surprise Valley."),
    ("Roosevelt Hot Springs / Utah FORGE", "geothermal site", "UT",
     (38.2, 38.7, -113.1, -112.6),
     "DOE EGS field site; small, well-characterized shallow anomaly."),
    ("Aspen-Salida / Upper Arkansas", "geothermal region", "CO",
     (38.4, 39.4, -106.6, -105.8),
     "Northern reach of the Rio Grande rift; densest shallow cluster in interior Rockies."),
    ("Rio Grande Rift (New Mexico)", "geothermal region", "NM",
     (33.0, 36.2, -107.5, -106.0),
     "Extensional rift; Valles/Jemez, Socorro, Rio Grande corridor."),
    ("The Geysers / Clear Lake", "geothermal region", "CA",
     (38.4, 39.2, -123.2, -122.4),
     "Clear Lake volcanic field; world's largest operating geothermal complex. "
     "Shallowest CA cells outside the Salton Trough."),
    ("Coso / Owens Valley", "geothermal region", "CA",
     (35.8, 36.6, -117.8, -117.0),
     "Coso Volcanic Field on the eastern Sierra front; operating flash-steam field at China Lake."),
]


def build_reference(df):
    rows = []
    for name, typ, states, (la0, la1, lo0, lo1), setting in REGIONS:
        box = df[(df.lat >= la0) & (df.lat <= la1)
                 & (df.lon >= lo0) & (df.lon <= lo1)]
        reached = box[box["depth_300_km"].notna()]
        stanford = reached[reached["depth_300_km"] < 7.5]  # continuous tier
        n_le6 = int((box["depth_300_km"] <= 6.0).sum())
        n_le7 = int((box["depth_300_km"] <= 7.0).sum())
        n_le10 = int(reached.shape[0])
        # Characterize the region by its shallow (accessible) signature, not a
        # box-wide median that deep SMU cells would drag down.
        if len(stanford) >= 20:
            disp = f"{stanford['depth_300_km'].median():.1f} km"
            kind = "Stanford (continuous, ≤7 km cells)"
            tier = stanford
        elif len(reached):
            lo = sorted(set(np.round(reached["depth_300_km"], 1)))
            disp = f"{lo[0]:.1f}–{lo[min(1, len(lo) - 1)]:.1f} km bracket"
            kind, tier = "SMU (categorical)", reached
        else:
            disp, kind, tier = ">10 km (none reached)", "none", box
        rep_lat = round(tier["lat"].median(), 3)
        rep_lon = round(tier["lon"].median(), 3)
        shallowest = round(reached["depth_300_km"].min(), 2) if len(reached) else np.nan
        coherence = ("large coherent region" if n_le10 >= 100
                     else "moderate cluster" if n_le10 >= 20
                     else "small / isolated anomaly")
        rows.append({
            "location": name, "type": typ, "states": states,
            "rep_lat": rep_lat, "rep_lon": rep_lon,
            "modeled_depth_300c": disp, "depth_kind": kind,
            "shallowest_km": shallowest,
            "cells_reached_le10km": n_le10, "cells_le7km": n_le7,
            "cells_le6km": n_le6, "consistency": coherence,
            "interpretation": setting,
        })
    return pd.DataFrame(rows)


def main():
    df = pd.read_parquet(GRID)
    ref = build_reference(df)
    ref.to_csv(OUT_REF, index=False)
    print(f"Wrote {OUT_REF}")
    with pd.option_context("display.max_colwidth", 45, "display.width", 200):
        print(ref.to_string(index=False))


if __name__ == "__main__":
    main()

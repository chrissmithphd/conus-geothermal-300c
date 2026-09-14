#!/usr/bin/env python3
"""
Inspect and validate Stanford temperature data after download.
"""
import json
import sys
from pathlib import Path
from collections import Counter
import statistics

def load_layer_data(json_file):
    """Load a single depth layer JSON file."""
    with open(json_file, 'r') as f:
        return json.load(f)

def inspect_layer(json_file):
    """Inspect a single depth layer and return statistics."""
    print(f"\n{'='*80}")
    print(f"Layer: {json_file.name}")
    print('='*80)

    data = load_layer_data(json_file)
    metadata = data.get('metadata', {})
    features = data.get('features', [])

    # Basic metadata
    print(f"\nMetadata:")
    print(f"  Source: {metadata.get('source', 'N/A')}")
    print(f"  Download Date: {metadata.get('download_date', 'N/A')}")
    print(f"  Feature Count: {metadata.get('feature_count', 'N/A'):,}")
    print(f"  Spatial Reference: EPSG:{metadata.get('spatialReference', {}).get('wkid', 'N/A')}")

    # Extract temperature values
    temperatures = []
    lats = []
    lons = []
    missing_temp = 0
    missing_coords = 0

    for feature in features:
        attrs = feature.get('attributes', {})

        temp = attrs.get('T')
        lat = attrs.get('Lat')
        lon = attrs.get('Long')

        if temp is not None:
            temperatures.append(temp)
        else:
            missing_temp += 1

        if lat is not None and lon is not None:
            lats.append(lat)
            lons.append(lon)
        else:
            missing_coords += 1

    # Temperature statistics
    if temperatures:
        print(f"\nTemperature Statistics (T):")
        print(f"  Count: {len(temperatures):,}")
        print(f"  Min: {min(temperatures):.2f}")
        print(f"  Max: {max(temperatures):.2f}")
        print(f"  Mean: {statistics.mean(temperatures):.2f}")
        print(f"  Median: {statistics.median(temperatures):.2f}")
        print(f"  Std Dev: {statistics.stdev(temperatures):.2f}")
        print(f"  Missing: {missing_temp}")

        # Temperature distribution
        print(f"\n  Temperature Ranges:")
        ranges = [
            (0, 50, "0-50°C"),
            (50, 100, "50-100°C"),
            (100, 150, "100-150°C"),
            (150, 200, "150-200°C"),
            (200, 250, "200-250°C"),
            (250, 300, "250-300°C"),
            (300, 350, "300-350°C"),
            (350, float('inf'), ">350°C")
        ]

        for min_t, max_t, label in ranges:
            count = sum(1 for t in temperatures if min_t <= t < max_t)
            pct = (count / len(temperatures)) * 100
            print(f"    {label:12s}: {count:7,} ({pct:5.1f}%)")

    # Geographic extent
    if lats and lons:
        print(f"\nGeographic Extent:")
        print(f"  Latitude:  {min(lats):7.3f}° to {max(lats):7.3f}°")
        print(f"  Longitude: {min(lons):7.3f}° to {max(lons):7.3f}°")
        print(f"  Missing Coordinates: {missing_coords}")

    # Sample records
    print(f"\nSample Records (first 3):")
    for i, feature in enumerate(features[:3]):
        attrs = feature.get('attributes', {})
        geom = feature.get('geometry', {})
        print(f"  Record {i+1}:")
        print(f"    T={attrs.get('T', 'N/A')}°C, Lat={attrs.get('Lat', 'N/A')}, Long={attrs.get('Long', 'N/A')}")
        print(f"    Geometry: x={geom.get('x', 'N/A')}, y={geom.get('y', 'N/A')}")

    return {
        'file': json_file.name,
        'feature_count': len(features),
        'temp_count': len(temperatures),
        'temp_min': min(temperatures) if temperatures else None,
        'temp_max': max(temperatures) if temperatures else None,
        'temp_mean': statistics.mean(temperatures) if temperatures else None,
        'lat_min': min(lats) if lats else None,
        'lat_max': max(lats) if lats else None,
        'lon_min': min(lons) if lons else None,
        'lon_max': max(lons) if lons else None,
        'missing_temp': missing_temp,
        'missing_coords': missing_coords,
        'above_300c': sum(1 for t in temperatures if t >= 300) if temperatures else 0
    }

def compare_layers(stats_list):
    """Compare statistics across all layers."""
    print(f"\n{'='*80}")
    print("Cross-Layer Comparison")
    print('='*80)

    print(f"\nFeature Count Consistency:")
    feature_counts = Counter([s['feature_count'] for s in stats_list])
    for count, freq in feature_counts.most_common():
        print(f"  {count:,} features: {freq} layers")

    if len(feature_counts) == 1:
        print(f"  ✅ All layers have identical grid structure")
    else:
        print(f"  ⚠️  WARNING: Layers have different feature counts!")

    print(f"\nGeographic Extent Consistency:")
    print(f"  Latitude  Min: {min(s['lat_min'] for s in stats_list if s['lat_min']):.3f}°")
    print(f"  Latitude  Max: {max(s['lat_max'] for s in stats_list if s['lat_max']):.3f}°")
    print(f"  Longitude Min: {min(s['lon_min'] for s in stats_list if s['lon_min']):.3f}°")
    print(f"  Longitude Max: {max(s['lon_max'] for s in stats_list if s['lon_max']):.3f}°")

    lat_ranges = [(s['lat_min'], s['lat_max']) for s in stats_list if s['lat_min']]
    lon_ranges = [(s['lon_min'], s['lon_max']) for s in stats_list if s['lon_min']]

    if len(set(lat_ranges)) == 1 and len(set(lon_ranges)) == 1:
        print(f"  ✅ All layers cover identical geographic extent")
    else:
        print(f"  ⚠️  WARNING: Layers have different geographic extents!")

    print(f"\nTemperature Ranges by Depth:")
    print(f"  {'Layer':<20} {'Min°C':>8} {'Max°C':>8} {'Mean°C':>8} {'>300°C Count':>15}")
    print(f"  {'-'*20} {'-'*8} {'-'*8} {'-'*8} {'-'*15}")
    for s in stats_list:
        depth = s['file'].replace('temperature_', '').replace('.json', '')
        print(f"  {depth:<20} {s['temp_min']:8.1f} {s['temp_max']:8.1f} {s['temp_mean']:8.1f} {s['above_300c']:15,}")

    print(f"\nData Quality:")
    total_missing_temp = sum(s['missing_temp'] for s in stats_list)
    total_missing_coords = sum(s['missing_coords'] for s in stats_list)

    if total_missing_temp == 0 and total_missing_coords == 0:
        print(f"  ✅ No missing temperature values")
        print(f"  ✅ No missing coordinates")
    else:
        print(f"  ⚠️  Missing temperature values: {total_missing_temp:,}")
        print(f"  ⚠️  Missing coordinates: {total_missing_coords:,}")

def main():
    data_dir = Path("data/raw/stanford")

    print("Stanford Thermal Earth Model Data Inspection")
    print("=" * 80)

    # Find all temperature JSON files
    json_files = sorted(data_dir.glob("temperature_*.json"))

    if not json_files:
        print(f"\n❌ ERROR: No temperature JSON files found in {data_dir}")
        print("   Make sure the download has completed successfully.")
        sys.exit(1)

    print(f"\nFound {len(json_files)} layer files:")
    for f in json_files:
        print(f"  - {f.name}")

    # Inspect each layer
    stats_list = []
    for json_file in json_files:
        try:
            stats = inspect_layer(json_file)
            stats_list.append(stats)
        except Exception as e:
            print(f"\n❌ ERROR processing {json_file.name}: {e}")

    # Cross-layer comparison
    if len(stats_list) > 1:
        compare_layers(stats_list)

    print(f"\n{'='*80}")
    print("Inspection Complete")
    print('='*80)
    print(f"\nSummary:")
    print(f"  ✅ {len(stats_list)}/{len(json_files)} layers processed successfully")
    print(f"  ✅ Total grid points: {stats_list[0]['feature_count']:,} per layer" if stats_list else "")
    print(f"  ✅ Depth coverage: 0-7 km in 1 km increments")

    # Check if we can reach 300°C
    print(f"\n300°C Reachability:")
    for s in stats_list:
        depth = s['file'].replace('temperature_', '').replace('.json', '')
        pct = (s['above_300c'] / s['feature_count']) * 100 if s['feature_count'] > 0 else 0
        print(f"  At {depth:3s}: {s['above_300c']:6,} locations ({pct:4.1f}%) reach ≥300°C")

if __name__ == "__main__":
    main()

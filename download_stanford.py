#!/usr/bin/env python3
"""
Download Stanford Thermal Earth Model temperature data from ArcGIS REST services.
"""
import requests
import json
import sys
from pathlib import Path
from datetime import datetime

# Stanford temperature prediction layers at different depths
LAYERS = {
    "0km": "https://services.arcgis.com/7CRlmWNEbeCqEJ6a/arcgis/rest/services/stm_interpignn_0km/FeatureServer/0",
    "1km": "https://services.arcgis.com/7CRlmWNEbeCqEJ6a/arcgis/rest/services/Stanford_Temperature_Predictions_at_1km/FeatureServer/0",
    "2km": "https://services.arcgis.com/7CRlmWNEbeCqEJ6a/arcgis/rest/services/Stanford_Temperature_Predictions_at_2km/FeatureServer/0",
    "3km": "https://services.arcgis.com/7CRlmWNEbeCqEJ6a/arcgis/rest/services/Stanford_Temperature_Predictions_at_3km/FeatureServer/0",
    "4km": "https://services.arcgis.com/7CRlmWNEbeCqEJ6a/arcgis/rest/services/Stanford_Temperature_Predictions_at_4km/FeatureServer/0",
    "5km": "https://services.arcgis.com/7CRlmWNEbeCqEJ6a/arcgis/rest/services/Stanford_Temperature_Predictions_at_5km/FeatureServer/0",
    "6km": "https://services.arcgis.com/7CRlmWNEbeCqEJ6a/arcgis/rest/services/Stanford_Temperature_Predictions_at_6km/FeatureServer/0",
    "7km": "https://services.arcgis.com/7CRlmWNEbeCqEJ6a/arcgis/rest/services/Stanford_Temperature_Predictions_at_7km/FeatureServer/0",
}

def get_feature_count(service_url):
    """Get total feature count for a layer."""
    params = {
        "where": "1=1",
        "returnCountOnly": "true",
        "f": "json"
    }
    response = requests.get(f"{service_url}/query", params=params)
    response.raise_for_status()
    return response.json()["count"]

def download_layer(service_url, output_file, batch_size=1000):
    """Download all features from a layer using pagination."""

    # Get total count
    total_count = get_feature_count(service_url)
    print(f"  Total features: {total_count:,}")

    all_features = []
    offset = 0

    while offset < total_count:
        # Query with pagination
        params = {
            "where": "1=1",
            "outFields": "*",
            "resultOffset": offset,
            "resultRecordCount": batch_size,
            "f": "json"
        }

        response = requests.get(f"{service_url}/query", params=params)
        response.raise_for_status()
        data = response.json()

        features = data.get("features", [])
        if not features:
            break

        all_features.extend(features)
        offset += len(features)

        # Progress indicator
        progress = (offset / total_count) * 100
        print(f"  Progress: {offset:,}/{total_count:,} ({progress:.1f}%)", end="\r")

    print()  # New line after progress

    # Save to JSON
    output = {
        "metadata": {
            "source": service_url,
            "download_date": datetime.utcnow().isoformat() + "Z",
            "feature_count": len(all_features),
            "spatial_reference": data.get("spatialReference", {}),
            "fields": data.get("fields", [])
        },
        "features": all_features
    }

    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"  Saved to {output_file}")
    return len(all_features)

def main():
    output_dir = Path("data/raw/stanford")
    output_dir.mkdir(parents=True, exist_ok=True)

    print("Downloading Stanford Thermal Earth Model data...")
    print(f"Output directory: {output_dir}\n")

    manifest = {
        "dataset": "Stanford Thermal Earth Model for the Conterminous United States",
        "source": "https://data.openei.org/submissions/7669",
        "reference": "Aljubran & Horne (2024)",
        "doi": "10.1186/s40517-024-00304-7",
        "download_date": datetime.utcnow().isoformat() + "Z",
        "layers": {}
    }

    for depth, url in LAYERS.items():
        print(f"Downloading {depth} layer...")
        output_file = output_dir / f"temperature_{depth}.json"

        try:
            feature_count = download_layer(url, output_file)
            manifest["layers"][depth] = {
                "url": url,
                "output_file": str(output_file),
                "feature_count": feature_count
            }
        except Exception as e:
            print(f"  ERROR: {e}")
            manifest["layers"][depth] = {
                "url": url,
                "error": str(e)
            }

        print()

    # Save manifest
    manifest_file = output_dir / "manifest.json"
    with open(manifest_file, 'w') as f:
        json.dump(manifest, f, indent=2)

    print(f"Manifest saved to {manifest_file}")
    print("\nDownload complete!")

if __name__ == "__main__":
    main()

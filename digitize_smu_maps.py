#!/usr/bin/env python3
"""
Digitize SMU temperature-at-depth PNG maps into numerical gridded data.
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image
from pathlib import Path
from scipy.spatial.distance import cdist

# Output directory
OUTPUT_DIR = Path("data/processed/smu_digitized")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

PLOT_DIR = Path("plots")
PLOT_DIR.mkdir(exist_ok=True)

def analyze_image_structure(image_path):
    """Analyze the image to understand its structure."""
    img = Image.open(image_path)
    img_array = np.array(img)

    print(f"\n{'='*80}")
    print(f"Image Analysis: {image_path.name}")
    print('='*80)
    print(f"Dimensions: {img_array.shape[1]} x {img_array.shape[0]} pixels")
    print(f"Channels: {img_array.shape[2] if len(img_array.shape) > 2 else 1}")
    print(f"Data type: {img_array.dtype}")

    return img, img_array

def build_temperature_legend():
    """
    Build color-to-temperature mapping from the SMU legend.

    The SMU maps use a green-yellow-orange-red-magenta color scale.
    Based on visual inspection of the legend: 25°C (green) to 350°C (magenta).
    """
    # Define the color scale with RGB values and corresponding temperatures
    # These are approximate values extracted from the legend
    legend = [
        # (R, G, B), temperature_low, temperature_high, temperature_mid, label
        ((0, 100, 0), 25, 50, 37.5, "25-50°C"),      # Dark green
        ((0, 180, 0), 50, 75, 62.5, "50-75°C"),      # Green
        ((100, 255, 0), 75, 100, 87.5, "75-100°C"),  # Yellow-green
        ((200, 255, 0), 100, 125, 112.5, "100-125°C"), # Yellow
        ((255, 255, 0), 125, 150, 137.5, "125-150°C"), # Bright yellow
        ((255, 200, 0), 150, 175, 162.5, "150-175°C"), # Yellow-orange
        ((255, 150, 0), 175, 200, 187.5, "175-200°C"), # Orange
        ((255, 100, 0), 200, 225, 212.5, "200-225°C"), # Red-orange
        ((255, 50, 0), 225, 250, 237.5, "225-250°C"),  # Red
        ((255, 0, 0), 250, 275, 262.5, "250-275°C"),   # Bright red
        ((200, 0, 100), 275, 300, 287.5, "275-300°C"), # Red-magenta
        ((150, 0, 150), 300, 325, 312.5, "300-325°C"), # Magenta
        ((100, 0, 200), 325, 350, 337.5, "325-350°C"), # Blue-magenta
    ]

    colors = np.array([item[0] for item in legend])
    temp_low = np.array([item[1] for item in legend])
    temp_high = np.array([item[2] for item in legend])
    temp_mid = np.array([item[3] for item in legend])
    labels = [item[4] for item in legend]

    return {
        'colors': colors,
        'temp_low': temp_low,
        'temp_high': temp_high,
        'temp_mid': temp_mid,
        'labels': labels
    }

def extract_map_bounds(img_array):
    """
    Estimate the map area boundaries by detecting the black border
    and excluding the legend area.

    SMU maps have:
    - Black state boundaries
    - Legend on the right side
    - Title at top
    - Attribution at bottom
    """
    height, width = img_array.shape[:2]

    # Approximate boundaries (will vary slightly by image)
    # Based on visual inspection of SMU maps:
    # - Title ~40 pixels from top
    # - Attribution ~60 pixels from bottom
    # - Legend ~150 pixels from right
    # - Left edge ~50 pixels from left

    bounds = {
        'top': 80,
        'bottom': height - 60,
        'left': 50,
        'right': width - 180
    }

    print(f"\nEstimated map bounds:")
    print(f"  Top: {bounds['top']}, Bottom: {bounds['bottom']}")
    print(f"  Left: {bounds['left']}, Right: {bounds['right']}")
    print(f"  Map area: {bounds['right']-bounds['left']} x {bounds['bottom']-bounds['top']} pixels")

    return bounds

def extract_map_pixels(img_array, bounds):
    """Extract just the map area, excluding borders and legend."""
    map_area = img_array[
        bounds['top']:bounds['bottom'],
        bounds['left']:bounds['right'],
        :3  # RGB only
    ]
    return map_area

def classify_pixels(map_pixels, legend, max_distance=50):
    """
    Classify each map pixel to the closest temperature class.

    Args:
        map_pixels: RGB array of map area
        legend: Dictionary with color legend
        max_distance: Maximum color distance for classification
    """
    height, width = map_pixels.shape[:2]
    n_pixels = height * width

    # Reshape to (n_pixels, 3) for vectorized distance calculation
    pixels_flat = map_pixels.reshape(n_pixels, 3)

    print(f"\nClassifying {n_pixels:,} pixels...")

    # Calculate color distances to all legend colors
    distances = cdist(pixels_flat.astype(float), legend['colors'].astype(float), metric='euclidean')

    # Find closest color for each pixel
    closest_indices = np.argmin(distances, axis=1)
    closest_distances = np.min(distances, axis=1)

    # Mark pixels that are too far from any legend color as unclassified
    valid_mask = closest_distances <= max_distance

    # Create classification array
    temp_classified = np.full(n_pixels, np.nan)
    temp_classified[valid_mask] = legend['temp_mid'][closest_indices[valid_mask]]

    # Reshape back to map dimensions
    temp_map = temp_classified.reshape(height, width)

    n_valid = valid_mask.sum()
    pct_valid = (n_valid / n_pixels) * 100

    print(f"  Classified: {n_valid:,} pixels ({pct_valid:.1f}%)")
    print(f"  Unclassified: {n_pixels - n_valid:,} pixels ({100-pct_valid:.1f}%)")

    return temp_map, valid_mask.reshape(height, width)

def georeference_map(temp_map, bounds_px):
    """
    Assign lat/lon coordinates to each pixel based on CONUS extent.

    CONUS approximate bounds:
    - Latitude: 24.5°N to 49.4°N
    - Longitude: -125°W to -66°W
    """
    height, width = temp_map.shape

    # CONUS geographic bounds
    lat_min, lat_max = 24.5, 49.4
    lon_min, lon_max = -125.0, -66.0

    # Create coordinate arrays
    lats = np.linspace(lat_max, lat_min, height)  # Top to bottom
    lons = np.linspace(lon_min, lon_max, width)   # Left to right

    # Create meshgrid
    lon_grid, lat_grid = np.meshgrid(lons, lats)

    return lat_grid, lon_grid

def create_gridded_dataset(temp_map, lat_grid, lon_grid, depth_km, valid_mask):
    """Create a DataFrame with lat, lon, temperature for all valid pixels."""
    # Flatten arrays
    lats_flat = lat_grid.flatten()
    lons_flat = lon_grid.flatten()
    temps_flat = temp_map.flatten()
    valid_flat = valid_mask.flatten()

    # Keep only valid (classified) pixels
    df = pd.DataFrame({
        'lat': lats_flat[valid_flat],
        'lon': lons_flat[valid_flat],
        'depth_km': depth_km,
        'temperature_c': temps_flat[valid_flat]
    })

    # Add temperature class bins
    def temp_to_class(temp):
        if temp < 50:
            return "25-50°C"
        elif temp < 75:
            return "50-75°C"
        elif temp < 100:
            return "75-100°C"
        elif temp < 125:
            return "100-125°C"
        elif temp < 150:
            return "125-150°C"
        elif temp < 175:
            return "150-175°C"
        elif temp < 200:
            return "175-200°C"
        elif temp < 225:
            return "200-225°C"
        elif temp < 250:
            return "225-250°C"
        elif temp < 275:
            return "250-275°C"
        elif temp < 300:
            return "275-300°C"
        elif temp < 325:
            return "300-325°C"
        else:
            return "325-350°C"

    df['temperature_class'] = df['temperature_c'].apply(temp_to_class)

    return df

def plot_comparison(original_img, map_pixels, temp_map, valid_mask, output_path):
    """Plot original image next to reconstructed temperature map."""
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))

    # Original image
    axes[0].imshow(original_img)
    axes[0].set_title('Original SMU Map', fontsize=14, fontweight='bold')
    axes[0].axis('off')

    # Extracted map area
    axes[1].imshow(map_pixels)
    axes[1].set_title('Extracted Map Area', fontsize=14, fontweight='bold')
    axes[1].axis('off')

    # Reconstructed temperature map
    im = axes[2].imshow(temp_map, cmap='YlOrRd', vmin=25, vmax=350)
    axes[2].set_title('Digitized Temperature Map', fontsize=14, fontweight='bold')
    axes[2].axis('off')

    # Add colorbar
    cbar = plt.colorbar(im, ax=axes[2], orientation='vertical', pad=0.02)
    cbar.set_label('Temperature (°C)', fontsize=11)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"\n✅ Comparison plot saved: {output_path}")
    plt.close()

def digitize_smu_map(image_path, depth_km):
    """
    Complete digitization pipeline for one SMU map.
    """
    print(f"\n{'='*80}")
    print(f"DIGITIZING: {image_path.name}")
    print('='*80)

    # 1. Load and analyze image
    img, img_array = analyze_image_structure(image_path)

    # 2. Build temperature legend
    legend = build_temperature_legend()
    print(f"\nTemperature legend: {len(legend['colors'])} color classes")

    # 3. Extract map bounds
    bounds = extract_map_bounds(img_array)

    # 4. Extract map pixels
    map_pixels = extract_map_pixels(img_array, bounds)

    # 5. Classify pixels to temperature values
    temp_map, valid_mask = classify_pixels(map_pixels, legend, max_distance=60)

    # 6. Georeference
    lat_grid, lon_grid = georeference_map(temp_map, bounds)

    # 7. Create gridded dataset
    df = create_gridded_dataset(temp_map, lat_grid, lon_grid, depth_km, valid_mask)

    print(f"\n✅ Gridded dataset created: {len(df):,} points")
    print(f"   Temperature range: {df['temperature_c'].min():.1f}°C to {df['temperature_c'].max():.1f}°C")

    # 8. Plot comparison
    comparison_path = PLOT_DIR / f"smu_digitized_{depth_km}km_comparison.png"
    plot_comparison(img_array, map_pixels, temp_map, valid_mask, comparison_path)

    # 9. Save data
    csv_path = OUTPUT_DIR / f"smu_digitized_{depth_km}km.csv"
    df.to_csv(csv_path, index=False)
    print(f"✅ Data saved: {csv_path}")

    return df, temp_map

def main():
    print("SMU Temperature Map Digitization")
    print("="*80)

    # Start with one map as prototype
    prototype_map = Path("data/raw/smu/images/smu_2011_6point5km_temperature.png")
    depth_km = 6.5

    if not prototype_map.exists():
        print(f"❌ ERROR: Map not found: {prototype_map}")
        return

    # Digitize prototype
    df, temp_map = digitize_smu_map(prototype_map, depth_km)

    # Display sample data
    print(f"\n{'='*80}")
    print("SAMPLE DATA (first 10 points)")
    print('='*80)
    print(df.head(10).to_string(index=False))

    print(f"\n{'='*80}")
    print("TEMPERATURE STATISTICS")
    print('='*80)
    print(df['temperature_c'].describe())

    print(f"\n{'='*80}")
    print("PROTOTYPE COMPLETE")
    print('='*80)
    print(f"✅ Successfully digitized {prototype_map.name}")
    print(f"   Output: {OUTPUT_DIR / f'smu_digitized_{depth_km}km.csv'}")
    print(f"   Comparison: {PLOT_DIR / f'smu_digitized_{depth_km}km_comparison.png'}")

    # Ask if user wants to process all maps
    print(f"\n💡 To digitize all 7 SMU depth maps, run:")
    print(f"   python3 digitize_all_smu_maps.py")

if __name__ == "__main__":
    main()

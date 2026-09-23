#!/usr/bin/env python3
"""
Digitize the SMU 2011 temperature-at-depth maps (7.5, 8.5, 10 km).

Georeferencing: the SMU maps are drawn in a Lambert Conformal Conic projection
(ESRI:102004). Each map's pixel<->projected-coordinate relationship is a pure affine,
fitted per layer by aligning the maps' drawn state borders to US Census state
boundaries via iterative-closest-point (see smu_registration/ for the fit + diagnostic
report). Registration accuracy is ~3 km median / ~9 km 90th percentile, cross-validated.

This REPLACES an earlier plate-carree (linear lat/lon) assumption that mis-registered
by ~28 km median and pushed hot zones offshore. The affine coefficients below are the
frozen output of that fit and make this script self-contained: run it once and get
correctly georeferenced data. No separate regeneration step.

Only the 7.5/8.5/10 km maps are processed. The 3.5-6.5 km maps use a different image
layout (1381 vs 1665 px wide) and are not covered by these affines; the downstream
analysis (calculate_depth_to_300c.py) uses only 7.5/8.5/10 km, filling from the
authoritative Stanford model at shallower depths.
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pyproj
from PIL import Image
from pathlib import Path
from scipy.spatial.distance import cdist

# Output directories
OUTPUT_DIR = Path("data/processed/smu_digitized")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

PLOT_DIR = Path("plots")
PLOT_DIR.mkdir(exist_ok=True)

# --- Georeferencing constants (frozen ICP-affine fit; see smu_registration/) ---
# Projection the SMU maps are drawn in:
SMU_CRS = "ESRI:102004"  # USA Contiguous Lambert Conformal Conic
# Forward affine per layer maps Lambert (X,Y) metres -> full-image pixel (px, py):
#   px = ax[0]*X + ax[1]*Y + ax[2]
#   py = ay[0]*X + ay[1]*Y + ay[2]
# We invert it to go pixel -> Lambert, then reproject Lambert -> WGS84.
LAMBERT_AFFINES = {
    7.5: {"ax": [2.74791908e-04, 2.41211792e-06, 8.20347718e+02],
          "ay": [1.22852193e-06, -2.81582807e-04, 5.81215644e+02]},
    8.5: {"ax": [2.74760464e-04, 2.36986206e-06, 8.20308385e+02],
          "ay": [1.22872771e-06, -2.81566251e-04, 5.81225875e+02]},
    10.0: {"ax": [2.74834460e-04, 2.46452084e-06, 8.20366216e+02],
           "ay": [1.22750341e-06, -2.81562016e-04, 5.81188281e+02]},
}
# SMU logo occupies this full-image pixel box; exclude it so it is not digitized:
LOGO_BOX = {"x0": 230, "x1": 450, "y0": 895}  # x in [x0,x1), y >= y0

_TO_WGS84 = pyproj.Transformer.from_crs(SMU_CRS, "EPSG:4326", always_xy=True)


def build_temperature_legend():
    """Build color-to-temperature mapping from the SMU legend."""
    legend = [
        ((0, 100, 0), 25, 50, 37.5, "25-50°C"),
        ((0, 180, 0), 50, 75, 62.5, "50-75°C"),
        ((100, 255, 0), 75, 100, 87.5, "75-100°C"),
        ((200, 255, 0), 100, 125, 112.5, "100-125°C"),
        ((255, 255, 0), 125, 150, 137.5, "125-150°C"),
        ((255, 200, 0), 150, 175, 162.5, "150-175°C"),
        ((255, 150, 0), 175, 200, 187.5, "175-200°C"),
        ((255, 100, 0), 200, 225, 212.5, "200-225°C"),
        ((255, 50, 0), 225, 250, 237.5, "225-250°C"),
        ((255, 0, 0), 250, 275, 262.5, "250-275°C"),
        ((200, 0, 100), 275, 300, 287.5, "275-300°C"),
        ((150, 0, 150), 300, 325, 312.5, "300-325°C"),
        ((100, 0, 200), 325, 350, 337.5, "325-350°C"),
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
    """Estimate the map area boundaries (also drops the legend colorbar at right)."""
    height, width = img_array.shape[:2]
    bounds = {
        'top': 80,
        'bottom': height - 60,
        'left': 50,
        'right': width - 180
    }
    return bounds

def classify_pixels(map_pixels, legend, max_distance=60):
    """Classify each map pixel to the closest temperature class."""
    height, width = map_pixels.shape[:2]
    n_pixels = height * width

    pixels_flat = map_pixels.reshape(n_pixels, 3)
    distances = cdist(pixels_flat.astype(float), legend['colors'].astype(float), metric='euclidean')

    closest_indices = np.argmin(distances, axis=1)
    closest_distances = np.min(distances, axis=1)

    valid_mask = closest_distances <= max_distance

    temp_classified = np.full(n_pixels, np.nan)
    # Use upper bin value for optimistic resource assessment
    temp_classified[valid_mask] = legend['temp_high'][closest_indices[valid_mask]]

    temp_map = temp_classified.reshape(height, width)

    return temp_map, valid_mask.reshape(height, width)

def georeference_pixels(full_px, full_py, depth_km):
    """Convert full-image pixel coordinates to (lat, lon) via the per-layer Lambert
    affine, then reproject to WGS84.

    full_px, full_py are pixel coordinates in the ORIGINAL image (not the crop): the
    caller must add the crop offset (bounds['left'], bounds['top']) before calling.
    """
    aff = LAMBERT_AFFINES[depth_km]
    ax, ay = aff['ax'], aff['ay']
    # Forward affine: pixel = A @ [X, Y] + offset. Invert to recover Lambert X, Y.
    A = np.array([[ax[0], ax[1]], [ay[0], ay[1]]])
    offset = np.array([ax[2], ay[2]])
    XY = (np.column_stack([full_px, full_py]) - offset) @ np.linalg.inv(A).T
    lon, lat = _TO_WGS84.transform(XY[:, 0], XY[:, 1])
    return lat, lon

def temp_to_class(temp):
    """Map a temperature value to its SMU class label (upper-bin convention)."""
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

def digitize_smu_map(image_path, depth_km, legend):
    """Complete digitization pipeline for one SMU map."""
    print(f"\nProcessing {image_path.name}...")

    # Load image
    img = Image.open(image_path)
    img_array = np.array(img)

    # Extract map bounds and pixels
    bounds = extract_map_bounds(img_array)
    map_pixels = img_array[bounds['top']:bounds['bottom'], bounds['left']:bounds['right'], :3]

    # Classify pixels
    temp_map, valid_mask = classify_pixels(map_pixels, legend)

    # Full-image pixel coordinates for every crop pixel
    ch, cw = valid_mask.shape
    rr, cc = np.mgrid[0:ch, 0:cw]
    full_px = cc.ravel() + bounds['left']
    full_py = rr.ravel() + bounds['top']

    # Drop the SMU logo pixels (they can color-match the legend and are not data)
    logo = ((full_px >= LOGO_BOX['x0']) & (full_px < LOGO_BOX['x1'])
            & (full_py >= LOGO_BOX['y0']))
    keep = valid_mask.ravel() & (~logo)

    full_px = full_px[keep].astype(float)
    full_py = full_py[keep].astype(float)
    temps = temp_map.ravel()[keep]

    # Georeference via the corrected Lambert affine
    lat, lon = georeference_pixels(full_px, full_py, depth_km)

    df = pd.DataFrame({
        'lat': lat,
        'lon': lon,
        'depth_km': depth_km,
        'temperature_c': temps,
    })
    df['temperature_class'] = df['temperature_c'].apply(temp_to_class)

    n_valid = len(df)
    pct = (n_valid / valid_mask.size) * 100
    print(f"  Classified: {n_valid:,}/{valid_mask.size:,} pixels ({pct:.1f}%)")
    print(f"  Temperature range: {df['temperature_c'].min():.1f}°C to {df['temperature_c'].max():.1f}°C")
    print(f"  Lat {df['lat'].min():.2f}..{df['lat'].max():.2f}  Lon {df['lon'].min():.2f}..{df['lon'].max():.2f}")

    return df

def main():
    print("="*80)
    print("DIGITIZING SMU TEMPERATURE-AT-DEPTH MAPS (Lambert-corrected)")
    print("="*80)

    # Deep SMU maps covered by the fitted affines (1665-wide layout).
    smu_maps = [
        ("data/raw/smu/images/smu_2011_7point5km_temperature.png", 7.5),
        ("data/raw/smu/images/smu_2011_8point5km_temperature.png", 8.5),
        ("data/raw/smu/images/smu_2011_10km_temperature.png", 10.0),
    ]

    # Build legend once
    legend = build_temperature_legend()

    # Process all maps
    all_data = []

    for image_path, depth_km in smu_maps:
        image_path = Path(image_path)

        if not image_path.exists():
            print(f"⚠️  Warning: {image_path.name} not found, skipping...")
            continue

        df = digitize_smu_map(image_path, depth_km, legend)

        # Save individual file
        csv_path = OUTPUT_DIR / f"smu_digitized_{depth_km}km.csv"
        df.to_csv(csv_path, index=False)
        print(f"  ✅ Saved: {csv_path.name}")

        all_data.append(df)

    # Combine all depths into one file
    print("\n" + "="*80)
    print("COMBINING ALL DEPTHS")
    print("="*80)

    combined_df = pd.concat(all_data, ignore_index=True)

    # Save combined dataset
    combined_csv = OUTPUT_DIR / "smu_digitized_all_depths.csv"
    combined_df.to_csv(combined_csv, index=False)

    combined_parquet = OUTPUT_DIR / "smu_digitized_all_depths.parquet"
    combined_df.to_parquet(combined_parquet, index=False)

    print(f"\n✅ Combined CSV: {combined_csv}")
    print(f"✅ Combined Parquet: {combined_parquet}")

    # Summary statistics
    print("\n" + "="*80)
    print("SUMMARY STATISTICS")
    print("="*80)

    print(f"\nTotal grid points: {len(combined_df):,}")
    print(f"\nPoints per depth:")
    print(combined_df.groupby('depth_km').size().to_string())

    print(f"\nTemperature statistics by depth:")
    stats = combined_df.groupby('depth_km')['temperature_c'].agg(['min', 'median', 'mean', 'max', 'count'])
    print(stats.to_string())

    print(f"\nLocations reaching ≥300°C:")
    for depth in sorted(combined_df['depth_km'].unique()):
        df_depth = combined_df[combined_df['depth_km'] == depth]
        n_hot = (df_depth['temperature_c'] >= 300).sum()
        pct = (n_hot / len(df_depth)) * 100
        print(f"  {depth:4.1f} km: {n_hot:6,} points ({pct:5.2f}%)")

    # Create overview plot
    print("\n" + "="*80)
    print("CREATING OVERVIEW PLOT")
    print("="*80)

    depths = sorted(combined_df['depth_km'].unique())
    n_depths = len(depths)

    fig, axes = plt.subplots(n_depths, 1, figsize=(12, 4*n_depths))
    if n_depths == 1:
        axes = [axes]

    for idx, depth in enumerate(depths):
        df_depth = combined_df[combined_df['depth_km'] == depth]

        ax = axes[idx]
        scatter = ax.scatter(df_depth['lon'], df_depth['lat'],
                           c=df_depth['temperature_c'],
                           s=1, cmap='YlOrRd', vmin=25, vmax=350)

        ax.set_xlabel('Longitude', fontsize=11)
        ax.set_ylabel('Latitude', fontsize=11)
        ax.set_title(f'SMU Digitized Temperature at {depth} km Depth',
                    fontsize=12, fontweight='bold')
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.3)

        cbar = plt.colorbar(scatter, ax=ax, orientation='horizontal',
                          pad=0.05, aspect=40, shrink=0.8)
        cbar.set_label('Temperature (°C)', fontsize=10)

    plt.tight_layout()
    overview_path = PLOT_DIR / "smu_digitized_all_depths.png"
    plt.savefig(overview_path, dpi=150, bbox_inches='tight')
    print(f"✅ Overview plot saved: {overview_path}")
    plt.close()

    print("\n" + "="*80)
    print("DIGITIZATION COMPLETE")
    print("="*80)
    print(f"\n📁 Individual files: {OUTPUT_DIR}/")
    print(f"📁 Plots: {PLOT_DIR}/")
    print(f"\n✅ Successfully digitized {len(depths)} SMU depth maps")
    print(f"✅ Total grid points: {len(combined_df):,}")

if __name__ == "__main__":
    main()

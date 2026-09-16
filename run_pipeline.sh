#!/bin/bash
set -e

echo "=========================================="
echo "Running Geothermal Analysis Pipeline (V2)"
echo "=========================================="

# Use venv Python
PYTHON=.venv/bin/python

echo ""
echo "Step 1: Calculate depth to 300°C (with cross-validation)..."
$PYTHON calculate_depth_to_300c.py

echo ""
echo "Step 2: Create heatmap..."
$PYTHON create_heatmap.py

echo ""
echo "Step 3: Create final maps (points and interactive)..."
$PYTHON create_final_map.py

echo ""
echo "Step 4: Create combined metrics plot..."
$PYTHON create_combined_metrics_plot.py

echo ""
echo "Step 5: Create energy visualizations..."
$PYTHON create_energy_visualizations.py

echo ""
echo "Step 6: Create coal overlay map..."
$PYTHON create_coal_overlay_map.py

echo ""
echo "=========================================="
echo "Pipeline Complete!"
echo "=========================================="
echo ""
echo "Generated files:"
ls -lh plots/*.png | tail -10

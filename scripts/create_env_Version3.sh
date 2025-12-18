#!/usr/bin/env bash
# create_env.sh
# Create and configure a conda environment for the AUS_Land_Clearing project.
#
# Usage:
#   # Make executable first if needed:
#   chmod +x create_env.sh
#   # Run (recommended to 'source' so conda activation persists in your shell):
#   source ./create_env.sh
#   # Or if you want a custom name / python:
#   source ./create_env.sh my-env 3.9
#
# Notes:
# - It's recommended to 'source' this script (not run it) so the `conda activate`
#   in the script affects your current shell. If you run it without sourcing,
#   you will still get an environment created but the script's conda activation
#   will not persist in your shell session.
# - If you are on Windows use the create_env.bat file (Anaconda Prompt) instead.

set -euo pipefail

ENV_NAME="${1:-dea-env}"
PYVER="${2:-3.9}"
CONDA_FORGE_PKGS=(geopandas rasterio xarray numpy shapely fiona imageio pyyaml jupyterlab)
REQ_FILE="requirements.txt"

echo "=== Create conda env: $ENV_NAME (python $PYVER) ==="

# Ensure conda is available
if ! command -v conda >/dev/null 2>&1; then
    echo "ERROR: conda not found in PATH. Please install Miniconda/Anaconda and run 'conda init' in your shell."
    exit 1
fi

# Initialize conda in this script (so conda activate works)
CONDA_BASE="$(conda info --base 2>/dev/null || true)"
if [ -n "$CONDA_BASE" ] && [ -f "$CONDA_BASE/etc/profile.d/conda.sh" ]; then
    # shellcheck source=/dev/null
    . "$CONDA_BASE/etc/profile.d/conda.sh"
else
    echo "Warning: Could not locate conda.sh to initialise conda in this shell. 'conda activate' may fail."
fi

# Create the environment (if it already exists, conda create will fail; we handle that gracefully)
if conda env list | awk '{print $1}' | grep -q "^${ENV_NAME}$"; then
    echo "Conda environment '$ENV_NAME' already exists. Skipping create step."
else
    echo "Creating environment $ENV_NAME..."
    conda create -n "$ENV_NAME" python="$PYVER" -y
fi

echo "Installing core geospatial packages from conda-forge into $ENV_NAME..."
conda install -n "$ENV_NAME" -c conda-forge "${CONDA_FORGE_PKGS[@]}" -y

# If requirements.txt exists, pip install it inside the env
if [ -f "$REQ_FILE" ]; then
    echo "Pip installing from $REQ_FILE into $ENV_NAME..."
    # Use conda run to run pip inside the env (works even if not activated)
    conda run -n "$ENV_NAME" python -m pip install --upgrade pip
    conda run -n "$ENV_NAME" python -m pip install -r "$REQ_FILE"
else
    echo "No $REQ_FILE found in repo root; skipping pip install step."
fi

echo "Installing ipykernel and registering Jupyter kernel for this environment..."
conda run -n "$ENV_NAME" python -m pip install ipykernel || true
conda run -n "$ENV_NAME" python -m ipykernel install --user --name "$ENV_NAME" --display-name "Python ($ENV_NAME)"

echo ""
echo "=== Done. Activation instructions ==="
echo "To use the environment in this shell session (if you sourced this script you are probably already activated):"
echo "  conda activate $ENV_NAME"
echo ""
echo "If you didn't 'source' this script, run:"
echo "  conda activate $ENV_NAME"
echo ""
echo "Then start Jupyter Lab/Notebook and pick the kernel 'Python ($ENV_NAME)':"
echo "  jupyter lab"
echo ""
echo "Notes:"
echo "- On Windows, run the create_env.bat in an Anaconda Prompt (script included separately)."
echo "- If you plan to run heavy DEA/ODC operations, consider creating this env on the workstation (64GB RAM) rather than on a small laptop."
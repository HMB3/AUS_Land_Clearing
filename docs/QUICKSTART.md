# Quick Start Guide

Get started with AUS Land Clearing visualization in 5 minutes!

## Prerequisites

- Python 3.8 or higher
- Git
- 4GB+ RAM recommended

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/HMB3/AUS_Land_Clearing.git
cd AUS_Land_Clearing
```

### 2. Set Up Python Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Install Package

```bash
pip install -e .
```

## Basic Usage

### Example 1: Load Configuration

```python
from aus_land_clearing.utils import load_config, get_study_area_bbox, get_time_range

# Load configuration
config = load_config()
print(config['study_area']['name'])

# Get Queensland bounding box
bbox = get_study_area_bbox('queensland')
print(f"Queensland bbox: {bbox}")

# Get time range
start_year, end_year = get_time_range()
print(f"Analysis period: {start_year}-{end_year}")
```

### Example 2: Using Google Earth Engine (Quickest Start)

```python
from aus_land_clearing.data import initialize_gee, load_gee_landsat_fc, export_gee_timeseries

# First time: Authenticate GEE
# Run in terminal: earthengine authenticate

# Initialize GEE
initialize_gee()

# Load data from GEE (no local storage needed)
data = load_gee_landsat_fc(
    bbox=[138.0, -29.2, 154.0, -10.0],  # Queensland
    time_range=('2020-01-01', '2023-12-31'),
    cloud_cover=30
)

# Export time series
ts = export_gee_timeseries(
    data,
    variable='NDVI',
    output_path='ndvi_timeseries.csv'
)

print(f"Exported {len(ts)} observations")
```

**Note**: GEE is recommended for getting started quickly as it requires no local data downloads.
start_year, end_year = get_time_range()
print(f"Analysis period: {start_year}-{end_year}")
```

### Example 2: Data Access (requires DEA setup)

```python
from aus_land_clearing.data import load_dea_fractional_cover

# Define parameters
bbox = [138.0, -29.2, 154.0, -10.0]  # Queensland
time_range = ('2020-01-01', '2020-12-31')

# Load data
ds = load_dea_fractional_cover(
    bbox=bbox,
    time_range=time_range,
    bands=['PV', 'NPV', 'BS']
)
```

**Note**: This requires DEA datacube setup. See [DATA_SOURCES.md](docs/DATA_SOURCES.md) for details.

### Example 3: Time-Series Analysis

```python
from aus_land_clearing.processing import extract_time_series, calculate_change_statistics

# Extract time series
ts = extract_time_series(ds, variable='PV', method='mean')

# Calculate change
stats = calculate_change_statistics(
    ds,
    variable='PV',
    baseline_period=('2015-01-01', '2017-12-31'),
    comparison_period=('2020-01-01', '2020-12-31')
)

print(f"Change: {stats['percent_change']:.2f}%")
```

### Example 4: Create Visualizations

```python
from aus_land_clearing.visualization import create_time_series_plot, create_animation

# Time series plot
create_time_series_plot(
    ts,
    variable='PV',
    title='Vegetation Cover',
    output_path='vegetation_timeseries.png'
)

# Animation
create_animation(
    ds,
    variable='PV',
    output_path='vegetation_change.mp4',
    fps=2
)
```

## Using Jupyter Notebooks

Launch Jupyter and explore the example notebooks:

```bash
jupyter notebook
```

Navigate to the `notebooks/` directory and open:

1. **01_data_access.ipynb** - Learn how to access data
2. **02_time_series_analysis.ipynb** - Process and analyze time series
3. **03_visualization.ipynb** - Create plots and animations
4. **04_narrative_stories.ipynb** - Build story-driven visualizations

## Configuration

Edit `config.yaml` to customize:

- Study area boundaries
- Time period (default: 1988-2024)
- Data source settings
- Output formats and parameters

Example customization:

```yaml
time_period:
  start_year: 2000  # Change from 1988
  end_year: 2023    # Change from 2024
  
outputs:
  animations:
    fps: 5  # Faster animation
    dpi: 150  # Lower resolution for testing
```

## Directory Structure

```
AUS_Land_Clearing/
├── config.yaml           # Main configuration file
├── src/                  # Source code
├── data/                 # Data storage
│   ├── raw/             # Raw data downloads
│   ├── processed/       # Processed datasets
│   └── outputs/         # Generated visualizations
├── notebooks/           # Jupyter notebooks
└── docs/               # Documentation
```

## Data Access Setup

### Option 1: DEA Datacube (Full Access)

```bash
# Install datacube
pip install datacube

# Initialize
datacube system init

# Configure
datacube system check
```

See [DATA_SOURCES.md](docs/DATA_SOURCES.md) for detailed setup.

### Option 2: Sample Data (Quick Start)

For testing without DEA access, you can work with the template functions that demonstrate the workflow:

```python
# These will return empty datasets with warnings
# but demonstrate the interface
from aus_land_clearing.data import load_dea_fractional_cover

ds = load_dea_fractional_cover(bbox, time_range)
# Returns: UserWarning with setup instructions
```

## Common Issues

### Issue: ModuleNotFoundError

**Solution**: Make sure virtual environment is activated and dependencies installed:
```bash
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### Issue: Config file not found

**Solution**: Run Python from the project root directory:
```bash
cd AUS_Land_Clearing
python your_script.py
```

### Issue: DEA data access fails

**Solution**: Check datacube configuration:
```bash
datacube system check
```

See [DATA_SOURCES.md](docs/DATA_SOURCES.md) for DEA setup guide.

## Next Steps

1. **Explore the documentation** in `docs/` directory
2. **Run example notebooks** to learn the workflow
3. **Customize configuration** in `config.yaml`
4. **Load your own data** or set up DEA access
5. **Create visualizations** for your area of interest

## Getting Help

- **Documentation**: See `docs/` directory
- **Examples**: See `notebooks/` directory
- **Issues**: Open an issue on GitHub
- **Data Sources**: See `docs/DATA_SOURCES.md`

## Quick Commands Reference

```bash
# Activate environment
source venv/bin/activate

# Install/update dependencies
pip install -r requirements.txt

# Launch Jupyter
jupyter notebook

# Run Python script
python my_analysis.py

# Deactivate environment
deactivate
```

Happy analyzing! 🌏🌳

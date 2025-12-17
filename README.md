# AUS Land Clearing

Story-driven visualisations of land clearing across eastern Australia (Queensland + NSW) from 1988 to present.

## Overview

This project provides tools and workflows for analyzing and visualizing land clearing patterns in eastern Australia using authoritative remote sensing datasets. The focus is on creating compelling, narrative-driven visualizations rather than developing new remote sensing methods.

## Features

- **Dual Data Access**: Flexible data source options
  - **DEA (Digital Earth Australia)**: Authoritative Australian products
    - DEA Land Cover (25m, annual)
    - DEA Fractional Cover (PV, NPV, BS)
  - **Google Earth Engine (GEE)**: Global cloud-based access
    - Landsat Collection 2 (30m, 1984-present)
    - Sentinel-2 (10m, 2015-present)
  - **SLATS**: Queensland-specific woody vegetation data

- **Time-Series Analysis**: Process and analyze land cover changes from 1988 to present
  - Extract temporal statistics
  - Calculate change metrics
  - Detect clearing events
  - Aggregate by time periods (annual, seasonal, monthly)

- **Data Export**: Clean, analysis-ready outputs
  - Simple time-series plots for quality checking
  - CSV/JSON exports for narrative visualization tools
  - Focused on data preparation, not complex plotting
  - Reusable workflows transferable to other regions

## Project Structure

```
AUS_Land_Clearing/
├── src/aus_land_clearing/     # Source code
│   ├── data/                  # Data access modules
│   ├── processing/            # Time-series processing
│   ├── visualization/         # Visualization tools
│   ├── utils/                 # Configuration and utilities
│   └── dea_processor.py       # DEA annual landcover processor
├── scripts/                   # Processing scripts
│   ├── run_dea_processing.py  # Run DEA landcover processing
│   └── fetch_australian_state_geojson.py  # Download state boundaries
├── gee/                       # Google Earth Engine scripts
│   └── dea_annual_landcover_nsw_qld.js  # GEE export template
├── data/                      # Data storage
│   ├── raw/                   # Raw data downloads
│   ├── processed/             # Processed datasets
│   ├── outputs/               # Generated outputs
│   ├── nsw.geojson           # NSW boundary
│   └── qld.geojson           # QLD boundary
├── notebooks/                 # Jupyter notebooks for analysis
│   └── 0-demo-dea-processing.ipynb  # DEA workflow demo
├── tests/                     # Unit tests
│   └── test_dea_processor.py  # DEA processor tests
├── docs/                      # Documentation
├── config.yaml                # Configuration file
└── requirements.txt           # Python dependencies
```

## Installation

### Prerequisites

- Python 3.8 or higher
- Git

### Setup

1. Clone the repository:
```bash
git clone https://github.com/HMB3/AUS_Land_Clearing.git
cd AUS_Land_Clearing
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install the package in development mode:
```bash
pip install -e .
```

## Configuration

The project uses a YAML configuration file (`config.yaml`) to manage settings:

- **Study Area**: Queensland and NSW boundaries
- **Time Period**: 1988 to present (configurable)
- **Data Sources**: DEA and SLATS endpoints
- **Output Settings**: Animation parameters, figure formats

Edit `config.yaml` to customize these settings for your analysis.

## DEA Annual Landcover Processing

This repository now includes comprehensive support for processing **Digital Earth Australia (DEA) Annual Landcover** products to produce woody/non-woody vegetation classifications for NSW and Queensland from 1988 to present.

### What is DEA Annual Landcover?

DEA Annual Landcover is an authoritative Australia-wide land cover classification product produced by Geoscience Australia. It provides:
- **Coverage**: Continental Australia
- **Resolution**: 25m spatial resolution
- **Temporal**: Annual composites from 1988 to present
- **Classes**: Multiple land cover classes including woody vegetation, crops, urban, water, bare soil
- **Source**: Landsat satellite imagery processed through the Open Data Cube
- **Documentation**: https://www.dea.ga.gov.au/products/dea-land-cover

### Processing Routes

This repository provides **two processing routes** for DEA Annual Landcover:

#### 1. Python/Open Data Cube Route (Recommended for production)
- Uses `datacube` and `odc-stac` Python libraries
- Access data via DEA's STAC catalog or local datacube instance
- Full control over processing pipeline
- Suitable for batch processing and automation
- See `scripts/run_dea_processing.py` and `src/aus_land_clearing/dea_processor.py`

#### 2. Google Earth Engine Route (Alternative for cloud processing)
- Uses Google Earth Engine JavaScript API
- Cloud-based processing and export
- Exports to Google Drive or Earth Engine Assets
- Good for interactive exploration and prototyping
- See `gee/dea_annual_landcover_nsw_qld.js`

### Required Credentials and Setup

**For Python/ODC Route:**
```bash
# Install DEA dependencies
pip install datacube odc-stac pystac-client

# Option A: Use DEA STAC catalog (no authentication required)
# The scripts default to this method

# Option B: Set up local Open Data Cube (advanced)
datacube system init
# Follow DEA datacube setup guide: https://knowledge.dea.ga.gov.au/
```

**For Google Earth Engine Route:**
```bash
# Install Earth Engine
pip install earthengine-api

# Authenticate (one-time setup)
earthengine authenticate

# Initialize in your script
import ee
ee.Initialize()
```

### Step-by-Step Workflow

#### Step 1: Fetch Study Area Boundaries

Download official Australian state boundaries:

```bash
python scripts/fetch_australian_state_geojson.py
```

This creates:
- `data/nsw.geojson` - New South Wales boundary
- `data/qld.geojson` - Queensland boundary
- `data/australian_states.geojson` - All states (reference)

#### Step 2: Configure Processing Parameters

Edit `config.yaml` to customize the DEA processing profile:

```yaml
dea_annual_landcover:
  product_id: "ga_ls_landcover_class_cyear_2"
  start_year: 1988
  end_year: 2024
  crs: "EPSG:3577"  # Australian Albers
  resolution: 25
  output_dir: "data/outputs/dea_landcover"
  # ... see config.yaml for full options
```

#### Step 3: Run Processing (Python Route)

Process DEA data for NSW and QLD:

```bash
# Process both states for full time period (1988-present)
python scripts/run_dea_processing.py

# Process specific state and time range
python scripts/run_dea_processing.py --state nsw --start-year 2000 --end-year 2020

# Add buffer around state boundary (reduces edge artifacts)
python scripts/run_dea_processing.py --buffer 5000  # 5km buffer
```

This produces:
- `data/outputs/dea_landcover/nsw/landcover_1988.tif` (and one per year)
- `data/outputs/dea_landcover/qld/landcover_1988.tif` (and one per year)
- `data/outputs/dea_landcover/nsw/animation.gif` (animated time series)
- `data/outputs/dea_landcover/qld/animation.gif` (animated time series)

#### Step 4: View Results

Open the demonstration notebook:

```bash
jupyter notebook notebooks/0-demo-dea-processing.ipynb
```

### Class Mapping: DEA to Woody/Non-Woody

The processing scripts reclassify DEA's detailed land cover classes into a simplified woody/non-woody scheme:

| Output Class | Value | DEA Source Classes |
|--------------|-------|-------------------|
| Woody vegetation | 1 | Woody vegetation (dense, sparse), Forest |
| Non-woody vegetation | 2 | Grassland, Cropland, Wetland vegetation |
| Other/Masked | 0 | Water, Bare soil, Urban, Clouds, No data |

You can customize this mapping in `config.yaml` under `dea_annual_landcover.classes_map`.

### Recommended Sweeps

**Sweep 1 (Current)**: Template scripts and core functionality
- ✅ Documentation and configuration
- ✅ Python processing module (`dea_processor.py`)
- ✅ Runnable scripts with AOI support
- ✅ GEE JavaScript template
- ✅ Basic unit tests

**Sweep 2 (Planned)**: Enhanced processing and validation
- Improve STAC/datacube data fetching with error handling
- Add data quality checks and cloud masking
- Validate outputs against reference datasets
- Performance optimization for large areas

**Sweep 3 (Planned)**: Visualization and analysis
- Enhanced animation generation with legends and annotations
- R scripts for publication-quality figures
- Change detection analysis (clearing events, regrowth)
- Integration with narrative visualization tools

## Usage

### Option 1: Using DEA (Australia-specific)

```python
from aus_land_clearing import (
    load_dea_fractional_cover,
    extract_time_series,
)
from aus_land_clearing.utils import get_study_area_bbox, get_time_range

# Define study area (Queensland)
bbox = get_study_area_bbox('queensland')
time_range = ('2020-01-01', '2023-12-31')

# Load DEA data
ds = load_dea_fractional_cover(bbox, time_range, bands=['PV'])

# Extract time series
ts = extract_time_series(ds, variable='PV', method='mean')

# Export for visualization in other tools
ts.to_csv('outputs/vegetation_timeseries.csv', index=False)
```

### Option 2: Using Google Earth Engine (Global)

```python
from aus_land_clearing.data import (
    initialize_gee,
    load_gee_landsat_fc,
    export_gee_timeseries
)

# Initialize GEE (requires authentication)
initialize_gee()

# Load Landsat data
data = load_gee_landsat_fc(
    bbox=[138.0, -29.2, 154.0, -10.0],
    time_range=('2020-01-01', '2023-12-31'),
    cloud_cover=30
)

# Export NDVI time series
ts = export_gee_timeseries(
    data,
    variable='NDVI',
    output_path='outputs/gee_ndvi_timeseries.csv'
)
```

### Processing Workflow

1. **Load Data**: Choose DEA (Australia) or GEE (Global)
2. **Process**: Apply time-series analysis and change detection
3. **Export**: Generate clean CSV/JSON for narrative visualization tools

### Example Notebooks

Check the `notebooks/` directory for example workflows:

- `01_data_access.ipynb`: DEA data access patterns
- `02_time_series_analysis.ipynb`: Time-series processing
- `03_visualization.ipynb`: Basic plots for QA/QC
- `04_narrative_stories.ipynb`: Data export for narrative viz
- `05_google_earth_engine.ipynb`: GEE data access (global capability)

## Data Sources

### DEA (Australia-Specific)

**DEA Land Cover**
- **Coverage**: Australia-wide
- **Resolution**: 25m
- **Temporal**: Annual (1988-present)
- **URL**: https://www.dea.ga.gov.au/products/dea-land-cover

**DEA Fractional Cover**
- **Coverage**: Australia-wide
- **Resolution**: 25m
- **Temporal**: Monthly (1987-present)
- **Bands**: PV (green vegetation), NPV (dry vegetation), BS (bare soil)
- **URL**: https://www.dea.ga.gov.au/products/dea-fractional-cover

**SLATS (Queensland Only)**
- **Coverage**: Queensland
- **Resolution**: 30m
- **Temporal**: Biennial (1988-present)
- **URL**: https://www.qld.gov.au/environment/land/management/mapping/statewide-monitoring/slats

### Google Earth Engine (Global)

**Landsat Collection 2**
- **Coverage**: Global
- **Resolution**: 30m
- **Temporal**: 16-day revisit (1984-present)
- **Access**: Cloud-based via GEE

**Sentinel-2**
- **Coverage**: Global
- **Resolution**: 10m
- **Temporal**: 5-day revisit (2015-present)
- **Access**: Cloud-based via GEE

## Data Access Setup

### DEA Setup (Australia)

1. **DEA Datacube**: Install and configure Open Data Cube
   ```bash
   pip install datacube
   datacube system init
   ```

2. **Credentials**: Set up DEA authentication (if required)

3. **STAC Access**: Alternative access via STAC catalog
   ```python
   from pystac_client import Client
   catalog = Client.open('https://explorer.sandbox.dea.ga.gov.au/stac/')
   ```

For SLATS data, download from Queensland Government spatial data portal.

### GEE Setup (Global)

1. **Install GEE libraries**:
   ```bash
   pip install earthengine-api geemap
   ```

2. **Authenticate** (first time only):
   ```bash
   earthengine authenticate
   ```

3. **Initialize in Python**:
   ```python
   from aus_land_clearing.data import initialize_gee
   initialize_gee()
   ```

## Design Philosophy

This repository follows key principles:

1. **Simple, reusable functions** - Wrappers around established scientific methods
2. **Data preparation focus** - Generate clean exports for narrative visualization tools
3. **Dual capability** - Both DEA (authoritative Australian data) and GEE (global transferability)
4. **Basic plotting only** - Advanced visualization happens in dedicated tools/repos
5. **Build, don't discard** - Extend existing work rather than replacing it

## References

See `docs/REFERENCES.md` for comprehensive list of resources including:
- DEA documentation and guides
- GEE tools (geemap, rgee)
- Scientific publications
- Example repositories
- Community resources

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is released under the MIT License. See LICENSE file for details.

## Acknowledgments

- Digital Earth Australia for providing land cover data
- Queensland Government for SLATS data
- Geoscience Australia for spatial data infrastructure

## Contact

For questions or collaboration opportunities, please open an issue on GitHub.

## Citation

If you use this tool in your research, please cite:

```
AUS Land Clearing Visualization Tool (2024)
GitHub repository: https://github.com/HMB3/AUS_Land_Clearing
```

## References

- DEA Land Cover: https://www.dea.ga.gov.au/products/dea-land-cover
- DEA Fractional Cover: https://www.dea.ga.gov.au/products/dea-fractional-cover
- SLATS: https://www.qld.gov.au/environment/land/management/mapping/statewide-monitoring/slats
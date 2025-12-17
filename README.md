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
│   └── utils/                 # Configuration and utilities
├── data/                      # Data storage
│   ├── raw/                   # Raw data downloads
│   ├── processed/             # Processed datasets
│   └── outputs/               # Generated outputs
├── notebooks/                 # Jupyter notebooks for analysis
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

## Usage

### Quick Start: DEA Annual Land Cover Processing

This repository includes templates and scripts for processing Digital Earth Australia (DEA) annual land cover products for NSW and QLD (1988–present).

#### Step 1: Download State Boundaries

```bash
python scripts/fetch_australian_state_geojson.py
```

This downloads NSW and QLD boundaries from GADM and saves them as GeoJSON files.

#### Step 2: Run DEA Processing

```bash
# Process all years for both states
python scripts/run_dea_processing.py

# Process only NSW
python scripts/run_dea_processing.py --state nsw

# Process specific year range
python scripts/run_dea_processing.py --years 2020-2023
```

**Note**: The data fetching backend (`fetch_dea_raster_for_year()`) is a template function that needs to be implemented with your preferred method:
- Open Data Cube (ODC) - if you have a datacube instance
- STAC API - using `odc-stac` and `pystac_client`
- Direct download - from DEA's data repository

See `src/aus_land_clearing/dea_processor.py` for implementation guidance.

#### Step 3: Explore in Notebook

Open `notebooks/0-demo-dea-processing.ipynb` for an interactive walkthrough.

### Processing Routes

This repository provides **two complementary processing routes**:

#### Route 1: Python / Open Data Cube (Recommended for DEA)
- **Best for**: Native DEA product access, reproducible workflows, batch processing
- **Tools**: Python, datacube, odc-stac, rasterio, xarray
- **Data sources**: DEA Land Cover, DEA Fractional Cover via ODC or STAC
- **Scripts**: `scripts/run_dea_processing.py`, `src/aus_land_clearing/dea_processor.py`
- **Status**: Template implemented (sweep-1), data fetching to be completed (sweep-2)

#### Route 2: Google Earth Engine (Alternative for Global Data)
- **Best for**: Cloud-based processing, global datasets, quick exploration
- **Tools**: JavaScript, Google Earth Engine Code Editor
- **Data sources**: ESA WorldCover, Dynamic World, Landsat (DEA not directly available in GEE)
- **Scripts**: `gee/dea_annual_landcover_nsw_qld.js`
- **Status**: Template provided with alternative datasets

### Advanced Usage

#### Option 1: Using DEA (Australia-specific)

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

#### Option 2: Using Google Earth Engine (Global)

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

### Required Credentials and Setup

#### For DEA Processing (Python/ODC Route)

**Option A: Open Data Cube (Local/Server)**

If you have access to a server with DEA datacube configured:

1. Install datacube:
   ```bash
   pip install datacube
   ```

2. Configure datacube connection (if needed):
   ```bash
   datacube system init
   ```

3. Check available products:
   ```bash
   datacube product list | grep landcover
   ```

**Option B: STAC API (Recommended for Most Users)**

No credentials required for read-only access:

1. Install STAC libraries:
   ```bash
   pip install odc-stac pystac-client
   ```

2. Access DEA STAC catalog:
   ```python
   from pystac_client import Client
   catalog = Client.open('https://explorer.dea.ga.gov.au/stac/')
   ```

3. No authentication needed for public DEA data

**Option C: Direct Download**

Download GeoTIFFs directly from DEA's data repository. See DEA documentation for access details.

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

## Recommended Next Steps (Future Sweeps)

### Sweep-2: Implement Data Fetching Backend
- Implement `fetch_dea_raster_for_year()` using ODC or STAC
- Add connection configuration and authentication
- Test with real DEA annual land cover data
- Add error handling and retry logic
- Implement data caching for efficiency

### Sweep-3: Enhanced Processing
- Add parallel processing for multiple years
- Implement progress tracking and logging
- Add validation checks for output quality
- Extend to additional states (VIC, SA, WA)
- Add support for sub-annual temporal resolution

### Sweep-4: Advanced Visualizations
- Interactive web-based visualizations
- Enhanced animation options (MP4, WebM)
- Comparison tools (before/after, state-to-state)
- Integration with narrative visualization platforms

### Sweep-5: Production Deployment
- Containerization (Docker)
- Cloud deployment guides (AWS, NCI)
- Automated CI/CD pipeline
- Performance optimization for large-scale processing

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
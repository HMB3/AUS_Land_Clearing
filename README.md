# AUS Land Clearing

Story-driven visualisations of land clearing across eastern Australia (Queensland + NSW) from 1988 to present.

## Overview

This project provides tools and workflows for analyzing and visualizing land clearing patterns in eastern Australia using authoritative remote sensing datasets. The focus is on creating compelling, narrative-driven visualizations rather than developing new remote sensing methods.

## Features

- **Data Integration**: Access to multiple authoritative data sources
  - DEA (Digital Earth Australia) Land Cover
  - DEA Fractional Cover (PV, NPV, BS)
  - SLATS (Statewide Landcover and Trees Study - Queensland)

- **Time-Series Analysis**: Process and analyze land cover changes from 1988 to present
  - Extract temporal statistics
  - Calculate change metrics
  - Detect clearing events
  - Aggregate by time periods (annual, seasonal, monthly)

- **Visualization Tools**: Create story-driven visualizations
  - Time-series plots
  - Animated maps showing change over time
  - Before/after comparisons
  - Multi-temporal displays
  - Change detection maps

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

### Basic Example

```python
from aus_land_clearing import (
    load_dea_fractional_cover,
    extract_time_series,
    create_time_series_plot,
    create_animation
)
from aus_land_clearing.utils import get_study_area_bbox, get_time_range

# Define study area (Queensland)
bbox = get_study_area_bbox('queensland')

# Define time range
start_year, end_year = get_time_range()
time_range = (f'{start_year}-01-01', f'{end_year}-12-31')

# Load data
ds = load_dea_fractional_cover(bbox, time_range, bands=['PV'])

# Extract time series
ts = extract_time_series(ds, variable='PV', method='mean')

# Create visualization
create_time_series_plot(
    ts, 
    variable='PV',
    title='Photosynthetic Vegetation - Queensland',
    output_path='outputs/qld_pv_timeseries.png'
)

# Create animation
create_animation(
    ds,
    variable='PV',
    output_path='outputs/qld_vegetation_change.mp4',
    fps=2
)
```

### Processing Workflow

1. **Load Data**: Use data loaders to access DEA or SLATS datasets
2. **Process**: Apply time-series analysis and change detection
3. **Visualize**: Create plots, animations, and narrative visualizations
4. **Export**: Save results in various formats

### Example Notebooks

Check the `notebooks/` directory for example workflows:

- `01_data_access.ipynb`: How to access different data sources
- `02_time_series_analysis.ipynb`: Time-series processing examples
- `03_visualization.ipynb`: Creating visualizations and animations
- `04_narrative_stories.ipynb`: Story-driven visualization examples

## Data Sources

### DEA Land Cover
- **Coverage**: Australia-wide
- **Resolution**: 25m
- **Temporal**: Annual (1988-present)
- **URL**: https://www.dea.ga.gov.au/products/dea-land-cover

### DEA Fractional Cover
- **Coverage**: Australia-wide
- **Resolution**: 25m
- **Temporal**: Monthly (1987-present)
- **Bands**: PV (green vegetation), NPV (dry vegetation), BS (bare soil)
- **URL**: https://www.dea.ga.gov.au/products/dea-fractional-cover

### SLATS (Queensland Only)
- **Coverage**: Queensland
- **Resolution**: 30m
- **Temporal**: Biennial (1988-present)
- **URL**: https://www.qld.gov.au/environment/land/management/mapping/statewide-monitoring/slats

## Data Access Setup

To access DEA data, you'll need:

1. **DEA Datacube**: Install and configure Open Data Cube
   ```bash
   pip install datacube
   datacube system init
   ```

2. **Credentials**: Set up DEA authentication (if required)

3. **STAC Access**: Alternative access via STAC catalog
   ```python
   from pystac_client import Client
   catalog = Client.open('https://explorer.digitalearth.africa/stac/')
   ```

For SLATS data, download from Queensland Government spatial data portal.

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
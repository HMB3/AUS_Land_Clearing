# Australian Land Clearing Visualization Project

Story-driven visualizations of land clearing across eastern Australia (Queensland + NSW) from 1988 to present, using Google Earth Engine and authoritative remote sensing products.

## Project Overview

This project provides a complete workflow for generating clean, repeatable time-series visualizations of land clearing in eastern Australia. The focus is on narrative and design, using existing authoritative products (DEA Land Cover, DEA Fractional Cover, SLATS) rather than inventing new remote-sensing methods.

### Key Features

- **Modular Google Earth Engine scripts** for reproducible analysis
- **Multi-scale analysis**: Continental overview + regional case studies
- **Annual time-series** from 1988 to present (Landsat-era)
- **Consistent projection**: EPSG:3577 (Australian Albers Equal Area)
- **Multiple outputs**: GeoTIFF frames, MP4 animations, time-series data
- **Case studies**: Moree Plains (NSW), Brigalow Belt (QLD)

## Quick Start

### Prerequisites

1. **Google Earth Engine account** - Sign up at [https://earthengine.google.com](https://earthengine.google.com)
2. **DEA/SLATS data assets** - Upload or access via GEE Community Catalog
3. **Basic JavaScript knowledge** - For customizing workflows

### Basic Workflow

1. **Configure data sources** in `gee_scripts/core/config.js`:
   ```javascript
   // Update asset paths with your actual data
   exports.DEA_LAND_COVER.ASSET_ID = 'projects/YOUR_PROJECT/assets/dea_land_cover';
   ```

2. **Run main workflow** in GEE Code Editor:
   - Open `gee_scripts/main_workflow.js`
   - Select region and time period in WORKFLOW_CONFIG
   - Run script and check Tasks tab for exports

3. **Generate visualizations**:
   - GeoTIFF frames → External tools (Python/R/After Effects)
   - MP4 animations → Direct from GEE for quick previews

## Repository Structure

```
AUS_Land_Clearing/
├── gee_scripts/                    # Google Earth Engine JavaScript modules
│   ├── core/                       # Core functionality
│   │   ├── config.js              # Global configuration
│   │   └── utils.js               # Utility functions
│   ├── case_studies/              # Regional analysis scripts
│   │   ├── moree_plains_nsw.js    # NSW Moree Plains case study
│   │   └── brigalow_belt_qld.js   # QLD Brigalow Belt case study
│   └── main_workflow.js           # Main orchestration script
├── docs/                          # Documentation
│   ├── DATA_SOURCES.md           # Data source descriptions
│   ├── CONFIGURATION.md          # Configuration guide
│   └── USAGE_EXAMPLES.md         # Usage examples
├── examples/                      # Example outputs and templates
└── README.md                      # This file
```

## Data Sources

### Primary Sources

1. **DEA Land Cover (Landsat)** - Annual land cover classifications for Australia
   - Resolution: ~25-30m
   - Coverage: 1988-present
   - Source: Digital Earth Australia (GEE Community Catalog)

2. **DEA Fractional Cover** - Vegetation fraction estimates
   - Bands: Green vegetation / Non-green vegetation / Bare soil
   - Resolution: ~25-30m
   - Source: Digital Earth Australia

3. **SLATS** - Woody vegetation clearing data
   - QLD SLATS: Landsat-based (1988+) and Sentinel-2 (2015+)
   - NSW SEED: SLATS-equivalent clearing polygons
   - Source: State government agencies

### Reference Documentation

- [Digital Earth Australia Knowledge Hub](https://knowledge.dea.ga.gov.au/)
- [DEA Land Cover Product Description](https://knowledge.dea.ga.gov.au/data/product/dea-land-cover-landsat/)
- [Queensland SLATS](https://www.qld.gov.au/environment/land/management/mapping/slats)

## Configuration

The project uses a centralized configuration system in `gee_scripts/core/config.js`. Key parameters include:

### Spatial Settings

```javascript
// Projection: Australian Albers Equal Area
PROJECTION.crs = 'EPSG:3577'
PROJECTION.scale = 25  // meters

// Predefined regions
CONTINENTAL_DOMAIN        // Eastern Australia
REGIONAL_DOMAINS.MOREE_PLAINS      // NSW case study
REGIONAL_DOMAINS.BRIGALOW_BELT     // QLD case study
```

### Temporal Settings

```javascript
TIME_PERIOD.PRIMARY_START = '1988-01-01'
TIME_PERIOD.PRIMARY_END = '2024-12-31'
```

### Classification Schemes

The workflow simplifies detailed land cover classes into meaningful categories:

- **Woody Vegetation**: Trees, shrubs, woody vegetation
- **Non-Woody Vegetation**: Grasses, crops, herbaceous vegetation
- **Bare/Sparse**: Bare soil, sparse vegetation
- **Water**: Water bodies
- **Urban/Built**: Urban and built-up areas

See [CONFIGURATION.md](docs/CONFIGURATION.md) for detailed options.

## Usage Examples

### Example 1: Continental Overview

Generate a continental-scale animation of woody vegetation change:

```javascript
// In main_workflow.js
var WORKFLOW_CONFIG = {
  region: config.CONTINENTAL_DOMAIN,
  regionName: 'continental',
  startYear: '1988',
  endYear: '2023',
  scale: config.SCALES.SMOOTH_ANIMATION,  // 60m for smoother animation
  exportVideo: true
};
```

### Example 2: Regional Case Study

Analyze clearing in a specific region with high detail:

```javascript
// Run case_studies/moree_plains_nsw.js or brigalow_belt_qld.js
// These scripts are pre-configured for regional analysis
```

### Example 3: Custom Region

Define your own study area:

```javascript
var myRegion = ee.Geometry.Rectangle([lon1, lat1, lon2, lat2]);

var customConfig = {
  region: myRegion,
  regionName: 'my_study_area',
  startYear: '2000',
  endYear: '2020',
  scale: 25
};
```

See [USAGE_EXAMPLES.md](docs/USAGE_EXAMPLES.md) for more examples.

## Outputs

### Export Formats

1. **GeoTIFF Frames** (Annual)
   - Cloud-optimized GeoTIFF
   - EPSG:3577 projection
   - Use for external visualization tools

2. **MP4 Animations**
   - 1920px resolution (HD)
   - 2 frames per second (configurable)
   - Direct preview from GEE

3. **CSV Time Series**
   - Annual woody vegetation area statistics
   - Use for charts and analysis

### Output Organization

```
Google Drive/
└── AUS_Land_Clearing/
    ├── geotiff_frames/
    ├── animations/
    ├── moree_plains/
    ├── brigalow_belt_qld/
    └── timeseries_data/
```

## Scientific Assumptions

This workflow makes several key assumptions that are documented in the code:

1. **Clearing Definition**: Conversion of woody vegetation (trees/shrubs) to non-woody vegetation or bare soil
2. **Woody Vegetation**: All forest and shrubland classes from DEA Land Cover (>20% canopy cover)
3. **Temporal Compositing**: Annual medians to reduce noise and cloud contamination
4. **Change Detection**: Simple temporal comparison (woody → non-woody = clearing)
5. **Data Quality**: DEA products are pre-processed; SLATS provides validation

See code comments in `config.js` and `utils.js` for detailed scientific assumptions.

## Case Studies

### Moree Plains, NSW

Major agricultural region in northwestern NSW with significant clearing for cotton and wheat production.

**Key themes:**
- Agricultural expansion (1988-present)
- Irrigation agriculture development
- Cotton boom impacts

**Run:** `gee_scripts/case_studies/moree_plains_nsw.js`

### Brigalow Belt, QLD

One of Australia's most extensively cleared ecosystems, focal point for vegetation management debates.

**Key themes:**
- Historical brigalow scrub clearing
- Impact of vegetation management laws
- Policy timeline (2000-2018)

**Run:** `gee_scripts/case_studies/brigalow_belt_qld.js`

## Workflow Design Philosophy

1. **Visual clarity over complexity**: Smooth, cloud-free composites with stable color ramps
2. **Explicit assumptions**: All scientific assumptions documented in comments
3. **Modular architecture**: Easy to swap data products or update workflows
4. **Reproducibility**: Consistent projection, naming conventions, and configuration

## Customization

The modular design makes it easy to:

- Add new regions (define in `config.js`)
- Change time periods (update `WORKFLOW_CONFIG`)
- Swap data products (update asset IDs in `config.js`)
- Modify classification schemes (edit `LAND_COVER_CLASSES`)
- Adjust export parameters (update `EXPORT_CONFIG`)

## Troubleshooting

### Common Issues

1. **Asset not found**: Update asset paths in `config.js` with your actual GEE assets
2. **Memory errors**: Reduce scale or region size for large exports
3. **Cloud contamination**: Adjust `MAX_CLOUD_COVER` threshold in config
4. **Slow exports**: Use coarser scale for animations, fine scale for final products

### Tips

- Start with small regions and short time periods for testing
- Use `print()` statements to debug
- Check GEE Task Manager for export status
- Monitor computation usage in GEE console

## Contributing

This is a template project designed to be customized for your specific needs. Key areas for extension:

- Additional case study regions
- Alternative data products
- Enhanced change detection algorithms
- Integration with ground-truth data
- Temporal smoothing techniques

## References

### Code Patterns

- [GeoscienceAustralia/dea-notebooks](https://github.com/GeoscienceAustralia/dea-notebooks) - DEA usage patterns
- [calekochenour/gee-vegetation-change](https://github.com/calekochenour/gee-vegetation-change) - GEE change detection
- [mioash/lc_cover_australia](https://github.com/mioash/lc_cover_australia) - Australian land cover analysis

### Data Products

- [Digital Earth Australia](https://www.dea.ga.gov.au/)
- [Queensland SLATS](https://www.qld.gov.au/environment/land/management/mapping/slats)
- [NSW SEED Portal](https://www.seed.nsw.gov.au/)

## License

This project provides a framework for land clearing analysis. Please ensure you comply with the licenses of the underlying data products (DEA, SLATS) when using this code.

## Contact

For questions about this workflow, please refer to:
- [Google Earth Engine Community](https://developers.google.com/earth-engine)
- [Digital Earth Australia Support](https://www.dea.ga.gov.au/about/contact-us)
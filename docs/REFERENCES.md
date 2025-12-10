# References and Resources

This document contains links to key resources, scientific papers, and tools that inform and support the AUS Land Clearing project.

## Digital Earth Australia (DEA) Resources

### Official DEA Documentation

**DEA Land Cover Product**
- Product Page: https://knowledge.dea.ga.gov.au/notebooks/DEA_products/DEA_Land_Cover/
- Land Cover Change Mapping Guide: https://knowledge.dea.ga.gov.au/notebooks/How_to_guides/Land_cover_change_mapping/
- Land Cover Tools: https://knowledge.dea.ga.gov.au/notebooks/Tools/gen/dea_tools.landcover/

**DEA Fractional Cover**
- Fractional Cover Percentiles: https://knowledge.dea.ga.gov.au/data/product/dea-fractional-cover-percentiles-landsat/

### DEA Tools and Libraries
- dea_tools package with land cover utilities
- Open Data Cube (ODC) for data access
- STAC catalog for metadata discovery

## SLATS (Queensland)

**Statewide Landcover and Trees Study**
- SLATS Data Portal: https://www.qld.gov.au/environment/land/management/mapping/statewide-monitoring/slats/slats-data
- Queensland Government spatial data
- Woody vegetation extent, clearing, and regrowth products

## Google Earth Engine (GEE) Resources

### GEE Tools and Libraries

**geemap - Python Package for GEE**
- GitHub: https://github.com/gee-community/geemap
- Interactive mapping and analysis
- Export utilities and visualization tools
- Integration with Jupyter notebooks

**rgee - R Package for GEE**
- GitHub: https://github.com/r-spatial/rgee
- R interface to Google Earth Engine
- Spatial data analysis in R

### GEE Datasets
- Landsat Collection 2 (30m, 1984-present)
- Sentinel-2 (10m, 2015-present)
- MODIS vegetation products
- Global land cover datasets

## Scientific Publications

### Land Cover and Forest Change

**Remote Sensing and Land Cover**
- MDPI - Remote Sensing Data: https://www.mdpi.com/2306-5729/4/4/143
  - Special issue on land cover and remote sensing data

**Forest Cover Change Analysis**
- ScienceDirect Article: https://www.sciencedirect.com/science/article/pii/S0264837720325813
  - Methods and applications for forest change detection

**Geospatial Big Data**
- Springer Book: https://link.springer.com/book/10.1007/978-3-031-26588-4
  - Comprehensive guide to geospatial big data analysis
  - Remote sensing and earth observation techniques

## Code Repositories and Examples

### Fractional Cover Implementations

**GitLab - Fractional Cover Theme**
- Repository: https://gitlab.com/jrsrp/themes/cover/fractionalcover3
- Fractional cover algorithms and processing
- Queensland-specific implementations

### Land Cover Classification

**Landsat 30m Australia**
- GitHub: https://github.com/papersubmit1/landsat30-au
- High-resolution land cover for Australia
- Landsat-based classification methods

**Forest Cover Change Detection**
- GitHub: https://github.com/BzGEO/forest_cover_change
- Change detection algorithms
- Time-series analysis methods

## Key Concepts and Methods

### Fractional Cover
Fractional cover represents the proportion of:
- **PV (Photosynthetic Vegetation)**: Green, actively photosynthesizing vegetation
- **NPV (Non-Photosynthetic Vegetation)**: Dry vegetation, senescent material, litter
- **BS (Bare Soil)**: Exposed soil, rock, or non-vegetated surfaces

Where: PV + NPV + BS = 100%

### Land Cover Change Detection
Methods used in this project:
1. **Time-series analysis** - Track vegetation changes over time
2. **Threshold-based detection** - Identify significant changes
3. **Temporal compositing** - Reduce noise and cloud contamination
4. **Spectral indices** - NDVI, NDMI, EVI for vegetation monitoring

### Data Sources Comparison

| Source | Resolution | Temporal | Coverage | Access |
|--------|-----------|----------|----------|--------|
| DEA Land Cover | 25m | Annual | Australia | DEA/ODC |
| DEA Fractional Cover | 25m | Monthly | Australia | DEA/ODC |
| SLATS | 30m | Biennial | Queensland | QLD Gov |
| Landsat (GEE) | 30m | 16-day | Global | GEE |
| Sentinel-2 (GEE) | 10m | 5-day | Global | GEE |

## Workflow Integration

### DEA Workflow
1. Access data via ODC or STAC
2. Load time-series for study area
3. Process and analyze
4. Export results

### GEE Workflow
1. Authenticate with GEE
2. Filter collections by location and date
3. Compute indices and composites
4. Export to Drive or download

### Hybrid Approach
- Use DEA for Australia-specific authoritative products
- Use GEE for:
  - Global context and comparisons
  - Higher temporal resolution (Sentinel-2)
  - Quick prototyping and exploration
  - Large-scale batch processing

## Best Practices

### Data Selection
- **DEA**: Best for Australia, authoritative products, policy-relevant
- **GEE**: Best for global analysis, rapid iteration, cloud processing
- **SLATS**: Best for Queensland woody vegetation, detailed clearing data

### Processing
- Keep functions simple and modular
- Focus on data preparation for visualization
- Use established methods from scientific community
- Document data lineage and processing steps

### Visualization
- Export clean time-series data
- Generate simple plots for QA/QC
- Leave advanced visualization to dedicated tools
- Focus on narrative-ready outputs

## Additional Resources

### Learning Materials
- GEE JavaScript Guide: https://developers.google.com/earth-engine/tutorials
- GEE Python API: https://developers.google.com/earth-engine/guides/python_install
- DEA Notebooks: https://knowledge.dea.ga.gov.au/notebooks/
- ODC Documentation: https://www.opendatacube.org/

### Community
- GEE Developers Forum: https://groups.google.com/g/google-earth-engine-developers
- DEA User Community
- SLATS User Support: Queensland Government

## Citation Guidelines

When using these resources, please cite appropriately:

**DEA Products:**
```
© Commonwealth of Australia (Geoscience Australia) [Year]
Digital Earth Australia [Product Name]
https://www.dea.ga.gov.au/
```

**SLATS:**
```
© State of Queensland (Department of Environment and Science) [Year]
Statewide Landcover and Trees Study (SLATS)
https://www.qld.gov.au/environment/land/management/mapping/statewide-monitoring/slats
```

**Google Earth Engine:**
```
Gorelick, N., Hancher, M., Dixon, M., Ilyushchenko, S., Thau, D., & Moore, R. (2017).
Google Earth Engine: Planetary-scale geospatial analysis for everyone.
Remote Sensing of Environment, 202, 18-27.
```

## Updates

This document will be updated as new resources become available or methods evolve. 

Last updated: 2024-12-10

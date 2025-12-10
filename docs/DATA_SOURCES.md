# Data Sources Documentation

This document provides detailed information about the data sources used in the AUS Land Clearing project.

## Digital Earth Australia (DEA) Products

### Overview
Digital Earth Australia (DEA) provides free and open access to Earth observation data and analysis-ready satellite imagery for Australia.

Website: https://www.dea.ga.gov.au/

### DEA Land Cover

**Product Name**: ga_ls_landcover_class_cyear_2

**Description**: Annual land cover classification for Australia derived from Landsat satellite data.

**Key Characteristics**:
- **Spatial Coverage**: Continental Australia
- **Spatial Resolution**: 25 meters
- **Temporal Coverage**: 1988 to present
- **Temporal Resolution**: Annual
- **Update Frequency**: Annual
- **CRS**: EPSG:3577 (Australian Albers Equal Area)

**Land Cover Classes**:
1. Artificial surfaces
2. Cultivated terrestrial vegetation
3. Natural terrestrial vegetation
4. Natural aquatic vegetation
5. Water
6. Bare areas

**Access Methods**:
1. DEA Datacube (requires installation)
2. STAC API
3. AWS S3 (public bucket)
4. NCI (for Australian researchers)

**Citation**:
```
Lymburner, L., et al. (2020). Land cover classification of Australia.
Digital Earth Australia. https://doi.org/10.4225/25/5d4d8fcd4d56e
```

### DEA Fractional Cover

**Product Name**: ga_ls_fc_3

**Description**: Fractional cover data showing the proportion of photosynthetic vegetation (PV), non-photosynthetic vegetation (NPV), and bare soil (BS).

**Key Characteristics**:
- **Spatial Coverage**: Continental Australia
- **Spatial Resolution**: 25 meters
- **Temporal Coverage**: 1987 to present
- **Temporal Resolution**: 16-day (Landsat revisit)
- **Update Frequency**: Near real-time
- **CRS**: EPSG:3577 (Australian Albers Equal Area)

**Bands/Measurements**:
- **PV**: Photosynthetic (green) vegetation (0-100%)
- **NPV**: Non-photosynthetic (dry) vegetation (0-100%)
- **BS**: Bare soil (0-100%)

Note: PV + NPV + BS = 100% at each pixel

**Use Cases**:
- Monitoring vegetation health
- Detecting land clearing
- Assessing grazing pressure
- Tracking seasonal vegetation changes
- Drought monitoring

**Access Methods**:
1. DEA Datacube
2. STAC API
3. AWS S3
4. DEA Sandbox (JupyterHub)

**Citation**:
```
Scarth, P., et al. (2015). Tracking grazing pressure and climate interaction -
the role of Landsat fractional cover in time series analysis.
Proceedings of the 16th Australasian Remote Sensing and Photogrammetry Conference.
```

## SLATS (Statewide Landcover and Trees Study)

### Overview
SLATS is Queensland's long-term land cover change monitoring program, operated by the Queensland Department of Environment and Science.

Website: https://www.qld.gov.au/environment/land/management/mapping/statewide-monitoring/slats

**Key Characteristics**:
- **Spatial Coverage**: Queensland only
- **Spatial Resolution**: 30 meters (Landsat-based)
- **Temporal Coverage**: 1988 to present
- **Temporal Resolution**: Biennial (every 2 years)
- **Update Frequency**: Biennial

**Products**:

1. **Woody Vegetation Extent**
   - Maps extent of woody vegetation
   - Updated biennially

2. **Woody Vegetation Clearing**
   - Identifies areas of woody vegetation clearing
   - Distinguishes clearing methods (pulled, blade ploughed, etc.)

3. **Woody Vegetation Regrowth**
   - Maps areas of vegetation regrowth
   - Important for carbon accounting

4. **Remnant Vegetation**
   - Pre-clearing (1750s) extent
   - Current remnant extent
   - Biodiversity values

**Access Methods**:
1. Queensland Government Spatial Catalogue
2. WMS/WFS services
3. Direct download (GeoTIFF, Shapefile)
4. QSpatial platform

**Data Availability**:
- Historical reports: 1988-1989 onwards
- Digital data: Various formats
- API access: Limited

**Citation**:
```
Department of Environment and Science (2024). Queensland land cover change
and woody vegetation clearing (SLATS). Queensland Government.
```

## Study Area Boundaries

### Queensland
- **Bounding Box**: [138.0, -29.2, 154.0, -10.0] (WGS84)
- **Area**: ~1.85 million km²
- **EPSG**: 7856 (GDA2020 / MGA zone 56)

### New South Wales
- **Bounding Box**: [140.9, -38.0, 153.6, -28.1] (WGS84)
- **Area**: ~809,000 km²
- **EPSG**: 7856 (GDA2020 / MGA zone 56)

### Combined Study Area
- **Bounding Box**: [138.0, -38.0, 154.0, -10.0] (WGS84)
- **Area**: ~2.66 million km²

## Data Access Setup

### DEA Datacube Setup

1. Install datacube:
```bash
pip install datacube
```

2. Initialize datacube:
```bash
datacube system init
```

3. Add products:
```bash
datacube product add https://explorer.dea.ga.gov.au/products/ga_ls_landcover_class_cyear_2.odc-product.yaml
datacube product add https://explorer.dea.ga.gov.au/products/ga_ls_fc_3.odc-product.yaml
```

4. Index datasets (this can take time):
```bash
datacube dataset add --auto-add-lineage <dataset_yaml>
```

### Alternative: STAC API Access

```python
from pystac_client import Client

# Connect to DEA STAC catalog
catalog = Client.open('https://explorer.sandbox.dea.ga.gov.au/stac/')

# Search for data
search = catalog.search(
    collections=['ga_ls_fc_3'],
    bbox=[138.0, -29.2, 154.0, -10.0],
    datetime='1988-01-01/2024-12-31'
)

items = search.get_all_items()
```

### SLATS Data Access

1. Visit Queensland Government Spatial Portal:
   https://qldspatial.information.qld.gov.au/

2. Search for "SLATS" or "woody vegetation"

3. Download datasets in preferred format:
   - GeoTIFF (raster)
   - Shapefile (vector)
   - GeoPackage (vector)

4. Load in Python:
```python
import rasterio
import geopandas as gpd

# Raster data
with rasterio.open('slats_woody_extent.tif') as src:
    data = src.read(1)

# Vector data
gdf = gpd.read_file('slats_clearing.shp')
```

## Data Licensing

### DEA Products
- **License**: Creative Commons Attribution 4.0 International (CC BY 4.0)
- **Attribution**: "© Commonwealth of Australia (Geoscience Australia)"
- **Commercial Use**: Permitted
- **Modifications**: Permitted

### SLATS
- **License**: Creative Commons Attribution 4.0 International (CC BY 4.0)
- **Attribution**: "© State of Queensland (Department of Environment and Science)"
- **Commercial Use**: Permitted
- **Modifications**: Permitted

## Data Quality Considerations

### Temporal Consistency
- All products use Landsat data (consistent spectral characteristics)
- Be aware of sensor changes: Landsat 5, 7, 8, 9
- Cloud masking quality varies by product

### Spatial Accuracy
- DEA products: ~25m positional accuracy
- SLATS: ~30m positional accuracy
- Consider resampling for consistent resolution

### Temporal Gaps
- Cloud cover can cause gaps
- Landsat 7 SLC-off (2003+) affects coverage
- SLATS has biennial updates (gaps between)

### Validation
- DEA products validated against field data
- SLATS validated through aerial photography
- Consider local validation for specific applications

## Further Reading

1. **DEA User Guide**: https://knowledge.dea.ga.gov.au/
2. **SLATS Methodology**: https://www.qld.gov.au/environment/land/management/mapping/statewide-monitoring/slats/about
3. **Landsat Science**: https://landsat.gsfc.nasa.gov/
4. **Open Data Cube**: https://www.opendatacube.org/

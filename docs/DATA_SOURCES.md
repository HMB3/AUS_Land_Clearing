# Data Sources Documentation

This document provides detailed information about the data sources used in the Australian Land Clearing Visualization project.

## Overview

The project relies on three primary authoritative data sources:

1. **DEA Land Cover** - Annual land cover classifications
2. **DEA Fractional Cover** - Vegetation fraction estimates
3. **SLATS** - Woody vegetation clearing records

All data products are accessed through Google Earth Engine (GEE) and should be reprojected to EPSG:3577 (Australian Albers Equal Area) for consistent analysis.

---

## 1. DEA Land Cover (Landsat)

### Description

Digital Earth Australia (DEA) Land Cover provides annual land cover classifications for the Australian continent derived from Landsat satellite imagery. This is the primary data source for identifying woody vegetation.

### Specifications

- **Temporal Coverage**: 1988 - present (annual)
- **Spatial Resolution**: ~25-30 meters
- **Spatial Coverage**: Australia-wide
- **Sensor**: Landsat 5 TM, Landsat 7 ETM+, Landsat 8 OLI
- **Classification System**: Hierarchical (Level 3, Level 4)
- **Update Frequency**: Annual

### Classification Scheme

DEA Land Cover uses a hierarchical classification system. For this project, we focus on **Level 3** classifications:

#### Woody Vegetation Classes (Trees & Shrubs)
- **111**: Closed Forest
- **112**: Open Forest
- **113**: Sparse Forest
- **121**: Closed Woodland
- **122**: Open Woodland
- **123**: Sparse Woodland
- **124**: Dense Shrubland
- **125**: Open Shrubland
- **126**: Sparse Shrubland

#### Non-Woody Vegetation Classes
- **211**: Dense Tussock Grassland
- **212**: Open Tussock Grassland
- **213**: Sparse Tussock Grassland
- **214**: Dense Hummock Grassland
- **215**: Open Hummock Grassland
- **216**: Sparse Hummock Grassland

#### Other Classes
- **221-223**: Bare areas (bare soil, bare rock, etc.)
- **311-315**: Water bodies (aquatic vegetation, natural water, artificial water, etc.)
- **411-412**: Urban and built-up areas

### Access

**GEE Community Catalog** (when available):
```javascript
var deaLandCover = ee.ImageCollection('projects/dea-public/assets/land_cover');
```

**Direct Asset Upload**:
1. Download from [DEA Knowledge Hub](https://knowledge.dea.ga.gov.au/data/product/dea-land-cover-landsat/)
2. Upload to your GEE Assets
3. Update path in `config.js`

### Quality & Limitations

**Strengths:**
- Validated against Australian ground truth data
- Consistent methodology across time series
- Open access and well-documented

**Limitations:**
- Annual temporal resolution (may miss sub-annual clearing events)
- Cloud contamination in tropical regions
- Mixed pixels in heterogeneous landscapes
- Classification accuracy varies by region and cover type

### Citation

Liao, Z., Van Dijk, A.I., He, B., Larraondo, P.R., & Scarth, P. (2020). *Woody vegetation cover, height and biomass at 25-m resolution across Australia derived from multiple site, airborne and satellite observations.* International Journal of Applied Earth Observation and Geoinformation, 93, 102209.

---

## 2. DEA Fractional Cover

### Description

DEA Fractional Cover provides estimates of vegetation cover fractions across Australia. It classifies each pixel into percentages of photosynthetic (green) vegetation, non-photosynthetic vegetation, and bare soil.

### Specifications

- **Temporal Coverage**: 1987 - present (all available Landsat observations)
- **Spatial Resolution**: ~25-30 meters
- **Spatial Coverage**: Australia-wide
- **Sensor**: Landsat 5 TM, Landsat 7 ETM+, Landsat 8/9 OLI
- **Temporal Resolution**: 16-day (Landsat revisit)
- **Bands**: 3 continuous bands (PV, NPV, BS)

### Bands

1. **PV (Photosynthetic Vegetation)**: Green/live vegetation percentage (0-100%)
2. **NPV (Non-Photosynthetic Vegetation)**: Dead vegetation/litter percentage (0-100%)
3. **BS (Bare Soil)**: Bare soil/rock percentage (0-100%)

Note: PV + NPV + BS ≈ 100% (may not sum exactly due to rounding/residuals)

### Use in This Project

Fractional Cover can be used as:
- **Alternative woody vegetation proxy**: High PV+NPV values may indicate woody cover
- **Background visualization**: Shows vegetation structure and seasonality
- **Validation**: Cross-check with land cover classifications

### Woody Vegetation Threshold

In `utils.js`, we provide a function to derive woody vegetation from Fractional Cover:
```javascript
// Default: Total vegetation (PV + NPV) > 20% = woody
var woody = woodyFromFractionalCover(fcImage, 20);
```

This threshold can be adjusted based on regional conditions.

### Access

**GEE Collection**:
```javascript
var deaFC = ee.ImageCollection('projects/dea-public/assets/fc');
```

### Quality & Limitations

**Strengths:**
- High temporal resolution (every clear Landsat observation)
- Continuous variables (not discrete classes)
- Captures seasonal dynamics
- Useful for detecting subtle changes

**Limitations:**
- Requires temporal compositing to reduce noise
- Threshold selection for woody vs non-woody is subjective
- Sensitive to seasonal variation
- Cloud and shadow contamination

### Citation

Scarth, P., Röder, A., Schmidt, M., & Denham, R. (2010). *Tracking grazing pressure and climate interaction - the role of Landsat fractional cover in time series analysis.* In Proceedings of the 15th Australasian Remote Sensing and Photogrammetry Conference.

---

## 3. SLATS - Statewide Landcover and Trees Study

### Description

SLATS is Queensland's long-term land cover change monitoring program. It provides authoritative records of woody vegetation clearing and regrowth. NSW has an equivalent program (SEED) that provides similar clearing polygon data.

### Queensland SLATS

#### Specifications

- **Temporal Coverage**: 1988 - present (annual for Landsat, more frequent for Sentinel-2)
- **Spatial Resolution**: Landsat (~25-30m), Sentinel-2 (~10m from 2015+)
- **Spatial Coverage**: Queensland
- **Product Type**: Vector polygons (clearing events)
- **Attributes**: Year, area, clearing type, remnant/regrowth status

#### Landsat-based SLATS (1988-present)
```javascript
var slatsQLD = ee.FeatureCollection('projects/YOUR_PROJECT/slats_qld_woody');
```

#### Sentinel-2 based SLATS (2015-present)
```javascript
var slatsQLD_S2 = ee.FeatureCollection('projects/YOUR_PROJECT/slats_qld_s2');
```

### NSW SEED

#### Specifications

- **Temporal Coverage**: Varies by data layer (typically 2000+)
- **Spatial Coverage**: New South Wales
- **Product Type**: Vector polygons
- **Source**: NSW SEED Portal

#### Access
Download from [NSW SEED Portal](https://www.seed.nsw.gov.au/) and upload to GEE:
```javascript
var slatsNSW = ee.FeatureCollection('projects/YOUR_PROJECT/nsw_clearing');
```

### Use in This Project

SLATS data serves multiple purposes:
1. **Validation**: Ground-truth for DEA-derived clearing detection
2. **Narrative anchoring**: Link clearing events to known policy/historical events
3. **Overlay visualization**: Show authoritative clearing polygons on maps
4. **Accuracy assessment**: Calculate agreement between DEA and SLATS

### Comparison with DEA Products

| Aspect | DEA Land Cover | SLATS |
|--------|---------------|-------|
| Data Type | Raster (classified imagery) | Vector (polygons) |
| Coverage | Australia-wide | State-specific |
| Methodology | Machine learning on Landsat | Manual interpretation + automated detection |
| Temporal Resolution | Annual | Annual (Landsat), sub-annual (Sentinel-2) |
| Accuracy | ~80% overall | High (ground-truthed) |
| Access | Open/free | Open (QLD), varies (NSW) |

### Quality & Limitations

**Strengths:**
- High accuracy (manually verified)
- Long time series (1988+)
- Authoritative for policy and reporting
- Includes metadata (clearing type, extent)

**Limitations:**
- State-specific (not Australia-wide)
- Polygon boundaries may differ from pixel-based detection
- Definition of "woody vegetation" varies slightly from DEA
- Not all clearing types captured (e.g., gradual thinning)

### Citations

**Queensland SLATS:**
Queensland Government (2023). *Statewide Landcover and Trees Study (SLATS).* Department of Environment and Science. https://www.qld.gov.au/environment/land/management/mapping/slats

**NSW:**
NSW Government (2023). *SEED - The Central Resource for Sharing and Enabling Environmental Data in NSW.* https://www.seed.nsw.gov.au/

---

## 4. Additional Data Sources (Optional)

### Landsat Surface Reflectance

For custom analyses or areas without DEA coverage, raw Landsat surface reflectance can be used:

```javascript
// Landsat 8 Collection 2 Level 2
var landsat8 = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2');

// Landsat 7 Collection 2 Level 2
var landsat7 = ee.ImageCollection('LANDSAT/LE07/C02/T1_L2');
```

### Sentinel-2 (2015+)

For higher resolution recent analysis:

```javascript
// Sentinel-2 Level 2A (atmospherically corrected)
var sentinel2 = ee.ImageCollection('COPERNICUS/S2_SR');
```

### MODIS Vegetation Indices

For continental-scale or daily monitoring:

```javascript
// MODIS NDVI 16-day composite
var modisNDVI = ee.ImageCollection('MODIS/006/MOD13A1');
```

---

## Data Preparation Workflow

### Step 1: Acquire Data

1. **DEA Products**: Access via GEE Community Catalog or download from DEA
2. **SLATS**: Download from state government portals
3. **Upload to GEE**: Use Earth Engine Asset Manager for local files

### Step 2: Configure Asset Paths

Update `gee_scripts/core/config.js`:

```javascript
exports.DEA_LAND_COVER.ASSET_ID = 'projects/YOUR_PROJECT/assets/dea_land_cover';
exports.DEA_FRACTIONAL_COVER.ASSET_ID = 'projects/YOUR_PROJECT/assets/dea_fc';
exports.SLATS.QLD_LANDSAT.ASSET_ID = 'projects/YOUR_PROJECT/assets/slats_qld';
```

### Step 3: Verify Data Quality

Run a quick test in GEE:

```javascript
var testImage = ee.Image(config.DEA_LAND_COVER.ASSET_ID + '/1988');
Map.addLayer(testImage, {}, 'Test 1988');
print('Image properties:', testImage.propertyNames());
```

---

## Data Update Schedule

| Product | Update Frequency | Lag Time | Check For Updates |
|---------|------------------|----------|-------------------|
| DEA Land Cover | Annual | ~6 months | DEA Knowledge Hub |
| DEA Fractional Cover | Continuous | ~1 month | GEE Collection |
| SLATS QLD | Annual | ~6-12 months | QLD Gov website |
| SLATS NSW | Varies | Varies | NSW SEED portal |

---

## Contact & Support

### Data Issues

- **DEA Products**: https://www.dea.ga.gov.au/about/contact-us
- **Queensland SLATS**: slats@des.qld.gov.au
- **NSW SEED**: seed@environment.nsw.gov.au

### GEE Technical Support

- **GEE Community**: https://groups.google.com/g/google-earth-engine-developers
- **GEE Documentation**: https://developers.google.com/earth-engine

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2024-12 | Initial documentation |

---

## Appendix: Asset Upload Instructions

### Uploading Raster Data to GEE

1. Prepare GeoTIFF files (one per year)
2. Use Earth Engine Asset Manager or `earthengine upload` CLI
3. Create an ImageCollection from uploaded assets

```bash
# Example: Upload single image
earthengine upload image --asset_id=projects/YOUR_PROJECT/dea_lc_1988 gs://YOUR_BUCKET/dea_lc_1988.tif

# Create collection
earthengine create collection projects/YOUR_PROJECT/dea_land_cover
earthengine upload image --asset_id=projects/YOUR_PROJECT/dea_land_cover/1988 gs://YOUR_BUCKET/dea_lc_1988.tif
```

### Uploading Vector Data to GEE

1. Prepare shapefile or GeoJSON
2. Upload via Asset Manager

```bash
earthengine upload table --asset_id=projects/YOUR_PROJECT/slats_qld gs://YOUR_BUCKET/slats_qld.shp
```

---

*This document is maintained as part of the Australian Land Clearing Visualization project.*

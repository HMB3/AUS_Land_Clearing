# Configuration Guide

This guide explains all configuration options available in the Australian Land Clearing Visualization project.

## Overview

Configuration is centralized in `gee_scripts/core/config.js`. This modular approach allows you to:

- Easily switch between regions and time periods
- Maintain consistent settings across analyses
- Quickly adapt workflows for new data sources
- Document scientific assumptions in one place

---

## Core Configuration Sections

### 1. Spatial Configuration

#### Projection Settings

```javascript
exports.PROJECTION = {
  crs: 'EPSG:3577',  // Australian Albers Equal Area Conic
  scale: 25          // Target resolution in meters
};
```

**EPSG:3577** is the recommended projection for Australia-wide analysis because:
- Equal-area projection (accurate area calculations)
- Optimized for Australian continent
- Standard for DEA products
- Minimizes distortion across eastern Australia

**Alternative projections:**
- `EPSG:4326` (WGS84) - for web mapping (not recommended for area calculations)
- `EPSG:28355` (GDA94 MGA Zone 55) - for regional NSW analysis
- `EPSG:28356` (GDA94 MGA Zone 56) - for regional QLD analysis

#### Scale Options

```javascript
exports.SCALES = {
  LANDSAT: 25,           // DEA Land Cover / Landsat products
  SENTINEL: 10,          // Sentinel-2 based SLATS products
  SMOOTH_ANIMATION: 60,  // Coarser for smoother animations
  CONTINENTAL: 250       // Continental overviews
};
```

**Choosing the right scale:**
- **25m**: Standard for Landsat-based analysis, balances detail and processing time
- **10m**: Higher detail for recent years (2015+) with Sentinel-2 data
- **60m**: Smoother animations with reduced file sizes
- **250m**: Fast processing for continental overviews and quick prototyping

**Trade-offs:**
- Finer resolution → More detail, larger files, slower processing
- Coarser resolution → Faster processing, smoother animations, less detail

---

### 2. Temporal Configuration

#### Primary Time Period

```javascript
exports.TIME_PERIOD = {
  PRIMARY_START: '1988-01-01',  // Start of Landsat 5 consistent record
  PRIMARY_END: '2024-12-31',    // Present
  
  EXTENDED_START: '1985-01-01', // Earlier Landsat data (spottier coverage)
  SENTINEL_START: '2015-01-01'  // Sentinel-2 era begins
};
```

**Recommended periods:**
- **1988-present**: Most robust for Landsat-based analysis
- **2000-present**: Better data quality (Landsat 7 + 8)
- **2015-present**: Sentinel-2 available for higher resolution

#### Composite Windows

```javascript
exports.COMPOSITE_WINDOWS = {
  ANNUAL: 'year',      // One composite per year
  SEASONAL: 'season',  // Four composites per year (DJF, MAM, JJA, SON)
  QUARTERLY: 'quarter' // Three-month windows
};
```

**Use cases:**
- **Annual**: Standard for long-term trends and animations
- **Seasonal**: Capture seasonal clearing patterns (e.g., post-harvest)
- **Quarterly**: Fine temporal detail for specific events

---

### 3. Spatial Domains

#### Continental Domain

```javascript
exports.CONTINENTAL_DOMAIN = ee.Geometry.Polygon(
  [[[135, -10], [155, -10], [155, -39], [135, -39], [135, -10]]],
  null, false
);
```

**Coverage**: Eastern Australia from tropical Queensland to temperate Victoria/NSW.

**Customization**:
```javascript
// Custom bounding box
var myRegion = ee.Geometry.Rectangle([west, south, east, north]);

// From existing feature
var myRegion = statesBoundary.filter(ee.Filter.eq('STATE_NAME', 'Queensland'));
```

#### Regional Domains

```javascript
exports.REGIONAL_DOMAINS = {
  MOREE_PLAINS: ee.Geometry.Polygon([...]),
  BRIGALOW_BELT: ee.Geometry.Polygon([...]),
  DARLING_DOWNS: ee.Geometry.Polygon([...])
};
```

**Adding new regions**:

```javascript
// Method 1: Rectangle
MURRAY_DARLING: ee.Geometry.Rectangle([141, -35, 150, -28])

// Method 2: Polygon (for irregular shapes)
MY_REGION: ee.Geometry.Polygon([
  [[lon1, lat1], [lon2, lat2], [lon3, lat3], [lon1, lat1]]
])

// Method 3: From shapefile (upload to GEE first)
MY_REGION: ee.FeatureCollection('users/YOUR_USERNAME/my_region').geometry()
```

---

### 4. Data Source Configuration

#### DEA Land Cover

```javascript
exports.DEA_LAND_COVER = {
  ASSET_ID: 'projects/YOUR_PROJECT/assets/dea_land_cover',
  BAND: 'level3',  // Classification band name
  START_YEAR: 1988,
  END_YEAR: 2023
};
```

**Setup steps:**
1. Upload DEA Land Cover data to GEE Assets or use Community Catalog
2. Update `ASSET_ID` with your asset path
3. Verify `BAND` name matches your data

**Checking band names:**
```javascript
var testImage = ee.Image('YOUR_ASSET/1988');
print('Band names:', testImage.bandNames());
```

#### DEA Fractional Cover

```javascript
exports.DEA_FRACTIONAL_COVER = {
  ASSET_ID: 'projects/YOUR_PROJECT/assets/dea_fractional_cover',
  BANDS: {
    GREEN: 'PV',    // Photosynthetic vegetation
    NON_GREEN: 'NPV', // Non-photosynthetic vegetation
    BARE: 'BS'      // Bare soil
  }
};
```

#### SLATS Data

```javascript
exports.SLATS = {
  QLD_LANDSAT: {
    ASSET_ID: 'projects/YOUR_PROJECT/assets/slats_qld_woody_clearing'
  },
  QLD_SENTINEL: {
    ASSET_ID: 'projects/YOUR_PROJECT/assets/slats_qld_woody_clearing_s2',
    START_YEAR: 2015
  },
  NSW_SEED: {
    ASSET_ID: 'projects/YOUR_PROJECT/assets/nsw_slats_clearing'
  }
};
```

---

### 5. Classification Schemes

#### Land Cover Classes

The classification scheme maps detailed DEA classes to simplified categories:

```javascript
exports.LAND_COVER_CLASSES = {
  WOODY: {
    name: 'Woody Vegetation',
    classes: [111, 112, 113, 121, 122, 123, 124, 125, 126],
    color: '1a5928',  // Dark green (hex)
    description: 'Trees, shrubs, and woody vegetation'
  },
  // ... additional classes
};
```

**Customizing classes:**

To adjust what counts as "woody vegetation":

```javascript
// More restrictive (only forests, exclude shrubs)
WOODY: {
  classes: [111, 112, 113, 121, 122, 123],  // Remove shrubland classes
  // ...
}

// More inclusive (include dense grasslands)
WOODY: {
  classes: [111, 112, 113, 121, 122, 123, 124, 125, 126, 211],
  // ...
}
```

**Color schemes** (hexadecimal RGB):
- Use [ColorBrewer](https://colorbrewer2.org/) for accessible palettes
- Consider colorblind-friendly schemes
- Maintain consistency across outputs

#### Binary Classification

```javascript
exports.BINARY_CLASSES = {
  WOODY: {value: 1, color: '1a5928'},
  NON_WOODY: {value: 0, color: 'e8b520'}
};
```

Used for simple woody vs. non-woody visualizations.

---

### 6. Export Configuration

#### Output Directories

```javascript
exports.EXPORT_CONFIG = {
  DRIVE_FOLDER: 'AUS_Land_Clearing',
  
  FOLDERS: {
    GEOTIFF: 'geotiff_frames',
    VIDEO: 'animations',
    THUMBNAIL: 'thumbnails',
    CONTINENTAL: 'continental',
    REGIONAL: 'regional'
  }
};
```

**Organizing outputs:**
- Keep animations separate from individual frames
- Create folders for each case study region
- Use consistent naming across exports

#### File Naming

```javascript
exports.EXPORT_CONFIG.NAMING = {
  PREFIX: 'aus_lc',
  SEPARATOR: '_',
  DATE_FORMAT: 'YYYY'
};
```

**Naming pattern**: `{PREFIX}_{REGION}_{PRODUCT}_{YEAR}.tif`

**Examples**:
- `aus_lc_continental_woody_2020.tif`
- `aus_lc_moree_plains_clearing_1988_2023.tif`

#### GeoTIFF Options

```javascript
exports.EXPORT_CONFIG.GEOTIFF = {
  fileFormat: 'GeoTIFF',
  formatOptions: {
    cloudOptimized: true,  // Enable for better web performance
    noData: -9999          // Standard no-data value
  }
};
```

**Cloud-optimized GeoTIFF benefits:**
- Faster loading in QGIS/web viewers
- Efficient partial reads
- Better compression

#### Video Options

```javascript
exports.EXPORT_CONFIG.VIDEO = {
  fileFormat: 'mp4',
  framesPerSecond: 2,  // 2 fps = 0.5 seconds per year
  dimensions: 1920,    // HD resolution
  quality: 95          // 0-100 (higher = better quality, larger file)
};
```

**Frame rate guide:**
- **1 fps**: Slow, contemplative (1 second per year)
- **2 fps**: Standard narrative pace (0.5 seconds per year)
- **4 fps**: Fast overview (0.25 seconds per year)
- **10 fps**: Very fast (suitable for 50+ year series)

---

### 7. Visualization Parameters

#### Color Palettes

```javascript
exports.VIS_PARAMS = {
  BINARY_WOODY: {
    min: 0,
    max: 1,
    palette: ['e8b520', '1a5928']  // Non-woody to woody
  },
  
  FRACTIONAL_GREEN: {
    min: 0,
    max: 100,
    palette: ['ffffff', '78d203', '1a5928']  // White to light to dark green
  },
  
  CLEARING: {
    min: 0,
    max: 1,
    palette: ['dddddd', 'ff0000']  // Grey (stable) to red (cleared)
  }
};
```

**Creating custom palettes:**

```javascript
// Sequential (for continuous data)
MY_PALETTE: {
  min: 0,
  max: 100,
  palette: ['#f7fbff', '#6baed6', '#08519c']  // Light to dark blue
}

// Diverging (for change detection)
CHANGE_PALETTE: {
  min: -100,
  max: 100,
  palette: ['#d7191c', '#ffffbf', '#2c7bb6']  // Red (loss) to blue (gain)
}
```

**Palette resources:**
- [ColorBrewer](https://colorbrewer2.org/)
- [Google Earth Engine Palettes](https://github.com/gee-community/ee-palettes)

---

### 8. Quality Control

```javascript
exports.QUALITY_CONTROL = {
  MAX_CLOUD_COVER: 20,     // Maximum acceptable cloud cover %
  MIN_OBSERVATIONS: 3,      // Minimum images for compositing
  EXCLUDE_FLAGS: ['cloud', 'cloud_shadow', 'snow']
};
```

**Adjusting quality thresholds:**

```javascript
// Strict quality (fewer images, cleaner composites)
MAX_CLOUD_COVER: 10,
MIN_OBSERVATIONS: 5

// Relaxed quality (more images, some cloud contamination)
MAX_CLOUD_COVER: 40,
MIN_OBSERVATIONS: 1

// Tropical regions (hard to get cloud-free data)
MAX_CLOUD_COVER: 50,
MIN_OBSERVATIONS: 2
```

---

## Advanced Configuration

### Custom Composite Functions

Override default compositing in your workflow:

```javascript
// Green-band maximum composite (highlights vegetation peaks)
var customComposite = collection
  .filterDate(startDate, endDate)
  .qualityMosaic('PV');  // Use max green vegetation

// Temporal linear interpolation
var interpolated = collection.map(function(img) {
  return img.interpolate(previousImg, nextImg);
});
```

### Region-Specific Parameters

Create configuration objects for different regions:

```javascript
var REGION_CONFIGS = {
  tropical: {
    MAX_CLOUD_COVER: 50,
    COMPOSITE_METHOD: 'median',
    MONTHS: [5, 6, 7, 8]  // Dry season only
  },
  temperate: {
    MAX_CLOUD_COVER: 20,
    COMPOSITE_METHOD: 'mean',
    MONTHS: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]  // All months
  }
};
```

---

## Configuration Validation

### Checking Your Configuration

Before running analysis, validate settings:

```javascript
// Test data loading
var testCollection = utils.loadDEALandCover(
  config.REGIONAL_DOMAINS.MOREE_PLAINS,
  '2020-01-01',
  '2020-12-31'
);
print('Collection size:', testCollection.size());

// Test projection
print('CRS:', config.PROJECTION.crs);
print('Scale:', config.PROJECTION.scale);

// Test visualization
var testImage = ee.Image(testCollection.first());
Map.addLayer(testImage, config.VIS_PARAMS.BINARY_WOODY, 'Test');
```

### Common Configuration Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `Collection is empty` | Wrong ASSET_ID | Verify asset path in GEE Asset Manager |
| `Band not found` | Wrong BAND name | Print band names: `image.bandNames()` |
| `Computation timeout` | Region too large | Reduce region or increase scale |
| `Memory limit exceeded` | Too fine resolution | Increase scale or split into tiles |

---

## Best Practices

### 1. Version Control
Comment your configuration changes:
```javascript
// Updated 2024-01-15: Reduced cloud cover threshold for temperate regions
MAX_CLOUD_COVER: 15,  // Was: 20
```

### 2. Documentation
Document assumptions:
```javascript
/**
 * WOODY VEGETATION DEFINITION
 * We define woody vegetation as any DEA Land Cover class with >20% canopy cover.
 * This includes forests (111-113), woodlands (121-123), and shrublands (124-126).
 * 
 * Justification: Aligns with Queensland SLATS definition of "woody vegetation"
 * for regulatory consistency.
 */
```

### 3. Modularity
Keep region-specific settings separate:
```javascript
// config.js - Global settings
exports.GLOBAL_SETTINGS = {...};

// moree_config.js - Region-specific overrides
var moreeConfig = Object.assign({}, config.GLOBAL_SETTINGS, {
  scale: 10,  // Higher resolution for regional study
  MAX_CLOUD_COVER: 15
});
```

---

## Configuration Templates

### Template 1: Quick Continental Overview

```javascript
var QUICK_CONFIG = {
  region: config.CONTINENTAL_DOMAIN,
  startYear: '2000',
  endYear: '2020',
  scale: config.SCALES.CONTINENTAL,  // Fast processing
  exportVideo: true,
  exportGeoTIFFs: false  // Skip frames for quick preview
};
```

### Template 2: Detailed Regional Analysis

```javascript
var DETAILED_CONFIG = {
  region: config.REGIONAL_DOMAINS.MOREE_PLAINS,
  startYear: '1988',
  endYear: '2023',
  scale: config.SCALES.LANDSAT,  // Full resolution
  exportVideo: true,
  exportGeoTIFFs: true,
  exportTimeSeries: true
};
```

### Template 3: Recent High-Resolution

```javascript
var RECENT_CONFIG = {
  region: myCustomRegion,
  startYear: '2015',
  endYear: '2023',
  scale: config.SCALES.SENTINEL,  // 10m Sentinel-2
  useSentinel: true,
  exportVideo: true
};
```

---

## Troubleshooting Configuration Issues

### Issue: Exports failing

**Check:**
1. Region size × scale → pixels < 1e13
2. Drive folder exists
3. Filename < 100 characters

**Solution:**
```javascript
// Calculate pixel count
var pixelCount = region.area().divide(scale * scale);
print('Pixel count:', pixelCount);

// If > 1e13, increase scale or split region
```

### Issue: Unexpected results

**Check:**
1. Asset IDs correct
2. Date ranges valid
3. Band names match data

**Debug:**
```javascript
print('Config check:', config.DEA_LAND_COVER);
var test = ee.Image(config.DEA_LAND_COVER.ASSET_ID + '/2000');
print('Bands:', test.bandNames());
Map.addLayer(test);
```

---

## Next Steps

- Review [DATA_SOURCES.md](DATA_SOURCES.md) for data preparation
- See [USAGE_EXAMPLES.md](USAGE_EXAMPLES.md) for workflow examples
- Check main README for complete workflow

---

*Configuration guide maintained as part of the Australian Land Clearing Visualization project.*

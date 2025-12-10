# Usage Examples

This document provides practical examples for using the Australian Land Clearing Visualization workflow.

## Table of Contents

1. [Basic Workflow](#basic-workflow)
2. [Continental Analysis](#continental-analysis)
3. [Regional Case Studies](#regional-case-studies)
4. [Custom Analyses](#custom-analyses)
5. [Export Workflows](#export-workflows)
6. [Advanced Techniques](#advanced-techniques)

---

## Basic Workflow

### Example 1: First Run - Test with Small Region

Start with a small region and short time period to test your setup:

```javascript
// In main_workflow.js
var WORKFLOW_CONFIG = {
  // Small test region
  region: ee.Geometry.Rectangle([149.5, -29.5, 150.0, -29.0]),
  regionName: 'test_region',
  
  // Short time period
  startYear: '2020',
  endYear: '2023',
  
  // Coarse scale for fast processing
  scale: config.SCALES.SMOOTH_ANIMATION,  // 60m
  
  // Limited exports for testing
  exportGeoTIFFs: false,
  exportVideo: true,
  exportTimeSeries: true,
  
  product: 'woody_binary'
};
```

**Expected runtime**: 2-5 minutes  
**Output**: 
- Quick animation preview
- Time series CSV with 4 years of data

---

## Continental Analysis

### Example 2: Full Continental Time Series

Generate a complete time series for eastern Australia:

```javascript
// main_workflow.js
var WORKFLOW_CONFIG = {
  region: config.CONTINENTAL_DOMAIN,
  regionName: 'eastern_australia',
  
  startDate: config.TIME_PERIOD.PRIMARY_START,
  endDate: config.TIME_PERIOD.PRIMARY_END,
  startYear: '1988',
  endYear: '2023',
  
  // Moderate resolution for manageable file sizes
  scale: config.SCALES.SMOOTH_ANIMATION,  // 60m
  
  exportGeoTIFFs: true,   // Annual frames
  exportVideo: true,       // MP4 animation
  exportTimeSeries: true,  // Area statistics
  
  product: 'woody_binary'
};
```

**Processing strategy:**
1. Run with `exportGeoTIFFs: false` first to preview
2. Once satisfied, enable GeoTIFF exports
3. Each annual frame takes ~5-15 minutes to export

**Output size estimates:**
- Video: ~50-100 MB
- Each GeoTIFF frame: ~100-500 MB
- Time series CSV: <1 MB

### Example 3: Multi-Decadal Change Detection

Focus on major change periods:

```javascript
// Detect clearing in specific decades
var periods = [
  {start: 1988, end: 2000, name: 'pre_2000'},
  {start: 2000, end: 2010, name: 'decade_2000s'},
  {start: 2010, end: 2023, name: 'recent'}
];

periods.forEach(function(period) {
  var woodyStart = woodyTimeSeries.filter(
    ee.Filter.eq('year', period.start)
  ).first();
  
  var woodyEnd = woodyTimeSeries.filter(
    ee.Filter.eq('year', period.end)
  ).first();
  
  var clearing = utils.detectClearing(woodyStart, woodyEnd);
  
  // Export clearing for this period
  Export.image.toDrive({
    image: clearing,
    description: 'clearing_' + period.name,
    folder: 'AUS_Land_Clearing/decadal_change',
    fileNamePrefix: 'continental_clearing_' + period.name,
    crs: config.PROJECTION.crs,
    scale: 100,  // Coarser for large exports
    region: config.CONTINENTAL_DOMAIN,
    maxPixels: 1e13
  });
});
```

---

## Regional Case Studies

### Example 4: Moree Plains Analysis

Run the pre-configured Moree Plains case study:

```javascript
// Simply run: gee_scripts/case_studies/moree_plains_nsw.js

// The script is already configured for:
// - Moree Plains region
// - 1988-2023 time period
// - Key years: 1988, 1995, 2000, 2005, 2010, 2015, 2020, 2023
// - Outputs: Frames, animation, time series
```

**Customizing for nearby regions:**

```javascript
// Custom region near Moree
var myRegion = ee.Geometry.Rectangle([148.0, -30.0, 149.0, -29.0]);

var CASE_STUDY = {
  name: 'North_Moree',
  region: myRegion,
  zoomRegion: myRegion,
  // ... rest of configuration
};
```

### Example 5: Brigalow Belt Analysis

Focus on policy-driven change:

```javascript
// Run: gee_scripts/case_studies/brigalow_belt_qld.js

// Highlights:
// - Pre-regulation (1988-2000)
// - Transition (2001-2009)
// - Regulated (2010-2017)
// - Recent (2018-2023)
```

**Adding policy milestones to visualization:**

```javascript
// Annotate specific years
var policyYears = [2000, 2006, 2013, 2018];

policyYears.forEach(function(year) {
  var woody = woodyTimeSeries.filter(ee.Filter.eq('year', year)).first();
  
  Map.addLayer(woody.selfMask(), 
    {palette: ['1a5928']}, 
    'Policy Change: ' + year, 
    false);
});

// Create before/after pairs
var before2006 = woodyTimeSeries.filter(ee.Filter.eq('year', 2005)).first();
var after2006 = woodyTimeSeries.filter(ee.Filter.eq('year', 2007)).first();
var change2006 = utils.detectClearing(before2006, after2006);

Map.addLayer(change2006.selfMask(), 
  config.VIS_PARAMS.CLEARING, 
  'Clearing 2005-2007 (Around 2006 Law Change)');
```

---

## Custom Analyses

### Example 6: Custom Study Region

Define your own region of interest:

```javascript
// Method 1: Draw on map and get coordinates
// In GEE Code Editor: Use drawing tools, then:
var myRegion = /* paste drawn geometry */;

// Method 2: Define from coordinates
var myRegion = ee.Geometry.Polygon([
  [[lon1, lat1], [lon2, lat2], [lon3, lat3], [lon1, lat1]]
]);

// Method 3: Load from uploaded shapefile
var myRegion = ee.FeatureCollection('users/YOUR_USERNAME/my_boundary')
  .geometry();

// Use in workflow
var WORKFLOW_CONFIG = {
  region: myRegion,
  regionName: 'my_custom_region',
  // ... rest of config
};
```

### Example 7: Seasonal Analysis

Detect seasonal clearing patterns:

```javascript
// Focus on specific seasons across multiple years
var years = ee.List.sequence(2015, 2023);

var seasonalClearing = years.map(function(year) {
  // Winter composite (dry season in QLD)
  var winter = utils.createSeasonalComposites(
    landCoverCollection.filterDate(
      ee.Date.fromYMD(year, 1, 1),
      ee.Date.fromYMD(year, 12, 31)
    ),
    year
  ).filter(ee.Filter.eq('season', 'JJA')).first();
  
  // Summer composite
  var summer = utils.createSeasonalComposites(
    landCoverCollection.filterDate(
      ee.Date.fromYMD(year, 1, 1),
      ee.Date.fromYMD(year, 12, 31)
    ),
    year
  ).filter(ee.Filter.eq('season', 'DJF')).first();
  
  var winterWoody = utils.createWoodyMask(winter);
  var summerWoody = utils.createWoodyMask(summer);
  
  // Clearing in winter (peak clearing season)
  var winterClearing = utils.detectClearing(summerWoody, winterWoody);
  
  return winterClearing.set('year', year);
});

// Summarize seasonal clearing
var seasonalClearingSum = ee.ImageCollection(seasonalClearing).sum();
Map.addLayer(seasonalClearingSum.selfMask(), 
  {min: 0, max: 5, palette: ['yellow', 'red']}, 
  'Frequency of Winter Clearing');
```

### Example 8: Fractional Cover Alternative

Use fractional cover instead of land cover:

```javascript
// Load fractional cover
var fcCollection = utils.loadDEAFractionalCover(
  WORKFLOW_CONFIG.region,
  WORKFLOW_CONFIG.startDate,
  WORKFLOW_CONFIG.endDate
);

// Create annual composites
var annualFC = utils.createAnnualComposites(fcCollection, '1988', '2023');

// Convert to woody masks using vegetation fraction
var woodyTimeSeries_FC = annualFC.map(function(image) {
  return utils.woodyFromFractionalCover(image, 30)  // 30% threshold
    .copyProperties(image, ['year']);
});

// Compare with land cover approach
var woodyTimeSeries_LC = annualLandCover.map(function(image) {
  return utils.createWoodyMask(image)
    .copyProperties(image, ['year']);
});

// Visualize difference
var woody2020_FC = woodyTimeSeries_FC.filter(ee.Filter.eq('year', 2020)).first();
var woody2020_LC = woodyTimeSeries_LC.filter(ee.Filter.eq('year', 2020)).first();

var difference = woody2020_FC.subtract(woody2020_LC);

Map.addLayer(difference, 
  {min: -1, max: 1, palette: ['red', 'white', 'blue']}, 
  'FC vs LC Difference (red=LC only, blue=FC only)');
```

---

## Export Workflows

### Example 9: Batch Export Annual Frames

Export all years efficiently:

```javascript
// Define export function
function exportYearlyFrame(year, region, product) {
  var image = woodyTimeSeries.filter(ee.Filter.eq('year', year)).first();
  
  var filename = utils.generateFilename(
    config.EXPORT_CONFIG.NAMING.PREFIX,
    'my_region',
    year.toString(),
    product
  );
  
  Export.image.toDrive({
    image: image,
    description: filename,
    folder: config.EXPORT_CONFIG.DRIVE_FOLDER,
    fileNamePrefix: filename,
    crs: config.PROJECTION.crs,
    scale: 25,
    region: region,
    maxPixels: 1e13,
    fileFormat: 'GeoTIFF',
    formatOptions: {cloudOptimized: true}
  });
}

// Export all years
var years = ee.List.sequence(1988, 2023);
years.getInfo().forEach(function(year) {
  exportYearlyFrame(year, myRegion, 'woody_binary');
});

print('Created', years.length().getInfo(), 'export tasks');
print('Go to Tasks tab to run all exports');
```

### Example 10: Export Change Products

Export multiple change products:

```javascript
// Calculate various change metrics
var baseline = woodyTimeSeries.filter(ee.Filter.eq('year', 1988)).first();
var current = woodyTimeSeries.filter(ee.Filter.eq('year', 2023)).first();

// 1. Binary clearing mask
var clearing = utils.detectClearing(baseline, current);

// 2. Persistence (how long was each pixel woody?)
var persistence = woodyTimeSeries.map(function(img) {
  return img.rename('woody');
}).sum().rename('years_woody');

// 3. Year of clearing (when did clearing occur?)
var clearingYear = utils.cumulativeClearing(woodyTimeSeries);

// Export all products
var products = {
  'clearing_binary': clearing,
  'woody_persistence': persistence,
  'clearing_year': clearingYear
};

Object.keys(products).forEach(function(name) {
  Export.image.toDrive({
    image: products[name],
    description: 'continental_' + name,
    folder: 'AUS_Land_Clearing/change_products',
    fileNamePrefix: 'continental_' + name + '_1988_2023',
    crs: config.PROJECTION.crs,
    scale: 50,
    region: config.CONTINENTAL_DOMAIN,
    maxPixels: 1e13
  });
});
```

### Example 11: Multi-Resolution Exports

Export at multiple resolutions:

```javascript
var resolutions = {
  'high_res': 25,
  'medium_res': 60,
  'low_res': 250
};

var targetYear = 2020;
var image = woodyTimeSeries.filter(ee.Filter.eq('year', targetYear)).first();

Object.keys(resolutions).forEach(function(resName) {
  var scale = resolutions[resName];
  
  Export.image.toDrive({
    image: image,
    description: 'woody_' + targetYear + '_' + resName,
    folder: 'AUS_Land_Clearing/multi_resolution',
    fileNamePrefix: 'continental_woody_' + targetYear + '_' + scale + 'm',
    crs: config.PROJECTION.crs,
    scale: scale,
    region: config.CONTINENTAL_DOMAIN,
    maxPixels: 1e13
  });
});
```

---

## Advanced Techniques

### Example 12: SLATS Validation

Compare detected clearing with SLATS ground truth:

```javascript
// Load SLATS data
var slats = utils.loadSLATS('QLD', 'Landsat', myRegion);

// Convert SLATS polygons to raster
var slatsMask = slats
  .filter(ee.Filter.rangeContains('YEAR', 1988, 2023))
  .reduceToImage(['AREA'], ee.Reducer.sum())
  .gt(0)
  .rename('slats_clearing');

// Your detected clearing
var detectedClearing = utils.detectClearing(woodyBaseline, woodyCurrent);

// Confusion matrix
var confusion = detectedClearing.addBands(slatsMask);

// Calculate agreement
var both = detectedClearing.and(slatsMask);  // True positives
var detectedOnly = detectedClearing.and(slatsMask.not());  // False positives
var slatsOnly = slatsMask.and(detectedClearing.not());  // False negatives

// Visualize
Map.addLayer(both.selfMask(), {palette: 'green'}, 'Agreement (Both)');
Map.addLayer(detectedOnly.selfMask(), {palette: 'yellow'}, 'DEA Only');
Map.addLayer(slatsOnly.selfMask(), {palette: 'red'}, 'SLATS Only');

// Calculate areas
var areas = {
  both: utils.calculateArea(both, myRegion, 25),
  detectedOnly: utils.calculateArea(detectedOnly, myRegion, 25),
  slatsOnly: utils.calculateArea(slatsOnly, myRegion, 25)
};

print('Validation Results:');
print('Agreement (ha):', ee.Number(areas.both.get('slats_clearing')).divide(10000));
print('DEA only (ha):', ee.Number(areas.detectedOnly.get('clearing')).divide(10000));
print('SLATS only (ha):', ee.Number(areas.slatsOnly.get('slats_clearing')).divide(10000));
```

### Example 13: Animated GIF for Web

Create an animated GIF for web display:

```javascript
// Create visualization collection
var frames = woodyTimeSeries.map(function(image) {
  var year = image.get('year');
  
  // Add year label to image
  var labeled = image.visualize(config.VIS_PARAMS.BINARY_WOODY);
  
  // Optional: Add text annotation (requires additional processing)
  return labeled.set('year', year);
});

// Export as GIF (use third-party tools or Python post-processing)
// GEE doesn't directly export GIF, so export frames and combine externally

// Export thumbnail for each year
var years = ee.List.sequence(1988, 2023);
years.getInfo().forEach(function(year) {
  var image = frames.filter(ee.Filter.eq('year', year)).first();
  
  var thumbnail = image.getThumbURL({
    dimensions: 800,
    region: myRegion,
    format: 'png'
  });
  
  print('Year', year, 'thumbnail:', thumbnail);
});

// Python post-processing to create GIF:
// from PIL import Image
// images = [Image.open(f) for f in frame_files]
// images[0].save('animation.gif', save_all=True, append_images=images[1:], duration=500, loop=0)
```

### Example 14: Interactive Time Series Chart

Create rich interactive visualizations:

```javascript
// Calculate area statistics
var areaTimeSeries = utils.woodyAreaTimeSeries(
  woodyTimeSeries,
  myRegion,
  25
);

// Create chart with multiple series
var chart = ui.Chart.feature.byFeature({
  features: areaTimeSeries,
  xProperty: 'year',
  yProperties: ['woody_area_ha']
})
.setChartType('LineChart')
.setOptions({
  title: 'Woody Vegetation Cover - ' + regionName,
  vAxis: {
    title: 'Area (hectares)',
    viewWindow: {min: 0}
  },
  hAxis: {
    title: 'Year',
    format: '####'
  },
  lineWidth: 3,
  pointSize: 5,
  series: {
    0: {color: '1a5928', labelInLegend: 'Woody Vegetation'}
  },
  legend: {position: 'bottom'},
  
  // Add trend line
  trendlines: {
    0: {
      type: 'linear',
      color: 'red',
      lineWidth: 2,
      opacity: 0.5,
      showR2: true,
      visibleInLegend: true
    }
  }
});

print(chart);

// Export chart data
Export.table.toDrive({
  collection: areaTimeSeries,
  description: 'area_timeseries_' + regionName,
  folder: 'AUS_Land_Clearing',
  fileFormat: 'CSV'
});
```

---

## Troubleshooting Common Issues

### Issue: Export Task Fails

**Symptom**: Export task shows "Failed" in Tasks tab

**Solutions:**

```javascript
// 1. Check pixel count
var pixelCount = myRegion.area().divide(scale * scale);
print('Pixel count:', pixelCount);
// If > 1e13, reduce region or increase scale

// 2. Split large regions
var grid = myRegion.coveringGrid(config.PROJECTION.crs, scale * 1000);
grid.geometry().getInfo().coordinates[0].forEach(function(cell, index) {
  var cellGeom = ee.Geometry.Polygon(cell);
  // Export each cell separately
  Export.image.toDrive({
    image: myImage,
    description: 'tile_' + index,
    region: cellGeom,
    scale: scale,
    maxPixels: 1e13
  });
});
```

### Issue: Memory Limit Exceeded

**Solution:**

```javascript
// Use .aside() to force computation
var woody = woodyTimeSeries.aside(function(collection) {
  print('Processing', collection.size(), 'images');
});

// Or export intermediate products
var baseline = woodyTimeSeries.first();
Export.image.toAsset({
  image: baseline,
  description: 'baseline_woody',
  assetId: 'projects/YOUR_PROJECT/baseline_woody',
  region: myRegion,
  scale: 25,
  maxPixels: 1e13
});
```

---

## Next Steps

- Review full [README](../README.md) for project overview
- Check [CONFIGURATION.md](CONFIGURATION.md) for all options
- See [DATA_SOURCES.md](DATA_SOURCES.md) for data details

---

*Usage examples maintained as part of the Australian Land Clearing Visualization project.*

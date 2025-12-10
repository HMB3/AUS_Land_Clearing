/**
 * Moree Plains Case Study - NSW Land Clearing Analysis
 * 
 * This script focuses on the Moree Plains region in northwestern NSW,
 * a major agricultural area with significant land clearing history.
 * The region has seen extensive conversion of native woody vegetation
 * to cropland (primarily cotton and wheat).
 * 
 * NARRATIVE FOCUS:
 * - Agricultural expansion from 1988 onwards
 * - Clearing for irrigation agriculture (cotton boom)
 * - Comparison with NSW SLATS clearing records
 * 
 * USAGE:
 * Run this script in Google Earth Engine Code Editor to generate
 * visualizations specific to the Moree Plains region.
 */

// Load core modules
var config = require('../core/config.js');
var utils = require('../core/utils.js');

// ============================================================================
// CASE STUDY CONFIGURATION
// ============================================================================

var CASE_STUDY = {
  name: 'Moree Plains',
  state: 'NSW',
  
  // Regional boundary
  region: config.REGIONAL_DOMAINS.MOREE_PLAINS,
  
  // Refined boundary for zoomed visualization
  // Moree town center: ~-29.46, 149.84
  zoomRegion: ee.Geometry.Rectangle([149.5, -29.8, 150.2, -29.2]),
  
  // Time period - focus on key clearing periods
  periods: {
    baseline: {start: '1988-01-01', end: '1992-12-31', label: '1988-1992 (Baseline)'},
    expansion: {start: '1993-01-01', end: '2003-12-31', label: '1993-2003 (Expansion)'},
    recent: {start: '2015-01-01', end: '2023-12-31', label: '2015-2023 (Recent)'}
  },
  
  // Key clearing events to highlight (from SLATS/historical records)
  events: [
    {year: 1995, description: 'Cotton boom - major irrigation expansion'},
    {year: 2000, description: 'Peak clearing period'},
    {year: 2005, description: 'Introduction of native vegetation regulations'}
  ],
  
  // Export settings
  scale: config.SCALES.LANDSAT,  // 25m for detailed regional analysis
  exportFolder: 'moree_plains'
};

print('=== MOREE PLAINS CASE STUDY ===');
print('Region:', CASE_STUDY.name);
print('State:', CASE_STUDY.state);

// ============================================================================
// LOAD AND PROCESS DATA
// ============================================================================

print('Loading data for', CASE_STUDY.name);

// Load land cover for entire study period
var landCover = utils.loadDEALandCover(
  CASE_STUDY.region,
  CASE_STUDY.periods.baseline.start,
  CASE_STUDY.periods.recent.end
);

// Create annual woody vegetation masks
var annualLandCover = utils.createAnnualComposites(landCover, '1988', '2023');
var woodyTimeSeries = annualLandCover.map(function(image) {
  return utils.createWoodyMask(image).copyProperties(image, ['year']);
});

// Load NSW SLATS data for validation
// var nswSlats = utils.loadSLATS('NSW', 'Landsat', CASE_STUDY.region);

// ============================================================================
// PERIOD ANALYSIS
// ============================================================================

print('Analyzing clearing across periods');

/**
 * Calculate woody vegetation for each period
 */
var periodComparisons = Object.keys(CASE_STUDY.periods).map(function(periodKey) {
  var period = CASE_STUDY.periods[periodKey];
  
  // Get images from this period
  var periodLC = utils.loadDEALandCover(
    CASE_STUDY.region,
    period.start,
    period.end
  );
  
  // Create composite for the period
  var composite = periodLC.median();
  var woodyMask = utils.createWoodyMask(composite);
  
  // Calculate area
  var area = utils.calculateArea(woodyMask, CASE_STUDY.region, CASE_STUDY.scale);
  
  return {
    period: periodKey,
    label: period.label,
    woody_area_ha: area,
    image: woodyMask
  };
});

// ============================================================================
// CHANGE DETECTION
// ============================================================================

print('Detecting clearing events');

// Clearing between baseline and expansion period
// var baselineWoody = periodComparisons[0].image;
// var expansionWoody = periodComparisons[1].image;
// var recentWoody = periodComparisons[2].image;

// var clearing1 = utils.detectClearing(baselineWoody, expansionWoody);
// var clearing2 = utils.detectClearing(expansionWoody, recentWoody);
// var totalClearing = utils.detectClearing(baselineWoody, recentWoody);

// ============================================================================
// VISUALIZATION
// ============================================================================

print('Creating visualizations');

// Center map on Moree Plains
Map.centerObject(CASE_STUDY.zoomRegion, 10);

// Add region boundaries
Map.addLayer(CASE_STUDY.region, {color: 'red'}, 'Moree Plains Region', true, 0.3);
Map.addLayer(CASE_STUDY.zoomRegion, {color: 'blue'}, 'Zoom Area', true, 0.3);

// Add period comparisons
// Map.addLayer(baselineWoody.selfMask(), 
//   {palette: ['1a5928']}, 
//   CASE_STUDY.periods.baseline.label, false);
// Map.addLayer(recentWoody.selfMask(), 
//   {palette: ['78d203']}, 
//   CASE_STUDY.periods.recent.label, false);

// Add clearing visualization
// Map.addLayer(totalClearing.selfMask(), 
//   config.VIS_PARAMS.CLEARING, 
//   'Total Clearing (1988-2023)', false);

// Add NSW SLATS overlay
// Map.addLayer(nswSlats, {color: 'orange'}, 'NSW SLATS Clearing', false);

// ============================================================================
// TIME SERIES ANALYSIS
// ============================================================================

print('Generating time series');

// Calculate annual woody area
var areaTimeSeries = utils.woodyAreaTimeSeries(
  woodyTimeSeries,
  CASE_STUDY.region,
  CASE_STUDY.scale
);

print('Area Time Series:', areaTimeSeries.limit(5));

// Create chart
var chart = ui.Chart.feature.byFeature(areaTimeSeries, 'year', 'woody_area_ha')
  .setChartType('LineChart')
  .setOptions({
    title: 'Woody Vegetation Area - ' + CASE_STUDY.name,
    vAxis: {title: 'Area (hectares)'},
    hAxis: {title: 'Year'},
    lineWidth: 2,
    pointSize: 3,
    series: {0: {color: '1a5928'}}
  });

print(chart);

// ============================================================================
// EXPORT CONFIGURATION
// ============================================================================

print('Setting up exports');

/**
 * Export annual frames for animation
 */
var exportYears = [1988, 1995, 2000, 2005, 2010, 2015, 2020, 2023];

exportYears.forEach(function(year) {
  var image = woodyTimeSeries.filter(ee.Filter.eq('year', year)).first();
  
  var filename = [
    'moree_plains',
    'woody',
    year.toString()
  ].join('_');
  
  // Export for zoom region (higher detail)
  Export.image.toDrive({
    image: image,
    description: filename + '_zoom',
    folder: config.EXPORT_CONFIG.DRIVE_FOLDER + '/' + CASE_STUDY.exportFolder,
    fileNamePrefix: filename + '_zoom',
    crs: config.PROJECTION.crs,
    scale: CASE_STUDY.scale,
    region: CASE_STUDY.zoomRegion,
    maxPixels: 1e13,
    fileFormat: 'GeoTIFF',
    formatOptions: config.EXPORT_CONFIG.GEOTIFF.formatOptions
  });
});

/**
 * Export change detection products
 */
// Export.image.toDrive({
//   image: totalClearing,
//   description: 'moree_plains_clearing_1988_2023',
//   folder: config.EXPORT_CONFIG.DRIVE_FOLDER + '/' + CASE_STUDY.exportFolder,
//   fileNamePrefix: 'moree_plains_clearing_1988_2023',
//   crs: config.PROJECTION.crs,
//   scale: CASE_STUDY.scale,
//   region: CASE_STUDY.region,
//   maxPixels: 1e13,
//   fileFormat: 'GeoTIFF',
//   formatOptions: config.EXPORT_CONFIG.GEOTIFF.formatOptions
// });

/**
 * Export time series data
 */
Export.table.toDrive({
  collection: areaTimeSeries,
  description: 'moree_plains_timeseries',
  folder: config.EXPORT_CONFIG.DRIVE_FOLDER + '/' + CASE_STUDY.exportFolder,
  fileNamePrefix: 'moree_plains_woody_area_timeseries',
  fileFormat: 'CSV'
});

/**
 * Export video animation
 */
var visualizationCollection = woodyTimeSeries.map(function(image) {
  return image.visualize(config.VIS_PARAMS.BINARY_WOODY)
    .copyProperties(image, ['year', 'system:time_start']);
});

Export.video.toDrive({
  collection: visualizationCollection,
  description: 'moree_plains_animation',
  folder: config.EXPORT_CONFIG.DRIVE_FOLDER + '/' + CASE_STUDY.exportFolder,
  fileNamePrefix: 'moree_plains_woody_1988_2023',
  framesPerSecond: 2,
  dimensions: 1920,
  region: CASE_STUDY.zoomRegion,
  maxPixels: 1e13,
  crs: config.PROJECTION.crs
});

// ============================================================================
// NARRATIVE OUTPUTS
// ============================================================================

print('=== CASE STUDY SUMMARY ===');
print('Location: Moree Plains, northwestern NSW');
print('Known for: Cotton and wheat production, irrigation agriculture');
print('Clearing History:');
CASE_STUDY.events.forEach(function(event) {
  print(' -', event.year + ':', event.description);
});
print('');
print('Analysis Period: 1988-2023');
print('Key Findings: Check time series chart and clearing maps above');
print('');
print('Go to Tasks tab to run exports');

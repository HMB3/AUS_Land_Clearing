/**
 * Queensland Case Study - Brigalow Belt Clearing Analysis
 * 
 * This script focuses on the Brigalow Belt bioregion in Queensland,
 * one of the most extensively cleared regions in Australia. The Brigalow
 * Belt has been a focal point for SLATS monitoring and clearing debates.
 * 
 * NARRATIVE FOCUS:
 * - Historical clearing of brigalow scrub for agriculture (1988-2006)
 * - Impact of vegetation management laws (2006+)
 * - Recent clearing trends under changing regulations
 * - Validation with SLATS woody vegetation clearing data
 * 
 * USAGE:
 * Run this script in Google Earth Engine Code Editor to generate
 * visualizations specific to the Brigalow Belt region.
 */

// Load core modules
var config = require('../core/config.js');
var utils = require('../core/utils.js');

// ============================================================================
// CASE STUDY CONFIGURATION
// ============================================================================

var CASE_STUDY = {
  name: 'Brigalow Belt',
  state: 'QLD',
  
  // Regional boundary
  region: config.REGIONAL_DOMAINS.BRIGALOW_BELT,
  
  // Specific focus areas within the Brigalow Belt
  focusAreas: {
    central: ee.Geometry.Rectangle([149.0, -25.5, 150.5, -24.5]),
    northern: ee.Geometry.Rectangle([148.5, -24.5, 150.0, -23.5])
  },
  
  // Time period - aligned with key policy changes
  periods: {
    preRegulation: {
      start: '1988-01-01', 
      end: '2000-12-31', 
      label: '1988-2000 (Pre-regulation)',
      description: 'Peak clearing period before strict controls'
    },
    transitionPeriod: {
      start: '2001-01-01', 
      end: '2009-12-31', 
      label: '2001-2009 (Transition)',
      description: 'Introduction and strengthening of vegetation laws'
    },
    regulated: {
      start: '2010-01-01', 
      end: '2017-12-31', 
      label: '2010-2017 (Regulated)',
      description: 'Strong vegetation protection laws'
    },
    recent: {
      start: '2018-01-01', 
      end: '2023-12-31', 
      label: '2018-2023 (Recent)',
      description: 'Post-regulation changes and exemptions'
    }
  },
  
  // Key policy milestones
  milestones: [
    {year: 1988, description: 'SLATS monitoring begins'},
    {year: 2000, description: 'Peak clearing - over 500,000 ha/year cleared in QLD'},
    {year: 2004, description: 'Vegetation Management Act strengthened'},
    {year: 2006, description: 'Tree clearing restrictions tightened'},
    {year: 2013, description: 'Clearing restrictions weakened'},
    {year: 2018, description: 'Vegetation laws reinstated'}
  ],
  
  // Export settings
  scale: config.SCALES.LANDSAT,
  exportFolder: 'brigalow_belt_qld'
};

print('=== BRIGALOW BELT CASE STUDY ===');
print('Region:', CASE_STUDY.name);
print('State:', CASE_STUDY.state);
print('Bioregion: One of Australia\'s most cleared ecosystems');

// ============================================================================
// LOAD AND PROCESS DATA
// ============================================================================

print('Loading data for', CASE_STUDY.name);

// Load land cover for entire study period
var landCover = utils.loadDEALandCover(
  CASE_STUDY.region,
  CASE_STUDY.periods.preRegulation.start,
  CASE_STUDY.periods.recent.end
);

// Create annual woody vegetation masks
var annualLandCover = utils.createAnnualComposites(landCover, '1988', '2023');
var woodyTimeSeries = annualLandCover.map(function(image) {
  return utils.createWoodyMask(image).copyProperties(image, ['year']);
});

// Load SLATS data - critical for this region
// var slatsQLD = utils.loadSLATS('QLD', 'Landsat', CASE_STUDY.region);
// print('SLATS QLD Clearing Events:', slatsQLD.size());

// Load Sentinel-2 SLATS for recent years (2015+)
// var slatsQLD_S2 = utils.loadSLATS('QLD', 'Sentinel', CASE_STUDY.region);

// ============================================================================
// PERIOD ANALYSIS
// ============================================================================

print('Analyzing clearing across policy periods');

/**
 * Calculate woody vegetation statistics for each policy period
 */
var periodStats = {};

Object.keys(CASE_STUDY.periods).forEach(function(periodKey) {
  var period = CASE_STUDY.periods[periodKey];
  
  print('Processing period:', period.label);
  
  // Get years for this period
  var startYear = parseInt(period.start.split('-')[0]);
  var endYear = parseInt(period.end.split('-')[0]);
  
  // Get woody masks for start and end of period
  var woodyStart = woodyTimeSeries.filter(ee.Filter.eq('year', startYear)).first();
  var woodyEnd = woodyTimeSeries.filter(ee.Filter.eq('year', endYear)).first();
  
  // Detect clearing in this period
  var clearing = utils.detectClearing(woodyStart, woodyEnd);
  
  // Calculate areas
  var clearingArea = utils.calculateArea(clearing, CASE_STUDY.region, CASE_STUDY.scale);
  
  periodStats[periodKey] = {
    label: period.label,
    startYear: startYear,
    endYear: endYear,
    woodyStart: woodyStart,
    woodyEnd: woodyEnd,
    clearing: clearing,
    clearingArea: clearingArea
  };
  
  // Print period summary
  // print(period.label, '- Clearing (ha):', 
  //   ee.Number(clearingArea.get('clearing')).divide(10000));
});

// ============================================================================
// CHANGE DETECTION - FULL TIME SERIES
// ============================================================================

print('Detecting cumulative clearing');

// Calculate total clearing from baseline (1988) to present (2023)
var woodyBaseline = woodyTimeSeries.filter(ee.Filter.eq('year', 1988)).first();
var woodyCurrent = woodyTimeSeries.filter(ee.Filter.eq('year', 2023)).first();
var totalClearing = utils.detectClearing(woodyBaseline, woodyCurrent);

var totalClearingArea = utils.calculateArea(
  totalClearing, 
  CASE_STUDY.region, 
  CASE_STUDY.scale
);

print('Total clearing 1988-2023 (ha):', 
  ee.Number(totalClearingArea.get('clearing')).divide(10000));

// ============================================================================
// VISUALIZATION
// ============================================================================

print('Creating visualizations');

// Center map on Brigalow Belt
Map.centerObject(CASE_STUDY.region, 7);

// Add region boundaries
Map.addLayer(CASE_STUDY.region, 
  {color: 'red'}, 'Brigalow Belt Region', true, 0.3);
Map.addLayer(CASE_STUDY.focusAreas.central, 
  {color: 'blue'}, 'Central Focus Area', false, 0.3);

// Add baseline and current woody vegetation
Map.addLayer(woodyBaseline.selfMask(), 
  {palette: ['1a5928']}, '1988 Woody Vegetation', false);
Map.addLayer(woodyCurrent.selfMask(), 
  {palette: ['78d203']}, '2023 Woody Vegetation', true);

// Add cumulative clearing
Map.addLayer(totalClearing.selfMask(), 
  config.VIS_PARAMS.CLEARING, 
  'Total Clearing (1988-2023)', true);

// Add SLATS clearing events
// Map.addLayer(slatsQLD, {color: 'orange'}, 'SLATS Clearing Events', false);

// Visualize clearing by period
// Object.keys(periodStats).forEach(function(key, index) {
//   var stat = periodStats[key];
//   Map.addLayer(stat.clearing.selfMask(), 
//     {palette: ['ff' + (index * 40).toString(16) + '00']}, 
//     'Clearing: ' + stat.label, false);
// });

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

print('Sample time series data:', areaTimeSeries.limit(5));

// Create interactive chart
var chart = ui.Chart.feature.byFeature(areaTimeSeries, 'year', 'woody_area_ha')
  .setChartType('LineChart')
  .setOptions({
    title: 'Woody Vegetation Area - Brigalow Belt',
    vAxis: {title: 'Area (hectares)'},
    hAxis: {title: 'Year'},
    lineWidth: 2,
    pointSize: 3,
    series: {0: {color: '1a5928'}},
    // Add annotations for key policy milestones
    annotations: {
      style: 'line',
      alwaysOutside: true
    }
  });

print(chart);

// ============================================================================
// SLATS VALIDATION
// ============================================================================

print('SLATS Validation');
print('This region has extensive SLATS ground-truth data.');
print('Comparison between DEA-derived clearing and SLATS records');
print('can validate the remote sensing approach.');

// Calculate overlap between detected clearing and SLATS polygons
// var slatsMask = slatsQLD.reduceToImage(['AREA'], ee.Reducer.sum()).gt(0);
// var overlap = totalClearing.multiply(slatsMask);
// var validationStats = utils.calculateArea(overlap, CASE_STUDY.region, CASE_STUDY.scale);

// print('Clearing validated by SLATS (ha):', 
//   ee.Number(validationStats.get('clearing')).divide(10000));

// ============================================================================
// EXPORT CONFIGURATION
// ============================================================================

print('Setting up exports');

/**
 * Export key years showing policy impacts
 */
var keyYears = [1988, 2000, 2006, 2013, 2018, 2023];

keyYears.forEach(function(year) {
  var image = woodyTimeSeries.filter(ee.Filter.eq('year', year)).first();
  
  var filename = [
    'brigalow_belt',
    'woody',
    year.toString()
  ].join('_');
  
  Export.image.toDrive({
    image: image,
    description: filename,
    folder: config.EXPORT_CONFIG.DRIVE_FOLDER + '/' + CASE_STUDY.exportFolder,
    fileNamePrefix: filename,
    crs: config.PROJECTION.crs,
    scale: CASE_STUDY.scale,
    region: CASE_STUDY.region,
    maxPixels: 1e13,
    fileFormat: 'GeoTIFF',
    formatOptions: config.EXPORT_CONFIG.GEOTIFF.formatOptions
  });
});

/**
 * Export clearing by period
 */
Object.keys(periodStats).forEach(function(key) {
  var stat = periodStats[key];
  var filename = [
    'brigalow_belt',
    'clearing',
    stat.startYear.toString(),
    stat.endYear.toString()
  ].join('_');
  
  // Export.image.toDrive({
  //   image: stat.clearing,
  //   description: filename,
  //   folder: config.EXPORT_CONFIG.DRIVE_FOLDER + '/' + CASE_STUDY.exportFolder,
  //   fileNamePrefix: filename,
  //   crs: config.PROJECTION.crs,
  //   scale: CASE_STUDY.scale,
  //   region: CASE_STUDY.region,
  //   maxPixels: 1e13,
  //   fileFormat: 'GeoTIFF',
  //   formatOptions: config.EXPORT_CONFIG.GEOTIFF.formatOptions
  // });
});

/**
 * Export total cumulative clearing
 */
Export.image.toDrive({
  image: totalClearing,
  description: 'brigalow_belt_total_clearing',
  folder: config.EXPORT_CONFIG.DRIVE_FOLDER + '/' + CASE_STUDY.exportFolder,
  fileNamePrefix: 'brigalow_belt_clearing_1988_2023',
  crs: config.PROJECTION.crs,
  scale: CASE_STUDY.scale,
  region: CASE_STUDY.region,
  maxPixels: 1e13,
  fileFormat: 'GeoTIFF',
  formatOptions: config.EXPORT_CONFIG.GEOTIFF.formatOptions
});

/**
 * Export time series
 */
Export.table.toDrive({
  collection: areaTimeSeries,
  description: 'brigalow_belt_timeseries',
  folder: config.EXPORT_CONFIG.DRIVE_FOLDER + '/' + CASE_STUDY.exportFolder,
  fileNamePrefix: 'brigalow_belt_woody_area_timeseries',
  fileFormat: 'CSV'
});

/**
 * Export video animation - full time series
 */
var visualizationCollection = woodyTimeSeries.map(function(image) {
  return image.visualize(config.VIS_PARAMS.BINARY_WOODY)
    .copyProperties(image, ['year', 'system:time_start']);
});

Export.video.toDrive({
  collection: visualizationCollection,
  description: 'brigalow_belt_animation',
  folder: config.EXPORT_CONFIG.DRIVE_FOLDER + '/' + CASE_STUDY.exportFolder,
  fileNamePrefix: 'brigalow_belt_woody_1988_2023',
  framesPerSecond: 2,
  dimensions: 1920,
  region: CASE_STUDY.focusAreas.central,
  maxPixels: 1e13,
  crs: config.PROJECTION.crs
});

// ============================================================================
// NARRATIVE OUTPUTS
// ============================================================================

print('=== CASE STUDY SUMMARY ===');
print('Location: Brigalow Belt bioregion, Queensland');
print('Significance: One of Australia\'s most extensively cleared ecosystems');
print('Vegetation Type: Brigalow (Acacia harpophylla) scrub and woodland');
print('');
print('Policy Timeline:');
CASE_STUDY.milestones.forEach(function(milestone) {
  print(' -', milestone.year + ':', milestone.description);
});
print('');
print('Analysis Periods:');
Object.keys(CASE_STUDY.periods).forEach(function(key) {
  var period = CASE_STUDY.periods[key];
  print(' -', period.label);
  print('   ', period.description);
});
print('');
print('Data Sources:');
print(' - DEA Land Cover (Landsat) for woody vegetation mapping');
print(' - SLATS woody clearing data for validation');
print(' - Policy records from Queensland government');
print('');
print('Go to Tasks tab to run exports');

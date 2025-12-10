/**
 * Continental-Scale Visualization Script
 * 
 * This script provides a streamlined workflow for generating continental-scale
 * visualizations of land clearing across eastern Australia.
 * 
 * Optimized for:
 * - Large spatial extent (eastern seaboard)
 * - Long time series (1988-present)
 * - Smooth animations for storytelling
 * - Efficient processing with coarser resolution
 * 
 * USAGE:
 * 1. Update asset paths in core/config.js
 * 2. Run this script in GEE Code Editor
 * 3. Check Tasks tab for exports
 */

// Load core modules
var config = require('./core/config.js');
var utils = require('./core/utils.js');

// ============================================================================
// CONTINENTAL CONFIGURATION
// ============================================================================

var CONTINENTAL_CONFIG = {
  name: 'Eastern Australia Continental Overview',
  
  // Use pre-defined continental domain
  region: config.CONTINENTAL_DOMAIN,
  
  // Time period - full Landsat era
  startYear: 1988,
  endYear: 2023,
  
  // Moderate resolution for manageable processing
  // 60m provides smooth animations while maintaining detail
  scale: config.SCALES.SMOOTH_ANIMATION,
  
  // Export options
  exports: {
    video: true,           // Create MP4 animation
    keyFrames: true,       // Export key years as GeoTIFF
    timeSeries: true,      // Export area statistics
    changeMap: true        // Export cumulative change map
  },
  
  // Key years to export as individual frames
  keyYears: [1988, 1995, 2000, 2005, 2010, 2015, 2020, 2023],
  
  // Visualization settings
  product: 'woody_binary',  // Binary woody/non-woody
  colorScheme: 'natural'     // 'natural' or 'emphasis'
};

print('=== CONTINENTAL SCALE ANALYSIS ===');
print('Region: Eastern Australia');
print('Period:', CONTINENTAL_CONFIG.startYear, '-', CONTINENTAL_CONFIG.endYear);
print('Resolution:', CONTINENTAL_CONFIG.scale, 'meters');
print('');

// ============================================================================
// LOAD AND PROCESS DATA
// ============================================================================

print('Step 1: Loading data...');

// Load DEA Land Cover
var landCoverCollection = utils.loadDEALandCover(
  CONTINENTAL_CONFIG.region,
  CONTINENTAL_CONFIG.startYear + '-01-01',
  CONTINENTAL_CONFIG.endYear + '-12-31'
);

print('Land cover collection:', landCoverCollection);

// Create annual composites
print('Step 2: Creating annual composites...');

var annualLandCover = utils.createAnnualComposites(
  landCoverCollection,
  CONTINENTAL_CONFIG.startYear.toString(),
  CONTINENTAL_CONFIG.endYear.toString()
);

// Generate woody vegetation masks
print('Step 3: Generating woody vegetation masks...');

var woodyTimeSeries = annualLandCover.map(function(image) {
  var woody = utils.createWoodyMask(image);
  return woody.copyProperties(image, ['year', 'system:time_start']);
});

print('Woody time series:', woodyTimeSeries);

// ============================================================================
// VISUALIZATION
// ============================================================================

print('Step 4: Creating visualizations...');

// Select color scheme
var visParams;
if (CONTINENTAL_CONFIG.colorScheme === 'natural') {
  visParams = config.VIS_PARAMS.BINARY_WOODY;
} else {
  // Emphasis scheme - higher contrast
  visParams = {
    min: 0,
    max: 1,
    palette: ['ffffff', '006400']  // White to dark green
  };
}

// Create visualization collection
var visualizationCollection = woodyTimeSeries.map(function(image) {
  return image.visualize(visParams)
    .copyProperties(image, ['year', 'system:time_start']);
});

// Display on map
Map.centerObject(CONTINENTAL_CONFIG.region, 5);

var firstYear = ee.Image(woodyTimeSeries.filter(
  ee.Filter.eq('year', CONTINENTAL_CONFIG.startYear)
).first());

var lastYear = ee.Image(woodyTimeSeries.filter(
  ee.Filter.eq('year', CONTINENTAL_CONFIG.endYear)
).first());

Map.addLayer(firstYear.selfMask(), {palette: '1a5928'}, 
  CONTINENTAL_CONFIG.startYear + ' Woody Vegetation', false);
Map.addLayer(lastYear.selfMask(), {palette: '78d203'}, 
  CONTINENTAL_CONFIG.endYear + ' Woody Vegetation', true);
Map.addLayer(CONTINENTAL_CONFIG.region, {color: 'red'}, 
  'Analysis Region', true, 0.3);

// ============================================================================
// CHANGE ANALYSIS
// ============================================================================

print('Step 5: Calculating change metrics...');

// Total clearing over study period
var totalClearing = utils.detectClearing(firstYear, lastYear);

Map.addLayer(totalClearing.selfMask(), config.VIS_PARAMS.CLEARING,
  'Total Clearing (' + CONTINENTAL_CONFIG.startYear + '-' + CONTINENTAL_CONFIG.endYear + ')', 
  true);

// Calculate clearing area
var clearingArea = utils.calculateArea(
  totalClearing,
  CONTINENTAL_CONFIG.region,
  CONTINENTAL_CONFIG.scale
);

print('Total Clearing:');
print('  Area (hectares):', 
  ee.Number(clearingArea.get('clearing')).divide(10000));

// Time series statistics
var areaTimeSeries = utils.woodyAreaTimeSeries(
  woodyTimeSeries,
  CONTINENTAL_CONFIG.region,
  CONTINENTAL_CONFIG.scale
);

print('Area time series (first 5 years):', areaTimeSeries.limit(5));

// Create chart
var chart = ui.Chart.feature.byFeature(areaTimeSeries, 'year', 'woody_area_ha')
  .setChartType('LineChart')
  .setOptions({
    title: 'Woody Vegetation Cover - Eastern Australia',
    vAxis: {
      title: 'Area (hectares)',
      viewWindow: {min: 0}
    },
    hAxis: {
      title: 'Year',
      format: '####'
    },
    lineWidth: 3,
    pointSize: 4,
    series: {0: {color: '1a5928'}},
    legend: {position: 'none'},
    chartArea: {width: '80%', height: '70%'}
  });

print(chart);

// ============================================================================
// EXPORTS
// ============================================================================

print('Step 6: Setting up exports...');
print('Go to the Tasks tab to run exports');

var exportFolder = config.EXPORT_CONFIG.DRIVE_FOLDER + '/continental';

// 1. Export video animation
if (CONTINENTAL_CONFIG.exports.video) {
  Export.video.toDrive({
    collection: visualizationCollection,
    description: 'continental_woody_animation',
    folder: exportFolder,
    fileNamePrefix: 'eastern_australia_woody_' + 
                    CONTINENTAL_CONFIG.startYear + '_' + 
                    CONTINENTAL_CONFIG.endYear,
    framesPerSecond: config.EXPORT_CONFIG.VIDEO.framesPerSecond,
    dimensions: config.EXPORT_CONFIG.VIDEO.dimensions,
    region: CONTINENTAL_CONFIG.region,
    maxPixels: 1e13,
    crs: config.PROJECTION.crs
  });
  
  print('✓ Video export task created');
}

// 2. Export key frames as GeoTIFF
if (CONTINENTAL_CONFIG.exports.keyFrames) {
  CONTINENTAL_CONFIG.keyYears.forEach(function(year) {
    var image = woodyTimeSeries.filter(ee.Filter.eq('year', year)).first();
    
    Export.image.toDrive({
      image: image,
      description: 'continental_woody_' + year,
      folder: exportFolder + '/frames',
      fileNamePrefix: 'eastern_australia_woody_' + year,
      crs: config.PROJECTION.crs,
      scale: CONTINENTAL_CONFIG.scale,
      region: CONTINENTAL_CONFIG.region,
      maxPixels: 1e13,
      fileFormat: 'GeoTIFF',
      formatOptions: config.EXPORT_CONFIG.GEOTIFF.formatOptions
    });
  });
  
  print('✓ Key frame export tasks created (' + 
        CONTINENTAL_CONFIG.keyYears.length + ' years)');
}

// 3. Export time series data
if (CONTINENTAL_CONFIG.exports.timeSeries) {
  Export.table.toDrive({
    collection: areaTimeSeries,
    description: 'continental_timeseries',
    folder: exportFolder,
    fileNamePrefix: 'eastern_australia_woody_area_' + 
                    CONTINENTAL_CONFIG.startYear + '_' + 
                    CONTINENTAL_CONFIG.endYear,
    fileFormat: 'CSV'
  });
  
  print('✓ Time series export task created');
}

// 4. Export change map
if (CONTINENTAL_CONFIG.exports.changeMap) {
  Export.image.toDrive({
    image: totalClearing,
    description: 'continental_clearing_map',
    folder: exportFolder,
    fileNamePrefix: 'eastern_australia_clearing_' + 
                    CONTINENTAL_CONFIG.startYear + '_' + 
                    CONTINENTAL_CONFIG.endYear,
    crs: config.PROJECTION.crs,
    scale: CONTINENTAL_CONFIG.scale,
    region: CONTINENTAL_CONFIG.region,
    maxPixels: 1e13,
    fileFormat: 'GeoTIFF',
    formatOptions: config.EXPORT_CONFIG.GEOTIFF.formatOptions
  });
  
  print('✓ Change map export task created');
}

// ============================================================================
// SUMMARY
// ============================================================================

print('');
print('=== CONTINENTAL ANALYSIS COMPLETE ===');
print('');
print('Configuration:');
print('  Region: Eastern Australia');
print('  Years:', CONTINENTAL_CONFIG.startYear, '-', CONTINENTAL_CONFIG.endYear);
print('  Resolution:', CONTINENTAL_CONFIG.scale, 'meters');
print('  Product:', CONTINENTAL_CONFIG.product);
print('');
print('Exports configured:');
if (CONTINENTAL_CONFIG.exports.video) print('  ✓ MP4 animation');
if (CONTINENTAL_CONFIG.exports.keyFrames) 
  print('  ✓ Key frames (' + CONTINENTAL_CONFIG.keyYears.length + ' years)');
if (CONTINENTAL_CONFIG.exports.timeSeries) print('  ✓ Area time series (CSV)');
if (CONTINENTAL_CONFIG.exports.changeMap) print('  ✓ Cumulative change map');
print('');
print('Next steps:');
print('1. Review visualizations on the map above');
print('2. Check the time series chart');
print('3. Go to Tasks tab to run exports');
print('4. Outputs will be saved to Google Drive:', exportFolder);
print('');
print('Estimated export time:');
print('  Video: 15-30 minutes');
print('  Each key frame: 5-10 minutes');
print('  Time series: <1 minute');
print('  Change map: 5-10 minutes');

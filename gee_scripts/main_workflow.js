/**
 * Main Workflow Script for Land Clearing Visualization
 * 
 * This script orchestrates the complete workflow for generating land clearing
 * visualizations across Eastern Australia. It demonstrates how to use the
 * modular functions from config.js and utils.js to create reproducible outputs.
 * 
 * USAGE:
 * 1. Update the asset paths in config.js with your actual DEA/SLATS data
 * 2. Modify the WORKFLOW_CONFIG section below to select regions and time periods
 * 3. Run the script in Google Earth Engine Code Editor
 * 4. Check the Tasks tab to monitor exports
 * 
 * OUTPUTS:
 * - Annual GeoTIFF frames for each year
 * - MP4 animation showing land cover change over time
 * - Time series data (area statistics)
 */

// Load configuration and utility modules
var config = require('./core/config.js');
var utils = require('./core/utils.js');

// ============================================================================
// WORKFLOW CONFIGURATION
// ============================================================================

/**
 * Select the analysis configuration
 * Uncomment the region and time period you want to analyze
 */
var WORKFLOW_CONFIG = {
  // Spatial domain - choose one
  region: config.CONTINENTAL_DOMAIN,
  // region: config.REGIONAL_DOMAINS.MOREE_PLAINS,
  // region: config.REGIONAL_DOMAINS.BRIGALOW_BELT,
  // region: config.REGIONAL_DOMAINS.DARLING_DOWNS,
  
  regionName: 'continental',  // Used in export filenames
  
  // Time period
  startDate: config.TIME_PERIOD.PRIMARY_START,
  endDate: config.TIME_PERIOD.PRIMARY_END,
  startYear: '1988',
  endYear: '2023',
  
  // Spatial resolution
  scale: config.SCALES.LANDSAT,
  // scale: config.SCALES.SMOOTH_ANIMATION,  // For smoother animations
  
  // Export options
  exportGeoTIFFs: true,      // Export annual frames as GeoTIFFs
  exportVideo: true,          // Export MP4 animation
  exportTimeSeries: true,     // Export area statistics CSV
  
  // Product to visualize
  product: 'woody_binary'  // Options: 'woody_binary', 'land_cover', 'fractional_cover'
};

print('Workflow Configuration:', WORKFLOW_CONFIG);

// ============================================================================
// STEP 1: LOAD DATA
// ============================================================================

print('=== STEP 1: Loading Data ===');

// Load DEA Land Cover data
var landCoverCollection = utils.loadDEALandCover(
  WORKFLOW_CONFIG.region,
  WORKFLOW_CONFIG.startDate,
  WORKFLOW_CONFIG.endDate
);

print('Land Cover Collection:', landCoverCollection);

// Load DEA Fractional Cover (optional, for background or alternative approach)
var fractionalCoverCollection = utils.loadDEAFractionalCover(
  WORKFLOW_CONFIG.region,
  WORKFLOW_CONFIG.startDate,
  WORKFLOW_CONFIG.endDate
);

print('Fractional Cover Collection:', fractionalCoverCollection);

// Load SLATS data for validation (optional)
// Uncomment if you want to overlay SLATS clearing polygons
// var slatsQLD = utils.loadSLATS('QLD', 'Landsat', WORKFLOW_CONFIG.region);
// var slatsNSW = utils.loadSLATS('NSW', 'Landsat', WORKFLOW_CONFIG.region);

// ============================================================================
// STEP 2: CREATE ANNUAL COMPOSITES
// ============================================================================

print('=== STEP 2: Creating Annual Composites ===');

// Create annual median composites from land cover data
var annualLandCover = utils.createAnnualComposites(
  landCoverCollection,
  WORKFLOW_CONFIG.startYear,
  WORKFLOW_CONFIG.endYear
);

print('Annual Land Cover Composites:', annualLandCover);

// ============================================================================
// STEP 3: GENERATE WOODY/NON-WOODY MASKS
// ============================================================================

print('=== STEP 3: Generating Woody Vegetation Masks ===');

// Convert each annual land cover image to a binary woody mask
var woodyTimeSeries = annualLandCover.map(function(image) {
  var woodyMask = utils.createWoodyMask(image);
  return woodyMask.copyProperties(image, ['year', 'system:time_start']);
});

print('Woody Time Series:', woodyTimeSeries);

// Calculate total woody area for each year
var areaTimeSeries = utils.woodyAreaTimeSeries(
  woodyTimeSeries,
  WORKFLOW_CONFIG.region,
  WORKFLOW_CONFIG.scale
);

print('Area Time Series:', areaTimeSeries);

// ============================================================================
// STEP 4: VISUALIZATION
// ============================================================================

print('=== STEP 4: Creating Visualizations ===');

// Create visualization collection based on selected product
var visualizationCollection;

if (WORKFLOW_CONFIG.product === 'woody_binary') {
  // Binary woody/non-woody visualization
  visualizationCollection = woodyTimeSeries.map(function(image) {
    return image.visualize(config.VIS_PARAMS.BINARY_WOODY)
      .copyProperties(image, ['year', 'system:time_start']);
  });
  
} else if (WORKFLOW_CONFIG.product === 'land_cover') {
  // Full land cover classification
  visualizationCollection = annualLandCover.map(function(image) {
    var simplified = utils.simplifyLandCover(image);
    return utils.visualizeLandCover(simplified)
      .copyProperties(image, ['year', 'system:time_start']);
  });
  
} else if (WORKFLOW_CONFIG.product === 'fractional_cover') {
  // Fractional cover - green vegetation
  visualizationCollection = fractionalCoverCollection.map(function(image) {
    return image.select(config.DEA_FRACTIONAL_COVER.BANDS.GREEN)
      .visualize(config.VIS_PARAMS.FRACTIONAL_GREEN)
      .copyProperties(image, ['year', 'system:time_start']);
  });
}

// Display the first and last frames on the map for quick check
var firstFrame = ee.Image(visualizationCollection.first());
var lastFrame = ee.Image(visualizationCollection.sort('year', false).first());

Map.centerObject(WORKFLOW_CONFIG.region, 6);
Map.addLayer(firstFrame, {}, WORKFLOW_CONFIG.startYear + ' (First Frame)');
Map.addLayer(lastFrame, {}, WORKFLOW_CONFIG.endYear + ' (Last Frame)');
Map.addLayer(WORKFLOW_CONFIG.region, {color: 'red'}, 'Analysis Region', false);

// Add SLATS overlay if loaded
// if (typeof slatsQLD !== 'undefined') {
//   Map.addLayer(slatsQLD, {color: 'orange'}, 'SLATS QLD Clearing', false);
// }

// ============================================================================
// STEP 5: CHANGE DETECTION (Optional)
// ============================================================================

print('=== STEP 5: Change Detection ===');

// Calculate clearing between first and last year
var woodyFirst = ee.Image(woodyTimeSeries.first());
var woodyLast = ee.Image(woodyTimeSeries.sort('year', false).first());
var totalClearing = utils.detectClearing(woodyFirst, woodyLast);

Map.addLayer(
  totalClearing.selfMask().visualize(config.VIS_PARAMS.CLEARING),
  {},
  'Total Clearing (' + WORKFLOW_CONFIG.startYear + '-' + WORKFLOW_CONFIG.endYear + ')',
  false
);

// Calculate area of clearing
var clearingArea = utils.calculateArea(
  totalClearing,
  WORKFLOW_CONFIG.region,
  WORKFLOW_CONFIG.scale
);

print('Total Clearing Area (ha):', 
  ee.Number(clearingArea.get('clearing')).divide(10000));

// ============================================================================
// STEP 6: EXPORT OUTPUTS
// ============================================================================

print('=== STEP 6: Setting Up Exports ===');
print('Go to the Tasks tab to start exports');

/**
 * Export annual GeoTIFF frames
 */
if (WORKFLOW_CONFIG.exportGeoTIFFs) {
  var years = ee.List.sequence(
    parseInt(WORKFLOW_CONFIG.startYear),
    parseInt(WORKFLOW_CONFIG.endYear)
  );
  
  years.getInfo().forEach(function(year) {
    var image = woodyTimeSeries.filter(ee.Filter.eq('year', year)).first();
    
    var filename = utils.generateFilename(
      config.EXPORT_CONFIG.NAMING.PREFIX,
      WORKFLOW_CONFIG.regionName,
      year.toString(),
      WORKFLOW_CONFIG.product
    );
    
    var exportParams = utils.getGeoTIFFExportParams(
      WORKFLOW_CONFIG.region,
      WORKFLOW_CONFIG.scale
    );
    
    Export.image.toDrive({
      image: image,
      description: filename,
      folder: config.EXPORT_CONFIG.DRIVE_FOLDER + '/' + 
              config.EXPORT_CONFIG.FOLDERS.GEOTIFF,
      fileNamePrefix: filename,
      crs: exportParams.crs,
      scale: exportParams.scale,
      region: exportParams.region,
      maxPixels: exportParams.maxPixels,
      fileFormat: exportParams.fileFormat,
      formatOptions: exportParams.formatOptions
    });
  });
  
  print('GeoTIFF export tasks created');
}

/**
 * Export video animation
 */
if (WORKFLOW_CONFIG.exportVideo) {
  var filename = utils.generateFilename(
    config.EXPORT_CONFIG.NAMING.PREFIX,
    WORKFLOW_CONFIG.regionName,
    WORKFLOW_CONFIG.startYear + '_' + WORKFLOW_CONFIG.endYear,
    WORKFLOW_CONFIG.product + '_animation'
  );
  
  var videoParams = utils.getVideoExportParams(WORKFLOW_CONFIG.region);
  
  Export.video.toDrive({
    collection: visualizationCollection,
    description: filename,
    folder: config.EXPORT_CONFIG.DRIVE_FOLDER + '/' + 
            config.EXPORT_CONFIG.FOLDERS.VIDEO,
    fileNamePrefix: filename,
    framesPerSecond: videoParams.framesPerSecond,
    dimensions: videoParams.dimensions,
    region: videoParams.region,
    maxPixels: videoParams.maxPixels,
    crs: videoParams.crs
  });
  
  print('Video export task created');
}

/**
 * Export time series data
 */
if (WORKFLOW_CONFIG.exportTimeSeries) {
  var filename = utils.generateFilename(
    config.EXPORT_CONFIG.NAMING.PREFIX,
    WORKFLOW_CONFIG.regionName,
    WORKFLOW_CONFIG.startYear + '_' + WORKFLOW_CONFIG.endYear,
    'timeseries'
  );
  
  Export.table.toDrive({
    collection: areaTimeSeries,
    description: filename,
    folder: config.EXPORT_CONFIG.DRIVE_FOLDER,
    fileNamePrefix: filename,
    fileFormat: 'CSV'
  });
  
  print('Time series export task created');
}

// ============================================================================
// SUMMARY
// ============================================================================

print('=== Workflow Complete ===');
print('Region:', WORKFLOW_CONFIG.regionName);
print('Time Period:', WORKFLOW_CONFIG.startYear, 'to', WORKFLOW_CONFIG.endYear);
print('Scale:', WORKFLOW_CONFIG.scale, 'meters');
print('Product:', WORKFLOW_CONFIG.product);
print('');
print('Check the Tasks tab to run exports.');
print('Exports will be saved to Google Drive folder:', config.EXPORT_CONFIG.DRIVE_FOLDER);

/**
 * Core Utility Functions for Land Clearing Analysis
 * 
 * This module contains reusable functions for loading, processing, and
 * compositing remote sensing data for land clearing visualization.
 */

var config = require('./config.js');

// ============================================================================
// DATA LOADING FUNCTIONS
// ============================================================================

/**
 * Load DEA Land Cover data for a given time period and region
 * 
 * IMPORTANT: This is a placeholder function. You must:
 * 1. Upload DEA Land Cover data to Google Earth Engine as an ImageCollection
 * 2. Update the ASSET_ID in config.js with your actual asset path
 * 3. Verify the band name matches your data (default: 'level3')
 * 
 * Expected ImageCollection structure:
 * - Each image represents one year of land cover
 * - Image property 'year' or 'system:time_start' indicates the year
 * - Band contains land cover classification codes (see config.LAND_COVER_CLASSES)
 * 
 * Example for loading from GEE asset:
 *   var collection = ee.ImageCollection(config.DEA_LAND_COVER.ASSET_ID)
 *     .filterBounds(region)
 *     .filterDate(startDate, endDate)
 *     .select(config.DEA_LAND_COVER.BAND);
 * 
 * See docs/DATA_SOURCES.md for details on obtaining and uploading DEA data.
 * 
 * @param {ee.Geometry} region - The geographic region of interest
 * @param {string} startDate - Start date (YYYY-MM-DD)
 * @param {string} endDate - End date (YYYY-MM-DD)
 * @return {ee.ImageCollection} Collection of annual land cover images
 */
exports.loadDEALandCover = function(region, startDate, endDate) {
  // Note: Replace with actual DEA Land Cover asset when available
  // This is a placeholder structure
  
  print('Loading DEA Land Cover from', startDate, 'to', endDate);
  print('WARNING: Using placeholder - update ASSET_ID in config.js with your data');
  
  // In practice, you would load from the GEE community catalog or uploaded asset:
  // var collection = ee.ImageCollection(config.DEA_LAND_COVER.ASSET_ID)
  //   .filterBounds(region)
  //   .filterDate(startDate, endDate)
  //   .select(config.DEA_LAND_COVER.BAND);
  
  // Placeholder returns empty collection - replace with actual loading code above
  var collection = ee.ImageCollection([]);
  
  return collection;
};

/**
 * Load DEA Fractional Cover data
 * 
 * @param {ee.Geometry} region - The geographic region of interest
 * @param {string} startDate - Start date (YYYY-MM-DD)
 * @param {string} endDate - End date (YYYY-MM-DD)
 * @return {ee.ImageCollection} Collection of fractional cover images
 */
exports.loadDEAFractionalCover = function(region, startDate, endDate) {
  print('Loading DEA Fractional Cover from', startDate, 'to', endDate);
  
  // Placeholder - replace with actual asset
  // var collection = ee.ImageCollection(config.DEA_FRACTIONAL_COVER.ASSET_ID)
  //   .filterBounds(region)
  //   .filterDate(startDate, endDate)
  //   .select([
  //     config.DEA_FRACTIONAL_COVER.BANDS.GREEN,
  //     config.DEA_FRACTIONAL_COVER.BANDS.NON_GREEN,
  //     config.DEA_FRACTIONAL_COVER.BANDS.BARE
  //   ]);
  
  var collection = ee.ImageCollection([]);
  
  return collection;
};

/**
 * Load SLATS woody vegetation clearing data
 * 
 * @param {string} state - 'QLD' or 'NSW'
 * @param {string} sensor - 'Landsat' or 'Sentinel'
 * @param {ee.Geometry} region - The geographic region of interest
 * @return {ee.FeatureCollection} SLATS clearing polygons
 */
exports.loadSLATS = function(state, sensor, region) {
  print('Loading SLATS data for', state, sensor);
  
  var assetId;
  if (state === 'QLD' && sensor === 'Landsat') {
    assetId = config.SLATS.QLD_LANDSAT.ASSET_ID;
  } else if (state === 'QLD' && sensor === 'Sentinel') {
    assetId = config.SLATS.QLD_SENTINEL.ASSET_ID;
  } else if (state === 'NSW') {
    assetId = config.SLATS.NSW_SEED.ASSET_ID;
  }
  
  // Placeholder - replace with actual asset
  // var features = ee.FeatureCollection(assetId)
  //   .filterBounds(region);
  
  var features = ee.FeatureCollection([]);
  
  return features;
};

// ============================================================================
// CLASSIFICATION AND MASKING FUNCTIONS
// ============================================================================

/**
 * Create a binary woody/non-woody mask from land cover classification
 * 
 * @param {ee.Image} landCoverImage - DEA Land Cover image
 * @return {ee.Image} Binary image (1 = woody, 0 = non-woody)
 */
exports.createWoodyMask = function(landCoverImage) {
  // Extract the woody vegetation classes from config
  var woodyClasses = ee.List(config.LAND_COVER_CLASSES.WOODY.classes);
  
  // Create binary mask: 1 where land cover is in woody classes, 0 otherwise
  var woodyMask = landCoverImage.remap({
    from: woodyClasses,
    to: ee.List.repeat(1, woodyClasses.length()),
    defaultValue: 0
  }).rename('woody');
  
  return woodyMask;
};

/**
 * Create a simplified land cover classification
 * Groups detailed classes into major categories (woody, non-woody, bare, water, urban)
 * 
 * @param {ee.Image} landCoverImage - DEA Land Cover image
 * @return {ee.Image} Simplified classification image
 */
exports.simplifyLandCover = function(landCoverImage) {
  var classified = landCoverImage.remap({
    from: [].concat(
      config.LAND_COVER_CLASSES.WOODY.classes,
      config.LAND_COVER_CLASSES.NON_WOODY.classes,
      config.LAND_COVER_CLASSES.BARE.classes,
      config.LAND_COVER_CLASSES.WATER.classes,
      config.LAND_COVER_CLASSES.URBAN.classes
    ),
    to: [].concat(
      ee.List.repeat(1, config.LAND_COVER_CLASSES.WOODY.classes.length),
      ee.List.repeat(2, config.LAND_COVER_CLASSES.NON_WOODY.classes.length),
      ee.List.repeat(3, config.LAND_COVER_CLASSES.BARE.classes.length),
      ee.List.repeat(4, config.LAND_COVER_CLASSES.WATER.classes.length),
      ee.List.repeat(5, config.LAND_COVER_CLASSES.URBAN.classes.length)
    ),
    defaultValue: 0
  }).rename('simplified_lc');
  
  return classified;
};

/**
 * Calculate woody vegetation fraction from fractional cover data
 * Combines green and non-green vegetation as proxy for woody cover
 * 
 * @param {ee.Image} fcImage - DEA Fractional Cover image
 * @param {number} threshold - Minimum total vegetation % to classify as woody (default: 20)
 * @return {ee.Image} Binary woody mask
 */
exports.woodyFromFractionalCover = function(fcImage, threshold) {
  threshold = threshold || 20;
  
  var greenBand = config.DEA_FRACTIONAL_COVER.BANDS.GREEN;
  var nonGreenBand = config.DEA_FRACTIONAL_COVER.BANDS.NON_GREEN;
  
  // Total vegetation = green + non-green
  var totalVeg = fcImage.select(greenBand).add(fcImage.select(nonGreenBand));
  
  // Classify as woody if total vegetation > threshold
  var woody = totalVeg.gt(threshold).rename('woody_fc');
  
  return woody;
};

// ============================================================================
// CLOUD MASKING AND QUALITY FILTERING
// ============================================================================

/**
 * Apply cloud masking to Landsat imagery
 * This is a generic function that can be adapted based on the specific
 * pixel QA band structure of your data
 * 
 * @param {ee.Image} image - Landsat image with QA band
 * @return {ee.Image} Cloud-masked image
 */
exports.maskClouds = function(image) {
  // This is a placeholder implementation
  // Actual implementation depends on the QA band structure
  // For Landsat Collection 2, you would typically use the QA_PIXEL band
  
  // Example for Landsat Collection 2:
  // var qa = image.select('QA_PIXEL');
  // var cloudBit = 1 << 3;
  // var cloudShadowBit = 1 << 4;
  // var mask = qa.bitwiseAnd(cloudBit).eq(0)
  //   .and(qa.bitwiseAnd(cloudShadowBit).eq(0));
  
  // For DEA products, cloud masking may already be applied
  // Return the image as-is if pre-processed
  return image;
};

/**
 * Filter collection by maximum cloud cover
 * 
 * @param {ee.ImageCollection} collection - Image collection
 * @param {number} maxCloudCover - Maximum cloud cover percentage (0-100)
 * @return {ee.ImageCollection} Filtered collection
 */
exports.filterByCloudCover = function(collection, maxCloudCover) {
  maxCloudCover = maxCloudCover || config.QUALITY_CONTROL.MAX_CLOUD_COVER;
  
  return collection.filter(ee.Filter.lt('CLOUD_COVER', maxCloudCover));
};

// ============================================================================
// TEMPORAL COMPOSITING
// ============================================================================

/**
 * Create annual median composites from an image collection
 * 
 * @param {ee.ImageCollection} collection - Input image collection
 * @param {string} startYear - Start year (YYYY)
 * @param {string} endYear - End year (YYYY)
 * @return {ee.ImageCollection} Collection of annual composites
 */
exports.createAnnualComposites = function(collection, startYear, endYear) {
  var years = ee.List.sequence(parseInt(startYear), parseInt(endYear));
  
  var annualComposites = ee.ImageCollection(years.map(function(year) {
    var startDate = ee.Date.fromYMD(year, 1, 1);
    var endDate = ee.Date.fromYMD(year, 12, 31);
    
    var composite = collection
      .filterDate(startDate, endDate)
      .median()
      .set('year', year)
      .set('system:time_start', startDate.millis());
    
    return composite;
  }));
  
  return annualComposites;
};

/**
 * Create seasonal composites (DJF, MAM, JJA, SON)
 * 
 * @param {ee.ImageCollection} collection - Input image collection
 * @param {number} year - Year for seasonal composites
 * @return {ee.ImageCollection} Collection of seasonal composites
 */
exports.createSeasonalComposites = function(collection, year) {
  var seasons = [
    {name: 'DJF', months: [12, 1, 2], label: 'Summer'},
    {name: 'MAM', months: [3, 4, 5], label: 'Autumn'},
    {name: 'JJA', months: [6, 7, 8], label: 'Winter'},
    {name: 'SON', months: [9, 10, 11], label: 'Spring'}
  ];
  
  var seasonalComposites = ee.ImageCollection(seasons.map(function(season) {
    var filtered = collection.filter(ee.Filter.calendarRange(
      season.months[0], season.months[2], 'month'
    ));
    
    var composite = filtered.median()
      .set('season', season.name)
      .set('season_label', season.label)
      .set('year', year);
    
    return composite;
  }));
  
  return seasonalComposites;
};

// ============================================================================
// CHANGE DETECTION
// ============================================================================

/**
 * Detect clearing events (woody to non-woody transitions)
 * 
 * @param {ee.Image} woodyT1 - Woody mask at time 1 (earlier)
 * @param {ee.Image} woodyT2 - Woody mask at time 2 (later)
 * @return {ee.Image} Clearing mask (1 = cleared, 0 = no change)
 */
exports.detectClearing = function(woodyT1, woodyT2) {
  // Clearing occurs where:
  // - Time 1 was woody (woodyT1 = 1)
  // - Time 2 is non-woody (woodyT2 = 0)
  var clearing = woodyT1.eq(1).and(woodyT2.eq(0)).rename('clearing');
  
  return clearing;
};

/**
 * Calculate cumulative clearing from a time series of woody masks
 * 
 * @param {ee.ImageCollection} woodyTimeSeries - Collection of annual woody masks
 * @return {ee.Image} Cumulative clearing (year of clearing event)
 */
exports.cumulativeClearing = function(woodyTimeSeries) {
  var list = woodyTimeSeries.toList(woodyTimeSeries.size());
  var baseline = ee.Image(list.get(0));
  
  // Iterate through time series to detect first clearing event
  var clearing = ee.Image(list.slice(1).iterate(function(current, previous) {
    current = ee.Image(current);
    previous = ee.Image(previous);
    
    var year = current.get('year');
    var cleared = exports.detectClearing(previous, current);
    
    // Update clearing year where clearing detected and not yet recorded
    var updated = previous.where(
      cleared.and(previous.select('clearing_year').eq(0)),
      ee.Image.constant(year).rename('clearing_year')
    );
    
    return updated;
  }, baseline.addBands(ee.Image.constant(0).rename('clearing_year'))));
  
  return clearing;
};

// ============================================================================
// SPATIAL AGGREGATION
// ============================================================================

/**
 * Calculate area statistics for a given class within a region
 * 
 * @param {ee.Image} image - Binary image (1 = class of interest, 0 = other)
 * @param {ee.Geometry} region - Region for statistics
 * @param {number} scale - Analysis scale in meters
 * @return {ee.Dictionary} Dictionary with area statistics
 */
exports.calculateArea = function(image, region, scale) {
  scale = scale || config.PROJECTION.scale;
  
  var areaImage = image.multiply(ee.Image.pixelArea());
  
  var stats = areaImage.reduceRegion({
    reducer: ee.Reducer.sum(),
    geometry: region,
    scale: scale,
    maxPixels: 1e13,
    crs: config.PROJECTION.crs
  });
  
  return stats;
};

/**
 * Calculate time series of woody vegetation area
 * 
 * @param {ee.ImageCollection} woodyTimeSeries - Collection of annual woody masks
 * @param {ee.Geometry} region - Region for statistics
 * @param {number} scale - Analysis scale in meters
 * @return {ee.FeatureCollection} Time series of area statistics
 */
exports.woodyAreaTimeSeries = function(woodyTimeSeries, region, scale) {
  scale = scale || config.PROJECTION.scale;
  
  var timeSeries = woodyTimeSeries.map(function(image) {
    var area = exports.calculateArea(image, region, scale);
    var year = image.get('year');
    
    return ee.Feature(null, {
      'year': year,
      'woody_area_m2': area.get('woody'),
      'woody_area_ha': ee.Number(area.get('woody')).divide(10000)
    });
  });
  
  return timeSeries;
};

// ============================================================================
// VISUALIZATION HELPERS
// ============================================================================

/**
 * Create RGB visualization from land cover classification
 * 
 * @param {ee.Image} landCoverImage - Simplified land cover image
 * @return {ee.Image} RGB image for visualization
 */
exports.visualizeLandCover = function(landCoverImage) {
  // Color palette for simplified classes
  var palette = [
    config.LAND_COVER_CLASSES.WOODY.color,
    config.LAND_COVER_CLASSES.NON_WOODY.color,
    config.LAND_COVER_CLASSES.BARE.color,
    config.LAND_COVER_CLASSES.WATER.color,
    config.LAND_COVER_CLASSES.URBAN.color
  ];
  
  var viz = landCoverImage.visualize({
    min: 1,
    max: 5,
    palette: palette
  });
  
  return viz;
};

/**
 * Create change visualization highlighting clearing events
 * 
 * @param {ee.Image} baseline - Baseline woody mask
 * @param {ee.Image} current - Current woody mask
 * @return {ee.Image} RGB visualization
 */
exports.visualizeChange = function(baseline, current) {
  var clearing = exports.detectClearing(baseline, current);
  
  // Create RGB: R = clearing, G = current woody, B = baseline woody
  var viz = ee.Image.rgb(
    clearing.multiply(255),
    current.multiply(128),
    baseline.multiply(64)
  );
  
  return viz;
};

// ============================================================================
// EXPORT HELPERS
// ============================================================================

/**
 * Generate export filename from parameters
 * 
 * @param {string} prefix - File prefix
 * @param {string} region - Region name
 * @param {string} year - Year
 * @param {string} product - Product type
 * @return {string} Formatted filename
 */
exports.generateFilename = function(prefix, region, year, product) {
  var parts = [
    prefix,
    region,
    product,
    year
  ];
  
  return parts.join(config.EXPORT_CONFIG.NAMING.SEPARATOR);
};

/**
 * Get export parameters for GeoTIFF
 * 
 * @param {ee.Geometry} region - Export region
 * @param {number} scale - Export scale in meters
 * @return {Object} Export parameters object
 */
exports.getGeoTIFFExportParams = function(region, scale) {
  scale = scale || config.PROJECTION.scale;
  
  return {
    crs: config.PROJECTION.crs,
    scale: scale,
    region: region,
    maxPixels: 1e13,
    fileFormat: 'GeoTIFF',
    formatOptions: config.EXPORT_CONFIG.GEOTIFF.formatOptions
  };
};

/**
 * Get export parameters for video
 * 
 * @param {ee.Geometry} region - Export region
 * @return {Object} Export parameters object
 */
exports.getVideoExportParams = function(region) {
  return {
    crs: config.PROJECTION.crs,
    region: region,
    dimensions: config.EXPORT_CONFIG.VIDEO.dimensions,
    framesPerSecond: config.EXPORT_CONFIG.VIDEO.framesPerSecond,
    maxPixels: 1e13,
    quality: config.EXPORT_CONFIG.VIDEO.quality
  };
};

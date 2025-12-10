/**
 * SLATS Integration Utilities
 * 
 * This module provides functions for working with SLATS (Statewide Landcover 
 * and Trees Study) data from Queensland and NSW, including loading, filtering,
 * validation, and comparison with DEA-derived clearing estimates.
 */

var config = require('../core/config.js');
var utils = require('../core/utils.js');

// ============================================================================
// SLATS DATA LOADING
// ============================================================================

/**
 * Load and filter SLATS clearing data by year range
 * 
 * @param {string} state - 'QLD' or 'NSW'
 * @param {string} sensor - 'Landsat' or 'Sentinel'
 * @param {ee.Geometry} region - Region of interest
 * @param {number} startYear - Start year (inclusive)
 * @param {number} endYear - End year (inclusive)
 * @return {ee.FeatureCollection} Filtered SLATS clearing polygons
 */
exports.loadSLATSByYear = function(state, sensor, region, startYear, endYear) {
  var slats = utils.loadSLATS(state, sensor, region);
  
  // Filter by year range (assumes 'YEAR' or 'year' property in features)
  var filtered = slats.filter(
    ee.Filter.and(
      ee.Filter.gte('YEAR', startYear),
      ee.Filter.lte('YEAR', endYear)
    )
  );
  
  return filtered;
};

/**
 * Convert SLATS vector polygons to raster mask
 * 
 * @param {ee.FeatureCollection} slatsFeatures - SLATS clearing polygons
 * @param {number} scale - Rasterization scale in meters
 * @param {ee.Geometry} region - Region bounds
 * @return {ee.Image} Binary raster (1 = clearing, 0 = no clearing)
 */
exports.slatsToRaster = function(slatsFeatures, scale, region) {
  scale = scale || config.PROJECTION.scale;
  
  // Rasterize based on feature count or area
  var rasterized = slatsFeatures
    .filterBounds(region)
    .reduceToImage({
      properties: ['AREA'],  // Sum area if multiple polygons overlap
      reducer: ee.Reducer.sum()
    })
    .gt(0)  // Convert to binary
    .rename('slats_clearing')
    .clip(region);
  
  return rasterized;
};

// ============================================================================
// VALIDATION AND COMPARISON
// ============================================================================

/**
 * Compare DEA-derived clearing with SLATS ground truth
 * 
 * @param {ee.Image} deaClearing - Binary clearing from DEA (1 = cleared)
 * @param {ee.FeatureCollection} slatsFeatures - SLATS clearing polygons
 * @param {ee.Geometry} region - Analysis region
 * @param {number} scale - Analysis scale in meters
 * @return {ee.Dictionary} Validation statistics
 */
exports.validateWithSLATS = function(deaClearing, slatsFeatures, region, scale) {
  scale = scale || config.PROJECTION.scale;
  
  // Convert SLATS to raster
  var slatsRaster = exports.slatsToRaster(slatsFeatures, scale, region);
  
  // Calculate confusion matrix components
  var agreement = deaClearing.and(slatsRaster);  // Both detected (TP)
  var deaOnly = deaClearing.and(slatsRaster.not());  // DEA only (FP)
  var slatsOnly = slatsRaster.and(deaClearing.not());  // SLATS only (FN)
  var neitherDetected = deaClearing.not().and(slatsRaster.not());  // Both clear (TN)
  
  // Calculate areas
  var stats = ee.Image.cat([
    agreement.rename('true_positive'),
    deaOnly.rename('false_positive'),
    slatsOnly.rename('false_negative'),
    neitherDetected.rename('true_negative')
  ]).multiply(ee.Image.pixelArea()).reduceRegion({
    reducer: ee.Reducer.sum(),
    geometry: region,
    scale: scale,
    maxPixels: 1e13,
    crs: config.PROJECTION.crs
  });
  
  // Calculate accuracy metrics
  var tp = ee.Number(stats.get('true_positive')).divide(10000);  // Convert to hectares
  var fp = ee.Number(stats.get('false_positive')).divide(10000);
  var fn = ee.Number(stats.get('false_negative')).divide(10000);
  var tn = ee.Number(stats.get('true_negative')).divide(10000);
  
  var precision = tp.divide(tp.add(fp));  // TP / (TP + FP)
  var recall = tp.divide(tp.add(fn));     // TP / (TP + FN)
  var f1Score = precision.multiply(recall).multiply(2).divide(precision.add(recall));
  var accuracy = tp.add(tn).divide(tp.add(fp).add(fn).add(tn));
  
  return ee.Dictionary({
    true_positive_ha: tp,
    false_positive_ha: fp,
    false_negative_ha: fn,
    true_negative_ha: tn,
    precision: precision,
    recall: recall,
    f1_score: f1Score,
    overall_accuracy: accuracy
  });
};

/**
 * Create validation visualization comparing DEA and SLATS
 * 
 * @param {ee.Image} deaClearing - Binary clearing from DEA
 * @param {ee.FeatureCollection} slatsFeatures - SLATS clearing polygons
 * @param {ee.Geometry} region - Visualization region
 * @param {number} scale - Rasterization scale
 * @return {ee.Image} RGB visualization
 */
exports.visualizeValidation = function(deaClearing, slatsFeatures, region, scale) {
  scale = scale || config.PROJECTION.scale;
  
  var slatsRaster = exports.slatsToRaster(slatsFeatures, scale, region);
  
  var agreement = deaClearing.and(slatsRaster);
  var deaOnly = deaClearing.and(slatsRaster.not());
  var slatsOnly = slatsRaster.and(deaClearing.not());
  
  // Create RGB visualization
  // R = DEA only (false positives) - Yellow
  // G = Agreement (true positives) - Green
  // B = SLATS only (false negatives) - Red
  var viz = ee.Image.rgb(
    deaOnly.multiply(255).add(agreement.multiply(128)),  // R: Yellow where DEA only, dim where agreement
    agreement.multiply(255),                              // G: Bright where agreement
    slatsOnly.multiply(255)                               // B: Red where SLATS only
  );
  
  return viz;
};

// ============================================================================
// TEMPORAL ANALYSIS WITH SLATS
// ============================================================================

/**
 * Create annual SLATS clearing raster series
 * 
 * @param {ee.FeatureCollection} slatsFeatures - All SLATS clearing polygons
 * @param {number} startYear - Start year
 * @param {number} endYear - End year
 * @param {ee.Geometry} region - Analysis region
 * @param {number} scale - Rasterization scale
 * @return {ee.ImageCollection} Annual SLATS clearing rasters
 */
exports.createAnnualSLATSSeries = function(slatsFeatures, startYear, endYear, region, scale) {
  scale = scale || config.PROJECTION.scale;
  
  var years = ee.List.sequence(startYear, endYear);
  
  var annualSLATS = ee.ImageCollection(years.map(function(year) {
    var yearFeatures = slatsFeatures.filter(ee.Filter.eq('YEAR', year));
    var raster = exports.slatsToRaster(yearFeatures, scale, region);
    return raster.set('year', year);
  }));
  
  return annualSLATS;
};

/**
 * Calculate cumulative SLATS clearing over time
 * 
 * @param {ee.FeatureCollection} slatsFeatures - All SLATS clearing polygons
 * @param {number} startYear - Start year
 * @param {number} endYear - End year
 * @param {ee.Geometry} region - Analysis region
 * @param {number} scale - Rasterization scale
 * @return {ee.Image} Cumulative clearing (year of first clearing)
 */
exports.cumulativeSLATSClearing = function(slatsFeatures, startYear, endYear, region, scale) {
  scale = scale || config.PROJECTION.scale;
  
  var annualSLATS = exports.createAnnualSLATSSeries(
    slatsFeatures, startYear, endYear, region, scale
  );
  
  // Track year of first clearing
  var clearingYear = ee.Image(annualSLATS.iterate(function(current, previous) {
    current = ee.Image(current);
    previous = ee.Image(previous);
    
    var year = current.get('year');
    var cleared = current.select('slats_clearing');
    
    // Update clearing year where clearing detected and not yet recorded
    return previous.where(
      cleared.and(previous.eq(0)),
      ee.Image.constant(year)
    ).set('year', year);
  }, ee.Image.constant(0).rename('clearing_year')));
  
  return clearingYear.select('clearing_year');
};

// ============================================================================
// SLATS SUMMARY STATISTICS
// ============================================================================

/**
 * Calculate SLATS clearing statistics by year
 * 
 * @param {ee.FeatureCollection} slatsFeatures - SLATS clearing polygons
 * @param {number} startYear - Start year
 * @param {number} endYear - End year
 * @param {ee.Geometry} region - Analysis region
 * @return {ee.FeatureCollection} Annual clearing statistics
 */
exports.slatsAnnualStats = function(slatsFeatures, startYear, endYear, region) {
  var years = ee.List.sequence(startYear, endYear);
  
  var stats = ee.FeatureCollection(years.map(function(year) {
    var yearFeatures = slatsFeatures
      .filterBounds(region)
      .filter(ee.Filter.eq('YEAR', year));
    
    // Sum clearing area for the year
    var totalArea = yearFeatures.aggregate_sum('AREA');
    var count = yearFeatures.size();
    
    return ee.Feature(null, {
      year: year,
      clearing_count: count,
      clearing_area_m2: totalArea,
      clearing_area_ha: ee.Number(totalArea).divide(10000)
    });
  }));
  
  return stats;
};

/**
 * Compare DEA and SLATS annual clearing rates
 * 
 * @param {ee.ImageCollection} deaWoodyTimeSeries - DEA annual woody masks
 * @param {ee.FeatureCollection} slatsFeatures - SLATS clearing polygons
 * @param {ee.Geometry} region - Analysis region
 * @param {number} scale - Analysis scale
 * @return {ee.FeatureCollection} Comparison statistics
 */
exports.compareAnnualClearing = function(deaWoodyTimeSeries, slatsFeatures, region, scale) {
  scale = scale || config.PROJECTION.scale;
  
  var years = deaWoodyTimeSeries.aggregate_array('year').distinct().sort();
  
  var comparison = ee.FeatureCollection(years.map(function(year) {
    year = ee.Number(year);
    
    // DEA clearing (year to year+1)
    var woodyT1 = deaWoodyTimeSeries.filter(ee.Filter.eq('year', year)).first();
    var woodyT2 = deaWoodyTimeSeries.filter(ee.Filter.eq('year', year.add(1))).first();
    var deaClearing = utils.detectClearing(woodyT1, woodyT2);
    var deaArea = utils.calculateArea(deaClearing, region, scale);
    
    // SLATS clearing for this year
    var slatsYear = slatsFeatures
      .filterBounds(region)
      .filter(ee.Filter.eq('YEAR', year));
    var slatsArea = slatsYear.aggregate_sum('AREA');
    
    return ee.Feature(null, {
      year: year,
      dea_clearing_ha: ee.Number(deaArea.get('clearing')).divide(10000),
      slats_clearing_ha: ee.Number(slatsArea).divide(10000),
      difference_ha: ee.Number(deaArea.get('clearing')).divide(10000)
        .subtract(ee.Number(slatsArea).divide(10000))
    });
  }));
  
  return comparison;
};

// ============================================================================
// EXPORT HELPERS
// ============================================================================

/**
 * Export SLATS validation results
 * 
 * @param {ee.Dictionary} validationStats - Results from validateWithSLATS
 * @param {string} regionName - Name for export
 * @param {string} period - Time period label
 */
exports.exportValidationStats = function(validationStats, regionName, period) {
  var feature = ee.Feature(null, validationStats);
  var collection = ee.FeatureCollection([feature]);
  
  Export.table.toDrive({
    collection: collection,
    description: 'slats_validation_' + regionName + '_' + period,
    folder: config.EXPORT_CONFIG.DRIVE_FOLDER + '/validation',
    fileNamePrefix: 'slats_validation_' + regionName + '_' + period,
    fileFormat: 'CSV'
  });
};

/**
 * Export annual comparison table
 * 
 * @param {ee.FeatureCollection} comparisonStats - Results from compareAnnualClearing
 * @param {string} regionName - Name for export
 */
exports.exportAnnualComparison = function(comparisonStats, regionName) {
  Export.table.toDrive({
    collection: comparisonStats,
    description: 'dea_slats_comparison_' + regionName,
    folder: config.EXPORT_CONFIG.DRIVE_FOLDER + '/validation',
    fileNamePrefix: 'dea_slats_annual_comparison_' + regionName,
    fileFormat: 'CSV'
  });
};

// Export the module
exports.config = config;
exports.utils = utils;

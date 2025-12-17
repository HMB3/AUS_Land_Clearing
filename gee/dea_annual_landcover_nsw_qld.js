/*
 * DEA Annual Landcover Export for NSW and Queensland
 * 
 * Google Earth Engine script to export DEA-compatible annual landcover
 * products to GeoTIFF format for NSW and QLD (1988-present).
 * 
 * This script provides an alternative to Python/ODC processing route,
 * using Google Earth Engine's cloud-based infrastructure for data
 * processing and export.
 * 
 * USAGE:
 *   1. Copy this script to Google Earth Engine Code Editor
 *      (https://code.earthengine.google.com/)
 *   2. Authenticate with your Google account
 *   3. Customize parameters in the CONFIGURATION section below
 *   4. Run the script (press Run button or Ctrl+Enter)
 *   5. Check Tasks tab for export status
 *   6. Exports will be saved to Google Drive or Earth Engine Assets
 * 
 * DATA SOURCE:
 *   Primary: DEA Annual Landcover (if available in GEE)
 *   Fallback: ESA WorldCover or Dynamic World for demonstration
 * 
 * OUTPUT:
 *   - Yearly GeoTIFF files with woody/non-woody classification
 *   - 0 = Other/masked (water, urban, bare, clouds)
 *   - 1 = Woody vegetation (forests, woodlands)
 *   - 2 = Non-woody vegetation (grasslands, crops, wetlands)
 * 
 * NOTES:
 *   - DEA Annual Landcover may not be directly available in GEE
 *   - This template uses ESA WorldCover as a fallback example
 *   - Adjust class mapping based on your chosen dataset
 *   - For authentic DEA data, use Python/ODC route
 * 
 * Author: AUS Land Clearing Project
 * Date: 2024-12
 * Repository: https://github.com/HMB3/AUS_Land_Clearing
 */

// ==============================================================================
// CONFIGURATION
// ==============================================================================

// Study area selection
var STATE = 'NSW';  // Options: 'NSW', 'QLD', or 'BOTH'

// Time period
// Note: Update these values as new data becomes available
// ESA WorldCover: 2020-2021 (current available years)
// For full Landsat record (1988-present), use Python/ODC route with DEA data
var START_YEAR = 2020;
var END_YEAR = 2023;

// Export settings
var EXPORT_TO_DRIVE = true;  // true = Google Drive, false = Earth Engine Asset
var EXPORT_FOLDER = 'AUS_Land_Clearing';  // Folder name in Drive or Assets
var EXPORT_SCALE = 25;  // Resolution in meters (25m matches DEA)
var EXPORT_CRS = 'EPSG:3577';  // Australian Albers (use EPSG:4326 for WGS84)

// Data source selection
// Note: DEA products are not directly available in GEE
// This template uses ESA WorldCover as an example
var USE_ESA_WORLDCOVER = true;  // Set to true for this template
var USE_DYNAMIC_WORLD = false;  // Alternative: Google/WRI Dynamic World

// ==============================================================================
// STUDY AREA GEOMETRIES
// ==============================================================================

// NSW boundary (approximate bounding box)
var nswBounds = ee.Geometry.Rectangle([140.9, -38.0, 153.6, -28.1]);

// Queensland boundary (approximate bounding box)
var qldBounds = ee.Geometry.Rectangle([138.0, -29.2, 154.0, -10.0]);

// Select geometry based on configuration
var geometry;
if (STATE === 'NSW') {
  geometry = nswBounds;
  print('Processing: New South Wales');
} else if (STATE === 'QLD') {
  geometry = qldBounds;
  print('Processing: Queensland');
} else {
  geometry = nswBounds.union(qldBounds);
  print('Processing: NSW + QLD');
}

// Center map on study area
Map.centerObject(geometry, 6);
Map.addLayer(geometry, {color: 'red'}, 'Study Area', false);

// ==============================================================================
// DATA LOADING AND PROCESSING FUNCTIONS
// ==============================================================================

/**
 * Load ESA WorldCover annual landcover
 * Available: 2020, 2021
 * https://developers.google.com/earth-engine/datasets/catalog/ESA_WorldCover_v200
 */
function loadESAWorldCover(year) {
  var dataset = ee.ImageCollection('ESA/WorldCover/v200')
    .filterDate(year + '-01-01', year + '-12-31')
    .first();
  
  return dataset.select('Map');
}

/**
 * Load Dynamic World annual composite (alternative)
 * Available: 2016-present
 */
function loadDynamicWorld(year, geometry) {
  var startDate = ee.Date.fromYMD(year, 1, 1);
  var endDate = ee.Date.fromYMD(year, 12, 31);
  
  var dw = ee.ImageCollection('GOOGLE/DYNAMICWORLD/V1')
    .filterDate(startDate, endDate)
    .filterBounds(geometry)
    .select('label')
    .mode();  // Most common class per pixel
  
  return dw;
}

/**
 * Reclassify ESA WorldCover to woody/non-woody scheme
 * 
 * ESA WorldCover Classes:
 *   10 = Tree cover
 *   20 = Shrubland
 *   30 = Grassland
 *   40 = Cropland
 *   50 = Built-up
 *   60 = Bare / sparse vegetation
 *   70 = Snow and ice
 *   80 = Permanent water bodies
 *   90 = Herbaceous wetland
 *   95 = Mangroves
 *   100 = Moss and lichen
 * 
 * Output Classes:
 *   0 = Other (water, urban, bare, ice)
 *   1 = Woody (trees, shrubs, mangroves)
 *   2 = Non-woody (grassland, cropland, wetland)
 */
function reclassifyESAToWoodyNonwoody(image) {
  var woody = image.eq(10)      // Tree cover
                .or(image.eq(20))  // Shrubland
                .or(image.eq(95)); // Mangroves
  
  var nonWoody = image.eq(30)      // Grassland
                  .or(image.eq(40))  // Cropland
                  .or(image.eq(90)); // Herbaceous wetland
  
  // Create output: 0=other, 1=woody, 2=non-woody
  var classified = ee.Image(0)
    .where(woody, 1)
    .where(nonWoody, 2)
    .rename('landcover_class')
    .uint8();
  
  return classified;
}

/**
 * Reclassify Dynamic World to woody/non-woody scheme
 * 
 * Dynamic World Classes (0-8):
 *   0 = Water
 *   1 = Trees
 *   2 = Grass
 *   3 = Flooded vegetation
 *   4 = Crops
 *   5 = Shrub and scrub
 *   6 = Built area
 *   7 = Bare ground
 *   8 = Snow and ice
 */
function reclassifyDynamicWorldToWoodyNonwoody(image) {
  var woody = image.eq(1)      // Trees
                .or(image.eq(5));  // Shrub and scrub
  
  var nonWoody = image.eq(2)      // Grass
                  .or(image.eq(3))  // Flooded vegetation
                  .or(image.eq(4)); // Crops
  
  var classified = ee.Image(0)
    .where(woody, 1)
    .where(nonWoody, 2)
    .rename('landcover_class')
    .uint8();
  
  return classified;
}

// ==============================================================================
// PROCESSING AND EXPORT
// ==============================================================================

print('=== DEA Annual Landcover Export ===');
print('Configuration:');
print('  State:', STATE);
print('  Years:', START_YEAR, 'to', END_YEAR);
print('  Resolution:', EXPORT_SCALE, 'meters');
print('  CRS:', EXPORT_CRS);
print('  Export to:', EXPORT_TO_DRIVE ? 'Google Drive' : 'Earth Engine Assets');

// Process each year
for (var year = START_YEAR; year <= END_YEAR; year++) {
  
  print('\nProcessing year:', year);
  
  // Load data
  var landcover;
  if (USE_ESA_WORLDCOVER) {
    // ESA WorldCover available for 2020, 2021
    if (year >= 2020 && year <= 2021) {
      landcover = loadESAWorldCover(year);
      var classified = reclassifyESAToWoodyNonwoody(landcover);
    } else {
      print('  Warning: ESA WorldCover not available for', year);
      print('  Skipping...');
      continue;
    }
  } else if (USE_DYNAMIC_WORLD) {
    landcover = loadDynamicWorld(year, geometry);
    var classified = reclassifyDynamicWorldToWoodyNonwoody(landcover);
  } else {
    print('  Error: No data source selected');
    continue;
  }
  
  // Clip to study area
  var clipped = classified.clip(geometry);
  
  // Add to map (only show last year to avoid clutter)
  if (year === END_YEAR) {
    var visParams = {
      min: 0,
      max: 2,
      palette: ['gray', 'darkgreen', 'lightgreen']
    };
    Map.addLayer(clipped, visParams, 'Landcover ' + year);
  }
  
  // Export
  var exportName = STATE + '_landcover_' + year;
  var description = 'DEA_Landcover_' + STATE + '_' + year;
  
  if (EXPORT_TO_DRIVE) {
    // Export to Google Drive
    Export.image.toDrive({
      image: clipped,
      description: description,
      folder: EXPORT_FOLDER,
      fileNamePrefix: exportName,
      scale: EXPORT_SCALE,
      region: geometry,
      crs: EXPORT_CRS,
      maxPixels: 1e13,
      fileFormat: 'GeoTIFF',
      formatOptions: {
        cloudOptimized: true
      }
    });
  } else {
    // Export to Earth Engine Asset
    Export.image.toAsset({
      image: clipped,
      description: description,
      assetId: EXPORT_FOLDER + '/' + exportName,
      scale: EXPORT_SCALE,
      region: geometry,
      crs: EXPORT_CRS,
      maxPixels: 1e13
    });
  }
  
  print('  ✓ Export task created:', exportName);
}

// ==============================================================================
// INSTRUCTIONS
// ==============================================================================

print('\n=== Next Steps ===');
print('1. Check the Tasks tab (right panel)');
print('2. Click RUN for each export task');
print('3. Exports will appear in your Google Drive folder:', EXPORT_FOLDER);
print('4. Download GeoTIFFs and use with Python scripts for animation');
print('\nNote: This template uses ESA WorldCover as DEA data is not in GEE.');
print('For authentic DEA Annual Landcover, use the Python/ODC processing route.');

// ==============================================================================
// LEGEND
// ==============================================================================

// Create legend
var legend = ui.Panel({
  style: {
    position: 'bottom-left',
    padding: '8px 15px'
  }
});

var legendTitle = ui.Label({
  value: 'Landcover Classes',
  style: {
    fontWeight: 'bold',
    fontSize: '16px',
    margin: '0 0 4px 0',
    padding: '0'
  }
});

legend.add(legendTitle);

var makeRow = function(color, name) {
  var colorBox = ui.Label({
    style: {
      backgroundColor: color,
      padding: '8px',
      margin: '0 0 4px 0'
    }
  });
  
  var description = ui.Label({
    value: name,
    style: {margin: '0 0 4px 6px'}
  });
  
  return ui.Panel({
    widgets: [colorBox, description],
    layout: ui.Panel.Layout.Flow('horizontal')
  });
};

legend.add(makeRow('gray', '0 - Other (water, urban, bare)'));
legend.add(makeRow('darkgreen', '1 - Woody vegetation'));
legend.add(makeRow('lightgreen', '2 - Non-woody vegetation'));

Map.add(legend);

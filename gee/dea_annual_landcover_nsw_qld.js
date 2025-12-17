/*
 * DEA Annual Land Cover Processing for NSW and QLD
 * Google Earth Engine Script Template
 * 
 * IMPORTANT NOTICE:
 * =================
 * As of this writing, Digital Earth Australia (DEA) products may not be
 * directly available in Google Earth Engine's public data catalog.
 * 
 * DEA products are primarily accessed through:
 * 1. Open Data Cube (ODC) instances
 * 2. DEA STAC API (https://explorer.dea.ga.gov.au/stac/)
 * 3. Direct download from DEA's data repository
 * 
 * FALLBACK OPTIONS IN GEE:
 * ========================
 * If DEA Land Cover is not available in GEE, consider these alternatives:
 * 
 * 1. Use ESA WorldCover (10m, annual since 2020)
 *    - Available in GEE as: ESA/WorldCover/v100 and v200
 *    - Global coverage with tree cover class
 * 
 * 2. Use Dynamic World (10m, near-real-time)
 *    - Available in GEE as: GOOGLE/DYNAMICWORLD/V1
 *    - Continuous monitoring, includes trees class
 * 
 * 3. Use GLAD Land Cover (30m)
 *    - Available in GEE as: UMD/GLAD/PRIMARY_HUMID_TROPICAL_FORESTS/v1
 *    - Focus on tropical forests
 * 
 * 4. Create land cover from Landsat
 *    - Use USGS Landsat Collection 2
 *    - Classify vegetation using NDVI, EVI, or machine learning
 * 
 * This template demonstrates the workflow structure for annual land cover
 * processing. Adapt it to use available GEE datasets.
 */

// ============================================================================
// CONFIGURATION
// ============================================================================

// Study area: NSW and QLD boundaries
// Load from GEE's FAO GAUL dataset or use imported assets
var aus_states = ee.FeatureCollection('FAO/GAUL/2015/level1')
  .filter(ee.Filter.eq('ADM0_NAME', 'Australia'));

var nsw = aus_states.filter(ee.Filter.eq('ADM1_NAME', 'New South Wales'));
var qld = aus_states.filter(ee.Filter.eq('ADM1_NAME', 'Queensland'));

// Time period
var startYear = 1988;
var endYear = 2024;

// Output configuration
var crs = 'EPSG:3577';  // GDA94 Australian Albers
var scale = 25;  // meters (DEA native resolution)

// ============================================================================
// ALTERNATIVE DATA SOURCE EXAMPLE: ESA WorldCover
// ============================================================================

/**
 * Process ESA WorldCover data (available from 2020 onwards)
 * WorldCover classes: 10=Tree cover, 20=Shrubland, 30=Grassland, etc.
 */
function processESAWorldCover(year, region, regionName) {
  
  // ESA WorldCover is only available from 2020
  if (year < 2020) {
    print('ESA WorldCover not available for ' + year);
    return null;
  }
  
  // Load ESA WorldCover for the year
  var collection = (year === 2020) ? 'ESA/WorldCover/v100' : 'ESA/WorldCover/v200';
  var worldcover = ee.ImageCollection(collection)
    .filterBounds(region)
    .first();
  
  if (!worldcover) {
    print('No WorldCover data for ' + year);
    return null;
  }
  
  // Reclassify to woody (1) / non-woody (0)
  // WorldCover: 10=trees (woody), others=non-woody
  var woody = worldcover.select('Map').eq(10)  // Trees
    .or(worldcover.select('Map').eq(20));  // Shrubland (partially woody)
  
  // Rename for clarity
  woody = woody.rename('woody').byte();
  
  // Set metadata
  woody = woody.set({
    'year': year,
    'region': regionName,
    'source': 'ESA WorldCover',
    'system:time_start': ee.Date.fromYMD(year, 1, 1).millis()
  });
  
  return woody;
}

// ============================================================================
// TEMPLATE: DEA-LIKE PROCESSING FROM LANDSAT
// ============================================================================

/**
 * Process Landsat data to create woody/non-woody classification
 * This is a simplified example - production code would use more sophisticated
 * classification methods.
 */
function processLandsatWoody(year, region, regionName) {
  
  // Load Landsat data for the year
  var landsat = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')
    .filterBounds(region)
    .filterDate(year + '-01-01', year + '-12-31')
    .filter(ee.Filter.lt('CLOUD_COVER', 30));
  
  if (landsat.size().getInfo() === 0) {
    print('No Landsat data for ' + year);
    return null;
  }
  
  // Calculate median composite
  var composite = landsat.median();
  
  // Calculate NDVI (simple woody vegetation proxy)
  var ndvi = composite.normalizedDifference(['SR_B5', 'SR_B4'])
    .rename('NDVI');
  
  // Threshold for woody vegetation (adjust as needed)
  // This is a very simplified classification
  var woody = ndvi.gt(0.4).rename('woody').byte();
  
  // Set metadata
  woody = woody.set({
    'year': year,
    'region': regionName,
    'source': 'Landsat 8',
    'system:time_start': ee.Date.fromYMD(year, 1, 1).millis()
  });
  
  return woody;
}

// ============================================================================
// MAIN PROCESSING LOOP
// ============================================================================

/**
 * Process annual land cover for a region across all years
 */
function processRegionTimeSeries(region, regionName, startYear, endYear) {
  
  print('Processing ' + regionName + ' (' + startYear + '-' + endYear + ')');
  
  var years = ee.List.sequence(startYear, endYear);
  
  // Process each year
  years.evaluate(function(yearsList) {
    yearsList.forEach(function(year) {
      
      // Choose processing method based on data availability
      var woody = null;
      
      // Try ESA WorldCover first (2020+)
      if (year >= 2020) {
        woody = processESAWorldCover(year, region, regionName);
      }
      
      // Fallback to Landsat-based classification (2013+ for Landsat 8)
      if (!woody && year >= 2013) {
        woody = processLandsatWoody(year, region, regionName);
      }
      
      if (woody) {
        // Visualize
        Map.addLayer(
          woody.clip(region),
          {min: 0, max: 1, palette: ['white', 'darkgreen']},
          regionName + ' ' + year
        );
        
        // Export as GeoTIFF
        Export.image.toDrive({
          image: woody,
          description: regionName.toLowerCase().replace(' ', '_') + '_woody_' + year,
          folder: 'DEA_LandCover',
          region: region.geometry(),
          crs: crs,
          scale: scale,
          maxPixels: 1e13,
          fileFormat: 'GeoTIFF'
        });
      }
    });
  });
}

// ============================================================================
// EXECUTION
// ============================================================================

// Center map on Australia
Map.setCenter(133.7751, -25.2744, 4);

// Add state boundaries to map
Map.addLayer(nsw, {color: 'blue'}, 'NSW', false);
Map.addLayer(qld, {color: 'red'}, 'QLD', false);

// Process NSW
// Uncomment the line below to start processing
// processRegionTimeSeries(nsw, 'NSW', 2020, 2023);  // Example: limited years

// Process QLD
// Uncomment the line below to start processing  
// processRegionTimeSeries(qld, 'QLD', 2020, 2023);  // Example: limited years

print('='.repeat(70));
print('DEA Annual Land Cover - GEE Template');
print('='.repeat(70));
print('');
print('IMPORTANT: DEA products may not be available in GEE.');
print('This template uses alternative datasets (ESA WorldCover, Landsat).');
print('');
print('To run processing:');
print('1. Uncomment processRegionTimeSeries() calls above');
print('2. Adjust year range as needed');
print('3. Click "Run" and check the Tasks tab to export results');
print('');
print('For native DEA data access, use:');
print('  - Open Data Cube (Python)');
print('  - DEA STAC API');
print('  - Direct download from DEA repository');
print('');
print('See README.md for Python/ODC processing scripts.');
print('='.repeat(70));

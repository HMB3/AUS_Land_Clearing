/**
 * Global Configuration for AUS Land Clearing Visualization
 * 
 * This file contains all configurable parameters for the land clearing
 * analysis workflow. Modify these settings to change time periods, spatial
 * domains, or output specifications.
 */

// ============================================================================
// SPATIAL CONFIGURATION
// ============================================================================

/**
 * Primary projection for all outputs
 * EPSG:3577 - Australian Albers Equal Area Conic
 * This projection is optimized for Australia-wide analysis and area calculations
 */
exports.PROJECTION = {
  crs: 'EPSG:3577',
  scale: 25  // Target resolution in meters (25-30m for Landsat products)
};

/**
 * Alternative scales for different use cases
 */
exports.SCALES = {
  LANDSAT: 25,           // DEA Land Cover / Landsat products
  SENTINEL: 10,          // Sentinel-2 based SLATS products
  SMOOTH_ANIMATION: 60,  // Coarser for smoother animations
  CONTINENTAL: 250       // Continental overviews
};

// ============================================================================
// TEMPORAL CONFIGURATION
// ============================================================================

/**
 * Primary analysis period (Landsat-era)
 */
exports.TIME_PERIOD = {
  PRIMARY_START: '1988-01-01',
  PRIMARY_END: '2024-12-31',
  
  // Extended period using Australia-wide datasets
  EXTENDED_START: '1985-01-01',
  
  // Sentinel-2 era (2015+)
  SENTINEL_START: '2015-01-01'
};

/**
 * Temporal compositing windows
 * Define how to aggregate data within each time step
 */
exports.COMPOSITE_WINDOWS = {
  ANNUAL: 'year',
  SEASONAL: 'season',  // For higher temporal resolution animations
  QUARTERLY: 'quarter'
};

// ============================================================================
// SPATIAL DOMAINS
// ============================================================================

/**
 * Continental-scale domain: Eastern Australia
 * Covers the eastern seaboard and agricultural interior
 */
exports.CONTINENTAL_DOMAIN = ee.Geometry.Polygon(
  [[[135, -10], [155, -10], [155, -39], [135, -39], [135, -10]]],
  null, false
);

/**
 * Regional case study areas
 */
exports.REGIONAL_DOMAINS = {
  // Moree Plains, NSW - Major agricultural region with significant clearing history
  MOREE_PLAINS: ee.Geometry.Polygon(
    [[[148.5, -29.0], [150.5, -29.0], [150.5, -30.5], [148.5, -30.5], [148.5, -29.0]]],
    null, false
  ),
  
  // Brigalow Belt, QLD - Iconic clearing region
  BRIGALOW_BELT: ee.Geometry.Polygon(
    [[[148.0, -24.0], [151.0, -24.0], [151.0, -28.0], [148.0, -28.0], [148.0, -24.0]]],
    null, false
  ),
  
  // Darling Downs, QLD - Major agricultural area
  DARLING_DOWNS: ee.Geometry.Polygon(
    [[[150.5, -27.0], [152.5, -27.0], [152.5, -28.5], [150.5, -28.5], [150.5, -27.0]]],
    null, false
  )
};

// ============================================================================
// DATA SOURCE IDENTIFIERS
// ============================================================================

/**
 * DEA Land Cover (Landsat) - Annual classifications
 * Available in GEE Community Catalog
 * 
 * SETUP INSTRUCTIONS:
 * 1. Option A - Use GEE Community Catalog (if available):
 *    Check https://developers.google.com/earth-engine/datasets for DEA products
 * 
 * 2. Option B - Upload your own data:
 *    a. Download DEA Land Cover from https://knowledge.dea.ga.gov.au/
 *    b. Upload to GEE using Asset Manager or Earth Engine CLI
 *    c. Update ASSET_ID below with your asset path
 * 
 * 3. Verify band names match your data (print band names in Code Editor)
 * 
 * See docs/DATA_SOURCES.md for detailed instructions and data specifications.
 */
exports.DEA_LAND_COVER = {
  // Replace with actual GEE asset path when available
  // Examples:
  //   'projects/dea-public/assets/land_cover'  (if in community catalog)
  //   'projects/YOUR_PROJECT/assets/dea_land_cover'  (if you upload it)
  ASSET_ID: 'projects/YOUR_PROJECT/assets/dea_land_cover',
  BAND: 'level3',  // Land cover classification band
  START_YEAR: 1988,
  END_YEAR: 2023
};

/**
 * DEA Fractional Cover (Landsat)
 * Green vegetation / Non-green vegetation / Bare soil fractions
 */
exports.DEA_FRACTIONAL_COVER = {
  // Replace with actual GEE asset path when available
  ASSET_ID: 'projects/YOUR_PROJECT/assets/dea_fractional_cover',
  BANDS: {
    GREEN: 'PV',    // Photosynthetic (green) vegetation
    NON_GREEN: 'NPV', // Non-photosynthetic vegetation
    BARE: 'BS'      // Bare soil
  }
};

/**
 * SLATS woody vegetation clearing data
 */
exports.SLATS = {
  QLD_LANDSAT: {
    ASSET_ID: 'projects/YOUR_PROJECT/assets/slats_qld_woody_clearing',
    DESCRIPTION: 'Queensland SLATS woody vegetation clearing (Landsat)'
  },
  QLD_SENTINEL: {
    ASSET_ID: 'projects/YOUR_PROJECT/assets/slats_qld_woody_clearing_s2',
    DESCRIPTION: 'Queensland SLATS woody vegetation clearing (Sentinel-2)',
    START_YEAR: 2015
  },
  NSW_SEED: {
    ASSET_ID: 'projects/YOUR_PROJECT/assets/nsw_slats_clearing',
    DESCRIPTION: 'NSW SLATS-equivalent clearing polygons from SEED'
  }
};

// ============================================================================
// CLASSIFICATION SCHEMES
// ============================================================================

/**
 * Land cover class definitions and groupings
 * These map DEA Land Cover classes to simplified categories for visualization
 */
exports.LAND_COVER_CLASSES = {
  // Woody vegetation classes (trees, shrubs)
  WOODY: {
    name: 'Woody Vegetation',
    classes: [111, 112, 113, 121, 122, 123, 124, 125, 126],
    color: '1a5928',  // Dark green
    description: 'Trees, shrubs, and woody vegetation'
  },
  
  // Non-woody vegetation (grasses, crops)
  NON_WOODY: {
    name: 'Non-Woody Vegetation',
    classes: [211, 212, 213, 214, 215, 216],
    color: '78d203',  // Light green
    description: 'Grasses, crops, and herbaceous vegetation'
  },
  
  // Bare/sparse
  BARE: {
    name: 'Bare/Sparse',
    classes: [221, 222, 223],
    color: 'e8b520',  // Yellow/tan
    description: 'Bare soil, sparse vegetation'
  },
  
  // Water
  WATER: {
    name: 'Water',
    classes: [311, 312, 313, 314, 315],
    color: '0060ff',  // Blue
    description: 'Water bodies'
  },
  
  // Urban/Built
  URBAN: {
    name: 'Urban/Built',
    classes: [411, 412],
    color: 'ff0000',  // Red
    description: 'Urban and built-up areas'
  }
};

/**
 * Simplified binary classification for clearing detection
 */
exports.BINARY_CLASSES = {
  WOODY: {
    name: 'Woody',
    value: 1,
    color: '1a5928'
  },
  NON_WOODY: {
    name: 'Non-Woody',
    value: 0,
    color: 'e8b520'
  }
};

// ============================================================================
// EXPORT CONFIGURATION
// ============================================================================

/**
 * Output directory structure in Google Drive
 */
exports.EXPORT_CONFIG = {
  DRIVE_FOLDER: 'AUS_Land_Clearing',
  
  // Subdirectories for different products
  FOLDERS: {
    GEOTIFF: 'geotiff_frames',
    VIDEO: 'animations',
    THUMBNAIL: 'thumbnails',
    CONTINENTAL: 'continental',
    REGIONAL: 'regional'
  },
  
  // File naming conventions
  NAMING: {
    PREFIX: 'aus_lc',
    SEPARATOR: '_',
    DATE_FORMAT: 'YYYY'  // Annual outputs
  },
  
  // Export parameters
  GEOTIFF: {
    fileFormat: 'GeoTIFF',
    formatOptions: {
      cloudOptimized: true,
      noData: -9999
    }
  },
  
  VIDEO: {
    fileFormat: 'mp4',
    framesPerSecond: 2,  // 2 frames per second = one year every 0.5 seconds
    dimensions: 1920,    // HD video
    quality: 95
  }
};

// ============================================================================
// VISUALIZATION PARAMETERS
// ============================================================================

/**
 * Color palettes for different visualization types
 */
exports.VIS_PARAMS = {
  // Binary woody vs non-woody
  BINARY_WOODY: {
    min: 0,
    max: 1,
    palette: ['e8b520', '1a5928']  // Non-woody to woody
  },
  
  // Fractional cover - green vegetation
  FRACTIONAL_GREEN: {
    min: 0,
    max: 100,
    palette: ['ffffff', '78d203', '1a5928']  // White to light green to dark green
  },
  
  // Fractional cover - bare soil
  FRACTIONAL_BARE: {
    min: 0,
    max: 100,
    palette: ['ffffff', 'e8b520', '8b4513']  // White to tan to brown
  },
  
  // Change detection (loss of woody vegetation)
  CLEARING: {
    min: 0,
    max: 1,
    palette: ['dddddd', 'ff0000']  // Grey (no change) to red (cleared)
  }
};

// ============================================================================
// QUALITY CONTROL
// ============================================================================

/**
 * Cloud masking and quality filtering thresholds
 */
exports.QUALITY_CONTROL = {
  // Maximum cloud cover percentage for including an image
  MAX_CLOUD_COVER: 20,
  
  // Minimum observations required for compositing
  MIN_OBSERVATIONS: 3,
  
  // Quality flags to exclude (if using pixel QA bands)
  EXCLUDE_FLAGS: ['cloud', 'cloud_shadow', 'snow']
};

// ============================================================================
// SCIENTIFIC ASSUMPTIONS (DOCUMENTATION)
// ============================================================================

/**
 * Key assumptions and interpretations for this analysis
 * 
 * CLEARING DEFINITION:
 * - "Clearing" is defined as the conversion of woody vegetation (trees/shrubs)
 *   to non-woody vegetation or bare soil
 * - We use DEA Land Cover Level 3 classifications as the authoritative source
 * - SLATS data is used for validation and anchoring the narrative
 * 
 * WOODY VEGETATION:
 * - Includes all forest and shrubland classes from DEA Land Cover
 * - Threshold: >20% canopy cover (implicit in DEA classification)
 * 
 * TEMPORAL COMPOSITING:
 * - Annual composites use median values to reduce noise and cloud contamination
 * - Seasonal composites available for finer temporal detail
 * 
 * CHANGE DETECTION:
 * - Simple temporal comparison: woody (t1) → non-woody (t2) = clearing
 * - Does not distinguish regrowth from clearing (use SLATS for this)
 * 
 * DATA QUALITY:
 * - DEA products are pre-processed and atmospherically corrected
 * - Cloud masking is applied but some contamination may remain
 * - SLATS provides ground-truthed clearing events for validation
 */

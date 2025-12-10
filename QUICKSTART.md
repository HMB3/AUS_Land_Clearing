# Quick Start Guide

Get started with the Australian Land Clearing Visualization project in 5 steps.

## Prerequisites

Before you begin, ensure you have:

1. ✅ **Google Earth Engine account** - Sign up at [https://earthengine.google.com](https://earthengine.google.com)
2. ✅ **Basic JavaScript knowledge** - For customizing GEE scripts
3. ✅ **Google Drive** - For receiving exports (included with GEE account)

## Step 1: Set Up Your Data (10 minutes)

### Option A: Use Placeholder Configuration (Fastest)

The scripts are ready to run with placeholder asset paths. You'll need to update them with real data later.

**Skip to Step 2** to explore the code structure first.

### Option B: Upload Your Own Data

1. **Obtain DEA Land Cover data:**
   - Download from [DEA Knowledge Hub](https://knowledge.dea.ga.gov.au/data/product/dea-land-cover-landsat/)
   - Or access via GEE Community Catalog (if available)

2. **Upload to Google Earth Engine:**
   ```bash
   # Using Earth Engine command line tool
   earthengine create collection projects/YOUR_PROJECT/dea_land_cover
   
   # Upload individual years
   earthengine upload image --asset_id=projects/YOUR_PROJECT/dea_land_cover/1988 \
     gs://YOUR_BUCKET/dea_lc_1988.tif
   ```

3. **Update configuration:**
   
   Edit `gee_scripts/core/config.js`:
   ```javascript
   exports.DEA_LAND_COVER = {
     ASSET_ID: 'projects/YOUR_PROJECT/dea_land_cover',  // Update this
     BAND: 'level3',
     START_YEAR: 1988,
     END_YEAR: 2023
   };
   ```

**Pro tip:** Start with a small subset (e.g., one region, 5 years) to test before uploading everything.

## Step 2: Choose Your Analysis (2 minutes)

Select the appropriate script for your needs:

### Quick Continental Overview
**Use:** `gee_scripts/continental_overview.js`
- Best for: First-time users, quick demonstration
- Output: Continental-scale animation + key frames
- Processing time: ~30 minutes

### Detailed Regional Study
**Use:** `gee_scripts/case_studies/moree_plains_nsw.js` or `brigalow_belt_qld.js`
- Best for: Deep-dive into specific regions
- Output: High-resolution frames, time series, change maps
- Processing time: ~1-2 hours

### Custom Analysis
**Use:** `gee_scripts/main_workflow.js`
- Best for: Custom regions and parameters
- Output: Fully configurable
- Processing time: Varies

## Step 3: Run Your First Analysis (5 minutes)

### In Google Earth Engine Code Editor:

1. **Open GEE Code Editor:** [https://code.earthengine.google.com](https://code.earthengine.google.com)

2. **Create a new repository:**
   - Click "Scripts" tab
   - Click "NEW" → "Repository"
   - Name it: `AUS_Land_Clearing`

3. **Upload the scripts:**
   - Create folders: `core`, `case_studies`
   - Upload scripts from this GitHub repository to corresponding folders

4. **Run Continental Overview:**
   - Open `continental_overview.js`
   - Click "Run" button
   - Wait for map to load (~30 seconds)

5. **Review the output:**
   - Map displays: First year, last year, total clearing
   - Console shows: Summary statistics and chart
   - Tasks tab: Export tasks ready to run

## Step 4: Export Your Results (5 minutes)

1. **Open the Tasks tab** (right panel in GEE Code Editor)

2. **Start exports** (click "RUN" next to each task):
   - `continental_woody_animation` - MP4 video
   - `continental_woody_XXXX` - Key year frames
   - `continental_timeseries` - CSV data
   - `continental_clearing_map` - Change map

3. **Configure export** (if prompted):
   - Drive folder: `AUS_Land_Clearing` (default)
   - All other settings: Use defaults
   - Click "Run"

4. **Monitor progress:**
   - Tasks show as "Running" (blue)
   - Check Google Drive for completed exports
   - Typical time: 5-30 minutes per export

## Step 5: View Your Results (5 minutes)

### In Google Drive:

1. Open `AUS_Land_Clearing/continental/` folder

2. **Watch the animation:**
   - File: `eastern_australia_woody_1988_2023.mp4`
   - Shows: 36 years of change in ~18 seconds
   - Use: Video player, presentation software

3. **View key frames:**
   - Folder: `frames/`
   - Files: `eastern_australia_woody_YYYY.tif`
   - Use: QGIS, ArcGIS, or any GIS software

4. **Analyze time series:**
   - File: `eastern_australia_woody_area_1988_2023.csv`
   - Columns: `year`, `woody_area_m2`, `woody_area_ha`
   - Use: Excel, R, Python for charting

### In QGIS (Optional - for map visualization):

1. **Install QGIS:** [https://qgis.org](https://qgis.org) (free)

2. **Load GeoTIFF frames:**
   - Drag & drop `.tif` files into QGIS
   - Apply styling: Dark green for woody (value=1), transparent for non-woody (value=0)

3. **Create map layout:**
   - Add legend, scale bar, north arrow
   - Export as PNG or PDF

## What's Next?

### Customize Your Analysis

**Change the region:**
```javascript
// In continental_overview.js or main_workflow.js
var myRegion = ee.Geometry.Rectangle([west, south, east, north]);

var WORKFLOW_CONFIG = {
  region: myRegion,
  regionName: 'my_study_area',
  // ... rest of config
};
```

**Adjust time period:**
```javascript
var WORKFLOW_CONFIG = {
  startYear: 2000,  // Change from 1988
  endYear: 2020,    // Change from 2023
  // ... rest of config
};
```

**Change resolution:**
```javascript
var WORKFLOW_CONFIG = {
  scale: 25,  // Higher detail (slower)
  // scale: 250,  // Lower detail (faster)
  // ... rest of config
};
```

### Explore Case Studies

**Moree Plains (NSW):**
```javascript
// Run: gee_scripts/case_studies/moree_plains_nsw.js
// Focus: Agricultural clearing, irrigation expansion
```

**Brigalow Belt (QLD):**
```javascript
// Run: gee_scripts/case_studies/brigalow_belt_qld.js
// Focus: Policy impacts, vegetation regulations
```

### Learn More

- **Full documentation:** [README.md](README.md)
- **Configuration options:** [docs/CONFIGURATION.md](docs/CONFIGURATION.md)
- **Data sources:** [docs/DATA_SOURCES.md](docs/DATA_SOURCES.md)
- **Advanced examples:** [docs/USAGE_EXAMPLES.md](docs/USAGE_EXAMPLES.md)

## Troubleshooting

### Common Issues

| Problem | Solution |
|---------|----------|
| "Asset not found" | Update `ASSET_ID` in `config.js` with your data path |
| "Collection is empty" | Check date range and asset availability |
| "Computation timeout" | Reduce region size or increase scale (coarser resolution) |
| "Memory limit exceeded" | Split large regions into smaller tiles |
| Export fails | Check pixel count: `region.area() / (scale * scale)` < 1e13 |

### Getting Help

- **GEE Community:** [Google Earth Engine Developers Group](https://groups.google.com/g/google-earth-engine-developers)
- **GEE Documentation:** [https://developers.google.com/earth-engine](https://developers.google.com/earth-engine)
- **DEA Support:** [https://www.dea.ga.gov.au/about/contact-us](https://www.dea.ga.gov.au/about/contact-us)

## Checklist

Track your progress:

- [ ] GEE account created
- [ ] Data uploaded or placeholder paths configured
- [ ] Scripts uploaded to GEE Code Editor
- [ ] First script run successfully
- [ ] Map visualization displayed
- [ ] Exports configured in Tasks tab
- [ ] First export completed
- [ ] Results viewed in Google Drive
- [ ] (Optional) Results loaded in QGIS or other GIS

## Tips for Success

1. **Start small:** Test with a small region and short time period first
2. **Check frequently:** Monitor Tasks tab for export progress/errors
3. **Save intermediate results:** Export baseline years before running full series
4. **Document changes:** Keep notes on configuration changes
5. **Backup exports:** Download results from Google Drive to local storage

## Next Steps

Once you've completed this quick start:

1. ✅ Run regional case studies
2. ✅ Customize for your own study area
3. ✅ Integrate SLATS data for validation
4. ✅ Create publication-quality visualizations
5. ✅ Share your results!

---

**Estimated time to first results:** 30-60 minutes

**Ready to dive deeper?** See the full [README](README.md) and [documentation](docs/).

---

*Quick Start Guide maintained as part of the Australian Land Clearing Visualization project.*

# Examples Directory

This directory contains example outputs and templates for the Australian Land Clearing Visualization project.

## Contents

### Visualization Templates

Templates for creating final visualizations from exported GEE data using external tools (Python, R, After Effects).

### Example Outputs

Sample outputs demonstrating the workflow results (when available):

- **Thumbnails**: Preview images of key frames
- **Animations**: Short clips showing land cover change
- **Maps**: Static maps highlighting clearing events
- **Charts**: Time series plots of vegetation area

## Generating Examples

Run the GEE workflows in `gee_scripts/` to generate your own outputs:

1. **Continental Overview**: Run `main_workflow.js` with continental domain
2. **Regional Study**: Run case study scripts in `case_studies/`
3. **Custom Analysis**: Modify workflows for your region of interest

## Output Organization

Recommended structure for your outputs:

```
examples/
├── continental/
│   ├── frames/           # Annual GeoTIFF frames
│   ├── animations/       # MP4/GIF animations
│   └── thumbnails/       # Preview images
├── moree_plains/
│   ├── frames/
│   ├── animations/
│   ├── timeseries/       # CSV data
│   └── maps/            # Static maps
├── brigalow_belt/
│   └── ...
└── templates/
    ├── python/          # Python visualization scripts
    ├── r/               # R visualization scripts
    └── aftereffects/    # After Effects project templates
```

## Post-Processing Workflows

### Python Example

```python
import rasterio
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Load annual frames
frames = []
for year in range(1988, 2024):
    with rasterio.open(f'aus_lc_continental_woody_{year}.tif') as src:
        frames.append(src.read(1))

# Create animation
fig, ax = plt.subplots(figsize=(12, 8))
im = ax.imshow(frames[0], cmap='YlGn', vmin=0, vmax=1)
ax.set_title('1988')

def update(frame_num):
    im.set_data(frames[frame_num])
    ax.set_title(f'{1988 + frame_num}')
    return [im]

anim = FuncAnimation(fig, update, frames=len(frames), interval=500)
anim.save('land_clearing_animation.mp4', dpi=150)
```

### R Example

```r
library(raster)
library(animation)

# Load annual frames
years <- 1988:2023
frames <- lapply(years, function(year) {
  raster(paste0('aus_lc_continental_woody_', year, '.tif'))
})

# Create animation
saveGIF({
  for (i in seq_along(frames)) {
    plot(frames[[i]], 
         main = paste('Woody Vegetation', years[i]),
         col = terrain.colors(2))
  }
}, movie.name = 'land_clearing.gif', interval = 0.5)
```

## Visualization Tips

### Color Schemes

- **Woody vegetation**: Dark green (#1a5928) for forests
- **Non-woody**: Tan/yellow (#e8b520) for grasslands
- **Cleared areas**: Red (#ff0000) for emphasis
- **Water**: Blue (#0060ff)

### Animation Settings

- **Frame rate**: 2 fps (0.5 seconds per year) for narrative pace
- **Resolution**: 1920px for HD video, 3840px for 4K
- **Duration**: 36 years (1988-2023) = 18 seconds at 2 fps

### Static Maps

- Include legend, scale bar, north arrow
- Add inset map showing location in Australia
- Annotate key clearing events with labels
- Use before/after panels for impact visualization

## External Tools

### Recommended Software

- **QGIS**: Free GIS software for map making
- **Python**: Rasterio, matplotlib, cartopy for programmatic visualization
- **R**: raster, ggplot2, tmap for statistical graphics
- **Adobe After Effects**: Professional motion graphics
- **GIMP/Photoshop**: Image editing and compositing

### Workflow Integration

1. **GEE → GeoTIFF**: Export frames from Google Earth Engine
2. **GeoTIFF → PNG**: Convert with GDAL or rasterio
3. **PNG → Animation**: Combine with FFmpeg, ImageMagick, or video editor
4. **Polish**: Add titles, annotations, transitions in video editor

## Resources

- [GDAL/OGR](https://gdal.org/) - Geospatial data processing
- [FFmpeg](https://ffmpeg.org/) - Video processing
- [ColorBrewer](https://colorbrewer2.org/) - Color scheme selection
- [Cartopy](https://scitools.org.uk/cartopy/) - Python mapping

---

*This directory is maintained as part of the Australian Land Clearing Visualization project.*

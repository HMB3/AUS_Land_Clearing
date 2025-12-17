#!/usr/bin/env python3
"""
Run DEA Annual Landcover Processing

Process Digital Earth Australia (DEA) annual landcover data for NSW and/or QLD,
producing yearly GeoTIFF outputs and animations.

This script:
1. Loads configuration from config.yaml
2. Loads area of interest (NSW, QLD, or both)
3. Fetches DEA annual landcover data
4. Reclassifies to woody/non-woody scheme
5. Exports yearly GeoTIFFs
6. Creates animated GIF

Usage:
    # Process both NSW and QLD for full time period
    python scripts/run_dea_processing.py
    
    # Process only NSW
    python scripts/run_dea_processing.py --state nsw
    
    # Process specific time range
    python scripts/run_dea_processing.py --start-year 2000 --end-year 2020
    
    # Add 5km buffer around state boundary
    python scripts/run_dea_processing.py --buffer 5000
    
    # Use custom config file
    python scripts/run_dea_processing.py --config my_config.yaml

Requirements:
    See requirements.txt - key dependencies:
    - geopandas, rasterio, xarray, numpy
    - pystac-client or datacube (for real data access)
    - imageio (for animations)
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import List

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

try:
    from aus_land_clearing.dea_processor import (
        load_aoi,
        load_dea_config,
        fetch_dea_landcover,
        reclassify_dea_to_woody_nonwoody,
        export_yearly_geotiff,
        create_animation
    )
except ImportError as e:
    print(f"Error importing dea_processor: {e}")
    print("Make sure you've installed the package: pip install -e .")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def process_state(
    state: str,
    config: dict,
    start_year: int,
    end_year: int,
    buffer_distance: float
) -> None:
    """
    Process DEA landcover for a single state.
    
    Parameters
    ----------
    state : str
        State name ('nsw' or 'qld')
    config : dict
        DEA configuration dictionary
    start_year : int
        Start year for processing
    end_year : int
        End year for processing
    buffer_distance : float
        Buffer distance in meters
    """
    logger.info(f"\n{'='*60}")
    logger.info(f"Processing {state.upper()}")
    logger.info(f"{'='*60}")
    
    # Get AOI path
    aoi_path = config['aoi_paths'].get(state.lower())
    if not aoi_path:
        logger.error(f"AOI path for {state} not found in config")
        return
    
    # Check if AOI file exists
    if not Path(aoi_path).exists():
        logger.error(f"AOI file not found: {aoi_path}")
        logger.info("Run: python scripts/fetch_australian_state_geojson.py")
        return
    
    # Load AOI
    try:
        aoi = load_aoi(aoi_path, buffer_distance=buffer_distance)
    except Exception as e:
        logger.error(f"Failed to load AOI: {e}")
        return
    
    # Fetch DEA data
    try:
        logger.info(f"Fetching DEA data for {start_year}-{end_year}...")
        data = fetch_dea_landcover(
            aoi=aoi,
            start_year=start_year,
            end_year=end_year,
            product_id=config.get('product_id', 'ga_ls_landcover_class_cyear_2'),
            resolution=config.get('resolution', 25),
            crs=config.get('crs', 'EPSG:3577'),
            stac_url=config.get('stac', {}).get('catalog_url')
        )
    except Exception as e:
        logger.error(f"Failed to fetch DEA data: {e}")
        logger.info("Note: This template uses mock data for demonstration")
        logger.info("For real data, install: pip install pystac-client odc-stac")
        return
    
    # Reclassify to woody/non-woody
    try:
        logger.info("Reclassifying to woody/non-woody...")
        classified = reclassify_dea_to_woody_nonwoody(
            data,
            classes_map=config.get('classes_map')
        )
    except Exception as e:
        logger.error(f"Failed to reclassify: {e}")
        return
    
    # Create output directory
    output_dir = Path(config.get('output_dir', 'data/outputs/dea_landcover')) / state.lower()
    output_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"Output directory: {output_dir}")
    
    # Export yearly GeoTIFFs
    logger.info("Exporting yearly GeoTIFFs...")
    yearly_files = []
    
    for year in range(start_year, end_year + 1):
        try:
            output_path = output_dir / f'landcover_{year}.tif'
            export_yearly_geotiff(
                classified,
                year=year,
                output_path=output_path,
                nodata_value=config.get('processing', {}).get('nodata_value', 255)
            )
            yearly_files.append(output_path)
        except Exception as e:
            logger.warning(f"Failed to export {year}: {e}")
    
    logger.info(f"Exported {len(yearly_files)} GeoTIFFs")
    
    # Create animation
    if yearly_files:
        try:
            animation_path = output_dir / 'animation.gif'
            logger.info("Creating animation...")
            create_animation(
                yearly_files,
                animation_path,
                fps=config.get('animation', {}).get('fps', 2),
                loop=config.get('animation', {}).get('loop', 0)
            )
            logger.info(f"✓ Animation complete: {animation_path}")
        except Exception as e:
            logger.warning(f"Failed to create animation: {e}")
            logger.info("Install imageio for animations: pip install imageio")
    
    logger.info(f"\n✓ {state.upper()} processing complete")
    logger.info(f"Output: {output_dir}")


def main():
    """Main processing function."""
    parser = argparse.ArgumentParser(
        description='Process DEA annual landcover for NSW and QLD',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process both states for full time period
  python scripts/run_dea_processing.py
  
  # Process only NSW from 2000-2020
  python scripts/run_dea_processing.py --state nsw --start-year 2000 --end-year 2020
  
  # Add 5km buffer to reduce edge artifacts
  python scripts/run_dea_processing.py --buffer 5000
        """
    )
    
    parser.add_argument(
        '--state',
        type=str,
        choices=['nsw', 'qld', 'both'],
        default='both',
        help='State to process (default: both)'
    )
    parser.add_argument(
        '--start-year',
        type=int,
        help='Start year (default: from config)'
    )
    parser.add_argument(
        '--end-year',
        type=int,
        help='End year (default: from config)'
    )
    parser.add_argument(
        '--buffer',
        type=float,
        default=0.0,
        help='Buffer distance in meters (default: 0)'
    )
    parser.add_argument(
        '--config',
        type=str,
        default='config.yaml',
        help='Path to config file (default: config.yaml)'
    )
    
    args = parser.parse_args()
    
    # Load configuration
    try:
        logger.info(f"Loading configuration from: {args.config}")
        config = load_dea_config(args.config)
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        sys.exit(1)
    
    # Get time range
    start_year = args.start_year or config.get('start_year', 1988)
    end_year = args.end_year or config.get('end_year', 2024)
    
    logger.info("\n" + "="*60)
    logger.info("DEA Annual Landcover Processing")
    logger.info("="*60)
    logger.info(f"Time period: {start_year}-{end_year}")
    logger.info(f"Buffer: {args.buffer}m")
    logger.info(f"Product: {config.get('product_id', 'ga_ls_landcover_class_cyear_2')}")
    
    # Process states
    states_to_process = []
    if args.state == 'both':
        states_to_process = ['nsw', 'qld']
    else:
        states_to_process = [args.state]
    
    for state in states_to_process:
        try:
            process_state(
                state=state,
                config=config,
                start_year=start_year,
                end_year=end_year,
                buffer_distance=args.buffer
            )
        except Exception as e:
            logger.error(f"Error processing {state}: {e}", exc_info=True)
    
    logger.info("\n" + "="*60)
    logger.info("Processing complete!")
    logger.info("="*60)
    logger.info("\nNext steps:")
    logger.info("  1. Review outputs in data/outputs/dea_landcover/")
    logger.info("  2. Open notebooks/0-demo-dea-processing.ipynb for visualization")
    logger.info("  3. Customize class mapping in config.yaml if needed")


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
Fetch Australian State Boundaries

Downloads official Australian state boundaries from Natural Earth and extracts
NSW and Queensland to separate GeoJSON files for use in DEA processing workflows.

This script:
1. Downloads Natural Earth admin-1 (states/provinces) dataset
2. Filters to Australian states
3. Extracts NSW and QLD to separate files
4. Saves a combined Australian states reference file

Data Source: Natural Earth (https://www.naturalearthdata.com/)
Alternative: Australian Bureau of Statistics (https://www.abs.gov.au/geography)

Usage:
    python scripts/fetch_australian_state_geojson.py
    
    # With custom output directory
    python scripts/fetch_australian_state_geojson.py --output-dir data/boundaries

Requirements:
    geopandas, requests
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import Optional

try:
    import geopandas as gpd
    import requests
except ImportError as e:
    print(f"Error: Missing required dependency: {e}")
    print("Install with: pip install geopandas requests")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Natural Earth data source
NATURAL_EARTH_URL = (
    "https://www.naturalearthdata.com/http//www.naturalearthdata.com/"
    "download/10m/cultural/ne_10m_admin_1_states_provinces.zip"
)

# Backup URL (GitHub mirror)
BACKUP_URL = (
    "https://github.com/nvkelso/natural-earth-vector/raw/master/"
    "geojson/ne_10m_admin_1_states_provinces.geojson"
)


def download_states_shapefile(output_dir: Path, use_backup: bool = False) -> gpd.GeoDataFrame:
    """
    Download and load Natural Earth states/provinces shapefile.
    
    Parameters
    ----------
    output_dir : Path
        Directory to cache downloaded data
    use_backup : bool, optional
        If True, use backup GitHub URL instead of main source
        
    Returns
    -------
    gpd.GeoDataFrame
        Global states/provinces dataset
        
    Raises
    ------
    Exception
        If download or loading fails
    """
    url = BACKUP_URL if use_backup else NATURAL_EARTH_URL
    logger.info(f"Downloading Natural Earth states from: {url}")
    
    try:
        # GeoDataFrame can read directly from URL
        if use_backup or url.endswith('.geojson'):
            gdf = gpd.read_file(url)
        else:
            # For .zip files, geopandas can read directly
            gdf = gpd.read_file(url)
        
        logger.info(f"Successfully loaded {len(gdf)} state/province boundaries")
        return gdf
        
    except Exception as e:
        if not use_backup:
            logger.warning(f"Primary download failed: {e}")
            logger.info("Attempting backup URL...")
            return download_states_shapefile(output_dir, use_backup=True)
        else:
            raise Exception(f"Failed to download state boundaries: {e}")


def filter_australian_states(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """
    Filter to Australian states only.
    
    Parameters
    ----------
    gdf : gpd.GeoDataFrame
        Global states dataset
        
    Returns
    -------
    gpd.GeoDataFrame
        Australian states only
    """
    # Natural Earth uses 'admin' field for country name
    # and 'name' or 'name_en' for state/province name
    aus_states = gdf[gdf['admin'] == 'Australia'].copy()
    
    logger.info(f"Filtered to {len(aus_states)} Australian states/territories")
    logger.info(f"States found: {sorted(aus_states['name'].unique())}")
    
    return aus_states


def extract_state(
    aus_states: gpd.GeoDataFrame,
    state_name: str,
    output_path: Path
) -> Optional[gpd.GeoDataFrame]:
    """
    Extract a specific state and save to GeoJSON.
    
    Parameters
    ----------
    aus_states : gpd.GeoDataFrame
        Australian states dataset
    state_name : str
        Name of state to extract (e.g., 'New South Wales', 'Queensland')
    output_path : Path
        Output GeoJSON file path
        
    Returns
    -------
    gpd.GeoDataFrame or None
        Extracted state, or None if not found
    """
    # Try different name variations
    name_variations = [
        state_name,
        state_name.upper(),
        state_name.lower(),
        state_name.replace(' ', ''),
    ]
    
    state_gdf = None
    for name_var in name_variations:
        matching = aus_states[
            aus_states['name'].str.contains(name_var, case=False, na=False)
        ]
        if len(matching) > 0:
            state_gdf = matching
            break
    
    if state_gdf is None or len(state_gdf) == 0:
        logger.error(f"Could not find state: {state_name}")
        logger.info(f"Available states: {sorted(aus_states['name'].unique())}")
        return None
    
    if len(state_gdf) > 1:
        logger.warning(f"Multiple matches found for {state_name}, using first match")
        state_gdf = state_gdf.iloc[[0]]
    
    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Save to GeoJSON
    state_gdf.to_file(output_path, driver='GeoJSON')
    logger.info(f"Saved {state_name} to: {output_path}")
    
    return state_gdf


def main():
    """Main function to download and process state boundaries."""
    parser = argparse.ArgumentParser(
        description='Download Australian state boundaries for DEA processing'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='data',
        help='Output directory for GeoJSON files (default: data)'
    )
    parser.add_argument(
        '--use-backup',
        action='store_true',
        help='Use backup download URL'
    )
    
    args = parser.parse_args()
    output_dir = Path(args.output_dir)
    
    logger.info("=== Australian State Boundary Fetch ===")
    logger.info(f"Output directory: {output_dir.absolute()}")
    
    try:
        # Download global states dataset
        states_gdf = download_states_shapefile(output_dir, use_backup=args.use_backup)
        
        # Filter to Australian states
        aus_states = filter_australian_states(states_gdf)
        
        if len(aus_states) == 0:
            logger.error("No Australian states found in dataset")
            sys.exit(1)
        
        # Save all Australian states as reference
        all_states_path = output_dir / 'australian_states.geojson'
        aus_states.to_file(all_states_path, driver='GeoJSON')
        logger.info(f"Saved all Australian states to: {all_states_path}")
        
        # Extract NSW
        nsw_path = output_dir / 'nsw.geojson'
        nsw = extract_state(aus_states, 'New South Wales', nsw_path)
        if nsw is None:
            logger.error("Failed to extract NSW")
            sys.exit(1)
        
        # Extract Queensland
        qld_path = output_dir / 'qld.geojson'
        qld = extract_state(aus_states, 'Queensland', qld_path)
        if qld is None:
            logger.error("Failed to extract Queensland")
            sys.exit(1)
        
        logger.info("\n=== Summary ===")
        logger.info(f"✓ All Australian states: {all_states_path}")
        logger.info(f"✓ New South Wales: {nsw_path}")
        logger.info(f"✓ Queensland: {qld_path}")
        logger.info("\nState boundaries ready for DEA processing!")
        
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

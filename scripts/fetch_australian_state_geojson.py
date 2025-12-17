#!/usr/bin/env python3
"""
Fetch Australian state boundaries from GADM and save as GeoJSON.

This script downloads administrative boundary data for Australian states
(NSW and QLD) and saves them as individual GeoJSON files for use in
DEA land cover processing.

Usage:
    python scripts/fetch_australian_state_geojson.py

Output:
    - data/australian_states.geojson (all states)
    - data/nsw.geojson (New South Wales)
    - data/qld.geojson (Queensland)
"""

import geopandas as gpd
import requests
from pathlib import Path
import sys


def fetch_gadm_states(country_code="AUS", admin_level=1):
    """
    Fetch Australian state boundaries from GADM database.
    
    Parameters
    ----------
    country_code : str
        ISO 3166-1 alpha-3 country code (default: "AUS")
    admin_level : int
        Administrative level (1 = states/territories)
        
    Returns
    -------
    geopandas.GeoDataFrame
        State boundaries
    """
    print(f"Fetching GADM data for {country_code} (admin level {admin_level})...")
    
    # GADM version 4.1 URL
    url = f"https://geodata.ucdavis.edu/gadm/gadm4.1/json/gadm41_{country_code}_{admin_level}.json"
    
    try:
        gdf = gpd.read_file(url)
        print(f"Successfully loaded {len(gdf)} administrative regions")
        return gdf
    except Exception as e:
        print(f"Error fetching GADM data: {e}")
        print("Attempting alternative method using shapefile...")
        
        # Alternative: try shapefile format
        url_shp = f"https://geodata.ucdavis.edu/gadm/gadm4.1/shp/gadm41_{country_code}_shp.zip"
        try:
            gdf = gpd.read_file(url_shp, layer=f"gadm41_{country_code}_{admin_level}")
            print(f"Successfully loaded {len(gdf)} administrative regions from shapefile")
            return gdf
        except Exception as e2:
            print(f"Error with alternative method: {e2}")
            raise


def save_state_geojson(gdf, state_name, output_path):
    """
    Extract and save a specific state as GeoJSON.
    
    Parameters
    ----------
    gdf : geopandas.GeoDataFrame
        GeoDataFrame with all states
    state_name : str
        State name to filter (e.g., "New South Wales", "Queensland")
    output_path : Path or str
        Output path for GeoJSON file
    """
    # Filter for the specific state
    state_gdf = gdf[gdf['NAME_1'] == state_name].copy()
    
    if len(state_gdf) == 0:
        print(f"Warning: State '{state_name}' not found in data")
        print(f"Available states: {gdf['NAME_1'].unique().tolist()}")
        return False
    
    # Save as GeoJSON
    state_gdf.to_file(output_path, driver='GeoJSON')
    print(f"Saved {state_name} boundary to {output_path}")
    return True


def main():
    """Main execution function."""
    # Set up paths
    repo_root = Path(__file__).parent.parent
    data_dir = repo_root / "data"
    data_dir.mkdir(exist_ok=True)
    
    try:
        # Fetch all Australian states
        gdf = fetch_gadm_states(country_code="AUS", admin_level=1)
        
        # Save all states
        all_states_path = data_dir / "australian_states.geojson"
        gdf.to_file(all_states_path, driver='GeoJSON')
        print(f"Saved all Australian states to {all_states_path}")
        
        # Save individual states
        states_to_save = {
            "New South Wales": data_dir / "nsw.geojson",
            "Queensland": data_dir / "qld.geojson"
        }
        
        success_count = 0
        for state_name, output_path in states_to_save.items():
            if save_state_geojson(gdf, state_name, output_path):
                success_count += 1
        
        print(f"\n✓ Successfully saved {success_count}/{len(states_to_save)} state boundaries")
        
        if success_count < len(states_to_save):
            print("\nNote: Some states could not be saved. Check the warnings above.")
            sys.exit(1)
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

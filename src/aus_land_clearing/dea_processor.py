"""
DEA Annual Land Cover Processor

This module provides functions to process Digital Earth Australia (DEA)
annual land cover data, reclassifying it into woody/non-woody categories
and exporting results as GeoTIFFs and animations.

The data fetching backend (datacube or STAC) is intentionally left as a
template to avoid assumptions about the user's environment.
"""

import numpy as np
import yaml
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
import geopandas as gpd
import rasterio
from rasterio.transform import from_bounds
from rasterio.crs import CRS
import imageio
import warnings


def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load configuration from YAML file.
    
    Parameters
    ----------
    config_path : str, optional
        Path to configuration file. If None, searches for config.yaml
        in project directory.
        
    Returns
    -------
    dict
        Configuration dictionary
    """
    if config_path is None:
        # Find project root and load default config
        current = Path(__file__).resolve()
        for parent in [current] + list(current.parents):
            config_file = parent / "config.yaml"
            if config_file.exists():
                config_path = str(config_file)
                break
        
        if config_path is None:
            raise FileNotFoundError(
                "Could not find config.yaml in project directory"
            )
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    return config


def load_aoi(aoi_path: str) -> gpd.GeoDataFrame:
    """
    Load area of interest (AOI) from GeoJSON file.
    
    Parameters
    ----------
    aoi_path : str
        Path to GeoJSON file
        
    Returns
    -------
    geopandas.GeoDataFrame
        Area of interest geometry
    """
    if not Path(aoi_path).exists():
        raise FileNotFoundError(
            f"AOI file not found: {aoi_path}\n"
            "Run scripts/fetch_australian_state_geojson.py to download boundaries."
        )
    
    return gpd.read_file(aoi_path)


def reclassify_dea_classes(
    data: np.ndarray,
    classes_map: Dict[str, List[int]]
) -> np.ndarray:
    """
    Reclassify DEA land cover classes into woody (1) / non-woody (0).
    
    Parameters
    ----------
    data : numpy.ndarray
        Input DEA land cover data with original class values
    classes_map : dict
        Dictionary with 'woody' and 'non_woody' keys containing lists
        of DEA class IDs
        
    Returns
    -------
    numpy.ndarray
        Binary raster: 1 = woody, 0 = non-woody, NaN = nodata
        
    Examples
    --------
    >>> data = np.array([[111, 124], [214, 215]])
    >>> classes_map = {
    ...     'woody': [111, 124],
    ...     'non_woody': [214, 215]
    ... }
    >>> result = reclassify_dea_classes(data, classes_map)
    >>> result
    array([[1, 1],
           [0, 0]])
    """
    # Create output array filled with NaN
    output = np.full_like(data, np.nan, dtype=np.float32)
    
    # Reclassify woody classes to 1
    woody_classes = classes_map.get('woody', [])
    for class_id in woody_classes:
        output[data == class_id] = 1
    
    # Reclassify non-woody classes to 0
    non_woody_classes = classes_map.get('non_woody', [])
    for class_id in non_woody_classes:
        output[data == class_id] = 0
    
    return output


def fetch_dea_raster_for_year(
    year: int,
    aoi: gpd.GeoDataFrame,
    config: Dict[str, Any]
) -> Optional[Tuple[np.ndarray, Dict[str, Any]]]:
    """
    Fetch DEA land cover raster for a specific year.
    
    **TEMPLATE FUNCTION - TO BE IMPLEMENTED IN SWEEP-2**
    
    This is a template function that should be implemented to fetch DEA
    annual land cover data using either:
    
    1. Open Data Cube (ODC) - if you have a local datacube instance configured
    2. STAC API - using odc-stac to query DEA's STAC catalog
    3. Direct download - from DEA's data repository
    
    Implementation notes:
    - Use the product_id from config['dea_profile']['product_id']
    - Filter by year and AOI bounds
    - Return data in the CRS specified in config['dea_profile']['crs']
    - Return data at resolution in config['dea_profile']['resolution']
    
    Example implementation outline:
    
    Using datacube:
        import datacube
        dc = datacube.Datacube()
        data = dc.load(
            product=config['dea_profile']['product_id'],
            time=(f'{year}-01-01', f'{year}-12-31'),
            geopolygon=aoi.geometry.unary_union,
            output_crs=config['dea_profile']['crs'],
            resolution=(-config['dea_profile']['resolution'], 
                       config['dea_profile']['resolution'])
        )
        
    Using STAC:
        from odc.stac import load
        from pystac_client import Client
        
        catalog = Client.open('https://explorer.dea.ga.gov.au/stac/')
        items = catalog.search(
            collections=[config['dea_profile']['product_id']],
            datetime=f'{year}-01-01/{year}-12-31',
            bbox=aoi.total_bounds
        ).items()
        
        data = load(items, 
                   crs=config['dea_profile']['crs'],
                   resolution=config['dea_profile']['resolution'])
    
    Parameters
    ----------
    year : int
        Year to fetch data for
    aoi : geopandas.GeoDataFrame
        Area of interest
    config : dict
        Configuration dictionary
        
    Returns
    -------
    tuple or None
        (data_array, metadata_dict) where:
        - data_array: numpy array of land cover classes
        - metadata_dict: dictionary with 'crs', 'transform', 'bounds'
        
        Returns None if no data available for the year.
        
    Raises
    ------
    NotImplementedError
        This template function must be implemented with actual data fetching
    """
    raise NotImplementedError(
        "fetch_dea_raster_for_year is a template function.\n\n"
        "Please implement data fetching using one of:\n"
        "  1. Open Data Cube (datacube library)\n"
        "  2. STAC API (odc-stac + pystac_client)\n"
        "  3. Direct download from DEA repository\n\n"
        "See function docstring for implementation examples.\n"
        "This will be implemented in sweep-2."
    )


def export_geotiff(
    data: np.ndarray,
    output_path: str,
    metadata: Dict[str, Any],
    nodata: float = np.nan
) -> None:
    """
    Export numpy array as GeoTIFF.
    
    Parameters
    ----------
    data : numpy.ndarray
        Data to export
    output_path : str
        Output file path
    metadata : dict
        Metadata dictionary with 'crs', 'transform', 'bounds' keys
    nodata : float
        Nodata value (default: NaN)
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Prepare metadata for rasterio
    height, width = data.shape
    
    with rasterio.open(
        output_path,
        'w',
        driver='GTiff',
        height=height,
        width=width,
        count=1,
        dtype=data.dtype,
        crs=metadata['crs'],
        transform=metadata['transform'],
        nodata=nodata,
        compress='lzw'
    ) as dst:
        dst.write(data, 1)
    
    print(f"Exported: {output_path}")


def create_animation(
    image_dir: str,
    output_path: str,
    pattern: str = "*.tif",
    fps: int = 2,
    duration: Optional[float] = None
) -> None:
    """
    Create animated GIF from a series of GeoTIFF files.
    
    Parameters
    ----------
    image_dir : str
        Directory containing input images
    output_path : str
        Output GIF file path
    pattern : str
        Glob pattern for finding input files (default: "*.tif")
    fps : int
        Frames per second (default: 2)
    duration : float, optional
        Duration per frame in seconds. If provided, overrides fps.
    """
    image_dir = Path(image_dir)
    image_files = sorted(image_dir.glob(pattern))
    
    if len(image_files) == 0:
        raise ValueError(f"No images found matching pattern '{pattern}' in {image_dir}")
    
    print(f"Creating animation from {len(image_files)} images...")
    
    images = []
    for img_path in image_files:
        with rasterio.open(img_path) as src:
            # Read data and normalize to 0-255 for GIF
            data = src.read(1)
            
            # Handle NaN values
            data_min = np.nanmin(data)
            data_max = np.nanmax(data)
            
            if np.isnan(data_min) or np.isnan(data_max):
                # All NaN
                normalized = np.zeros_like(data, dtype=np.uint8)
            else:
                # Normalize to 0-255
                normalized = np.where(
                    np.isnan(data),
                    0,
                    ((data - data_min) / (data_max - data_min) * 255).astype(np.uint8)
                )
            
            images.append(normalized)
    
    # Calculate duration per frame
    if duration is None:
        duration = 1.0 / fps
    
    # Save as GIF
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    imageio.mimsave(
        output_path,
        images,
        duration=duration,
        loop=0
    )
    
    print(f"Animation saved to: {output_path}")


def process_dea_timeseries(
    state_code: str,
    config_path: Optional[str] = None,
    years: Optional[List[int]] = None
) -> Dict[str, Any]:
    """
    Process DEA land cover time series for a specific state.
    
    Parameters
    ----------
    state_code : str
        State code ('nsw' or 'qld')
    config_path : str, optional
        Path to config file
    years : list of int, optional
        Years to process. If None, uses start_year to end_year from config.
        
    Returns
    -------
    dict
        Processing summary with 'state', 'years_processed', 'output_dir'
        
    Raises
    ------
    NotImplementedError
        When fetch_dea_raster_for_year is not yet implemented
    """
    # Load configuration
    config = load_config(config_path)
    dea_config = config['dea_profile']
    
    # Get AOI path
    aoi_path = dea_config['aoi_paths'].get(state_code)
    if aoi_path is None:
        raise ValueError(f"No AOI path configured for state: {state_code}")
    
    # Load AOI
    aoi = load_aoi(aoi_path)
    
    # Determine years to process
    if years is None:
        years = list(range(dea_config['start_year'], dea_config['end_year'] + 1))
    
    # Set up output directory
    output_dir = Path(dea_config['output_dir']) / state_code
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Process each year
    years_processed = []
    for year in years:
        print(f"\nProcessing {state_code.upper()} - {year}")
        
        try:
            # Fetch data (template - will raise NotImplementedError)
            result = fetch_dea_raster_for_year(year, aoi, config)
            
            if result is None:
                print(f"  No data available for {year}")
                continue
            
            data, metadata = result
            
            # Reclassify to woody/non-woody
            woody_data = reclassify_dea_classes(data, dea_config['classes_map'])
            
            # Export GeoTIFF
            output_path = output_dir / f"{state_code}_woody_{year}.tif"
            export_geotiff(woody_data, str(output_path), metadata)
            
            years_processed.append(year)
            
        except NotImplementedError:
            # Re-raise NotImplementedError to inform user
            raise
        except Exception as e:
            print(f"  Error processing {year}: {e}")
            continue
    
    # Create animation if we have processed images
    if years_processed:
        gif_path = output_dir.parent / f"{state_code}_woody_timeseries.gif"
        try:
            create_animation(
                str(output_dir),
                str(gif_path),
                pattern=f"{state_code}_woody_*.tif",
                fps=config['outputs']['animations']['fps']
            )
        except Exception as e:
            print(f"Warning: Could not create animation: {e}")
    
    return {
        'state': state_code,
        'years_processed': years_processed,
        'output_dir': str(output_dir)
    }

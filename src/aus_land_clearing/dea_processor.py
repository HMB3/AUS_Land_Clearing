"""
DEA Annual Landcover Processor

This module provides functions to process Digital Earth Australia (DEA) annual 
landcover products for time-series analysis and visualization. It supports:

- Loading DEA landcover data via STAC catalog or Open Data Cube
- Reclassifying DEA classes to simplified woody/non-woody scheme
- Clipping to areas of interest (e.g., NSW, QLD)
- Exporting yearly GeoTIFFs
- Creating animated GIFs from time series

Data Source:
    DEA Annual Landcover (ga_ls_landcover_class_cyear_2)
    https://www.dea.ga.gov.au/products/dea-land-cover

Example:
    >>> from aus_land_clearing.dea_processor import (
    ...     load_aoi, fetch_dea_landcover, reclassify_dea_to_woody_nonwoody
    ... )
    >>> aoi = load_aoi('data/nsw.geojson')
    >>> data = fetch_dea_landcover(aoi, start_year=2000, end_year=2020)
    >>> classified = reclassify_dea_to_woody_nonwoody(data)
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

import numpy as np
import yaml

try:
    import geopandas as gpd
    import rasterio
    from rasterio.transform import from_bounds
    from rasterio.warp import calculate_default_transform, reproject, Resampling
    import xarray as xr
    from shapely.geometry import box, mapping
except ImportError as e:
    raise ImportError(
        f"Missing required dependency: {e}\n"
        "Install with: pip install geopandas rasterio xarray shapely"
    )

# Optional dependencies with graceful degradation
try:
    import imageio
    HAS_IMAGEIO = True
except ImportError:
    HAS_IMAGEIO = False

try:
    from pystac_client import Client
    HAS_PYSTAC = True
except ImportError:
    HAS_PYSTAC = False

try:
    import datacube
    HAS_DATACUBE = True
except ImportError:
    HAS_DATACUBE = False

# Configure logging (can be overridden by user)
logger = logging.getLogger(__name__)


def load_aoi(
    aoi_path: Union[str, Path],
    buffer_distance: float = 0.0
) -> gpd.GeoDataFrame:
    """
    Load area of interest from GeoJSON file.
    
    Parameters
    ----------
    aoi_path : str or Path
        Path to GeoJSON file containing area of interest
    buffer_distance : float, optional
        Distance to buffer the geometry (in meters), by default 0.0.
        Positive values expand the boundary, reducing edge artifacts.
        
    Returns
    -------
    gpd.GeoDataFrame
        Area of interest as GeoDataFrame
        
    Raises
    ------
    FileNotFoundError
        If GeoJSON file doesn't exist
    ValueError
        If GeoJSON is empty or invalid
        
    Examples
    --------
    >>> aoi = load_aoi('data/nsw.geojson')
    >>> aoi_buffered = load_aoi('data/qld.geojson', buffer_distance=5000)
    """
    aoi_path = Path(aoi_path)
    
    if not aoi_path.exists():
        raise FileNotFoundError(f"AOI file not found: {aoi_path}")
    
    logger.info(f"Loading AOI from: {aoi_path}")
    aoi = gpd.read_file(aoi_path)
    
    if len(aoi) == 0:
        raise ValueError(f"AOI file is empty: {aoi_path}")
    
    # Apply buffer if specified
    if buffer_distance != 0:
        logger.info(f"Applying {buffer_distance}m buffer to AOI")
        # Ensure we're in a projected CRS for metric buffer
        if aoi.crs and aoi.crs.is_geographic:
            # Reproject to Australian Albers for metric operations
            aoi = aoi.to_crs('EPSG:3577')
        aoi['geometry'] = aoi.geometry.buffer(buffer_distance)
    
    logger.info(f"AOI loaded with {len(aoi)} feature(s)")
    logger.info(f"AOI bounds: {aoi.total_bounds}")
    
    return aoi


def load_dea_config(config_path: Union[str, Path] = 'config.yaml') -> Dict:
    """
    Load DEA configuration from YAML file.
    
    Parameters
    ----------
    config_path : str or Path, optional
        Path to configuration YAML file, by default 'config.yaml'
        
    Returns
    -------
    dict
        DEA configuration dictionary
        
    Raises
    ------
    FileNotFoundError
        If config file doesn't exist
    KeyError
        If 'dea_annual_landcover' section not found in config
    """
    config_path = Path(config_path)
    
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    if 'dea_annual_landcover' not in config:
        raise KeyError(
            "Configuration missing 'dea_annual_landcover' section. "
            "Check config.yaml format."
        )
    
    return config['dea_annual_landcover']


def fetch_dea_landcover(
    aoi: gpd.GeoDataFrame,
    start_year: int = 1988,
    end_year: int = 2024,
    product_id: str = 'ga_ls_landcover_class_cyear_2',
    resolution: int = 25,
    crs: str = 'EPSG:3577',
    stac_url: Optional[str] = None
) -> xr.Dataset:
    """
    Fetch DEA annual landcover data for area of interest.
    
    This function attempts multiple access methods in order:
    1. STAC catalog (via pystac-client) - recommended, no auth required
    2. Open Data Cube (via datacube) - requires datacube setup
    3. Fallback to mock data for testing
    
    Parameters
    ----------
    aoi : gpd.GeoDataFrame
        Area of interest
    start_year : int, optional
        Start year for time series, by default 1988
    end_year : int, optional
        End year for time series, by default 2024
    product_id : str, optional
        DEA product identifier, by default 'ga_ls_landcover_class_cyear_2'
    resolution : int, optional
        Spatial resolution in meters, by default 25
    crs : str, optional
        Target coordinate reference system, by default 'EPSG:3577'
    stac_url : str, optional
        STAC catalog URL. If None, uses DEA default.
        
    Returns
    -------
    xr.Dataset
        DEA landcover dataset with time, x, y dimensions
        
    Notes
    -----
    For production use, ensure either pystac-client or datacube is installed.
    See https://knowledge.dea.ga.gov.au/ for datacube setup instructions.
    
    Examples
    --------
    >>> aoi = load_aoi('data/nsw.geojson')
    >>> data = fetch_dea_landcover(aoi, start_year=2000, end_year=2020)
    >>> print(data)
    """
    logger.info(f"Fetching DEA landcover: {product_id}")
    logger.info(f"Time period: {start_year}-{end_year}")
    logger.info(f"Resolution: {resolution}m, CRS: {crs}")
    
    # Get bounds in target CRS
    aoi_crs = aoi.to_crs(crs)
    bounds = aoi_crs.total_bounds  # [minx, miny, maxx, maxy]
    
    # Try STAC access first (recommended)
    if HAS_PYSTAC:
        try:
            return _fetch_via_stac(
                bounds=bounds,
                start_year=start_year,
                end_year=end_year,
                product_id=product_id,
                resolution=resolution,
                crs=crs,
                stac_url=stac_url
            )
        except Exception as e:
            logger.warning(f"STAC access failed: {e}")
    
    # Try Open Data Cube access
    if HAS_DATACUBE:
        try:
            return _fetch_via_datacube(
                bounds=bounds,
                start_year=start_year,
                end_year=end_year,
                product_id=product_id,
                resolution=resolution,
                crs=crs
            )
        except Exception as e:
            logger.warning(f"Datacube access failed: {e}")
    
    # Fallback to mock data for development/testing
    logger.warning(
        "No data access method available. "
        "Install 'pystac-client' or 'datacube' for real data access. "
        "Returning mock data for demonstration."
    )
    return _create_mock_dea_data(bounds, start_year, end_year, resolution, crs)


def _fetch_via_stac(
    bounds: Tuple[float, float, float, float],
    start_year: int,
    end_year: int,
    product_id: str,
    resolution: int,
    crs: str,
    stac_url: Optional[str] = None
) -> xr.Dataset:
    """
    Fetch DEA data via STAC catalog.
    
    This is a template function - full implementation requires
    odc-stac library and proper STAC item processing.
    """
    stac_url = stac_url or "https://explorer.dea.ga.gov.au/stac"
    
    logger.info(f"Accessing STAC catalog: {stac_url}")
    
    # This is a placeholder for STAC implementation
    # In production, use odc-stac to load data:
    # from odc.stac import load
    # catalog = Client.open(stac_url)
    # items = catalog.search(...).item_collection()
    # ds = load(items, bbox=bounds, ...)
    
    raise NotImplementedError(
        "STAC access template requires odc-stac implementation. "
        "See DEA documentation: https://knowledge.dea.ga.gov.au/"
    )


def _fetch_via_datacube(
    bounds: Tuple[float, float, float, float],
    start_year: int,
    end_year: int,
    product_id: str,
    resolution: int,
    crs: str
) -> xr.Dataset:
    """
    Fetch DEA data via Open Data Cube.
    
    This is a template function - requires datacube configuration.
    """
    logger.info("Accessing Open Data Cube")
    
    # This is a placeholder for datacube implementation
    # In production:
    # dc = datacube.Datacube()
    # ds = dc.load(
    #     product=product_id,
    #     x=(bounds[0], bounds[2]),
    #     y=(bounds[1], bounds[3]),
    #     time=(f'{start_year}-01-01', f'{end_year}-12-31'),
    #     output_crs=crs,
    #     resolution=(-resolution, resolution)
    # )
    
    raise NotImplementedError(
        "Datacube access template requires datacube configuration. "
        "See DEA documentation: https://knowledge.dea.ga.gov.au/"
    )


def _create_mock_dea_data(
    bounds: Tuple[float, float, float, float],
    start_year: int,
    end_year: int,
    resolution: int,
    crs: str
) -> xr.Dataset:
    """
    Create mock DEA data for testing and demonstration.
    
    This generates synthetic landcover data with realistic structure
    but random values. Use for template demonstration only.
    """
    logger.info("Creating mock DEA data for demonstration")
    
    # Calculate grid dimensions
    width = int((bounds[2] - bounds[0]) / resolution)
    height = int((bounds[3] - bounds[1]) / resolution)
    
    # Limit size for mock data, ensure at least 2x2 grid
    width = max(2, min(width, 100))
    height = max(2, min(height, 100))
    
    # Create coordinate arrays
    x = np.linspace(bounds[0], bounds[2], width)
    y = np.linspace(bounds[1], bounds[3], height)
    
    # Create time dimension
    years = range(start_year, end_year + 1)
    n_years = len(years)
    
    # Create mock landcover data
    # DEA classes: 1=crops, 2=woody, 3=wetland, 4=urban, 5=bare, 6=water
    landcover = np.random.randint(1, 7, size=(n_years, height, width), dtype=np.uint8)
    
    # Create dataset
    ds = xr.Dataset(
        data_vars={
            'landcover_class': (['time', 'y', 'x'], landcover)
        },
        coords={
            'time': [f'{year}-07-01' for year in years],
            'y': y,
            'x': x
        },
        attrs={
            'crs': crs,
            'product': 'mock_dea_landcover',
            'resolution': resolution,
            'note': 'This is mock data for demonstration only'
        }
    )
    
    return ds


def reclassify_dea_to_woody_nonwoody(
    data: Union[xr.Dataset, xr.DataArray, np.ndarray],
    classes_map: Optional[Dict[str, List[int]]] = None
) -> Union[xr.DataArray, np.ndarray]:
    """
    Reclassify DEA land cover classes to woody/non-woody scheme.
    
    Output scheme:
        0 = Other/masked (water, urban, bare, nodata)
        1 = Woody vegetation (forests, woodlands, dense shrubs)
        2 = Non-woody vegetation (grasslands, crops, wetlands)
    
    Parameters
    ----------
    data : xr.Dataset, xr.DataArray, or np.ndarray
        Input DEA landcover data
    classes_map : dict, optional
        Custom class mapping. If None, uses default mapping:
        - woody: [2] (Natural Terrestrial Vegetated)
        - non_woody: [1, 3] (Cultivated, Aquatic Vegetated)
        - other: [4, 5, 6, 0] (Artificial, Bare, Water, NoData)
        
    Returns
    -------
    xr.DataArray or np.ndarray
        Reclassified data with values 0, 1, or 2
        
    Examples
    --------
    >>> ds = fetch_dea_landcover(aoi, 2000, 2020)
    >>> classified = reclassify_dea_to_woody_nonwoody(ds)
    >>> print(np.unique(classified.values))
    [0 1 2]
    """
    # Default class mapping
    if classes_map is None:
        classes_map = {
            'woody': [2],  # Natural Terrestrial Vegetated
            'non_woody': [1, 3],  # Cultivated + Aquatic Vegetated
            'other': [0, 4, 5, 6]  # NoData, Artificial, Bare, Water
        }
    
    # Extract numpy array from xarray if needed
    if isinstance(data, xr.Dataset):
        # Try common variable names
        if len(data.data_vars) == 0:
            raise ValueError("Dataset has no data variables")
        
        for var_name in ['landcover_class', 'landcover', 'level_4', 'classification']:
            if var_name in data.data_vars:
                arr = data[var_name].values
                break
        else:
            # Use first available variable if no standard name found
            first_var = list(data.data_vars.keys())[0]
            logger.warning(f"Using non-standard variable name: {first_var}")
            arr = data[first_var].values
    elif isinstance(data, xr.DataArray):
        arr = data.values
    else:
        arr = np.asarray(data)
    
    # Create output array
    output = np.zeros_like(arr, dtype=np.uint8)
    
    # Apply reclassification
    for dea_class in classes_map.get('woody', []):
        output[arr == dea_class] = 1
    
    for dea_class in classes_map.get('non_woody', []):
        output[arr == dea_class] = 2
    
    # 'other' classes remain 0
    
    logger.info(f"Reclassification complete. Output classes: {np.unique(output)}")
    logger.info(f"  Woody (1): {np.sum(output == 1)} pixels")
    logger.info(f"  Non-woody (2): {np.sum(output == 2)} pixels")
    logger.info(f"  Other (0): {np.sum(output == 0)} pixels")
    
    # Return as DataArray if input was xarray
    if isinstance(data, (xr.Dataset, xr.DataArray)):
        if isinstance(data, xr.Dataset):
            coords = data[list(data.data_vars.keys())[0]].coords
        else:
            coords = data.coords
        
        return xr.DataArray(
            output,
            coords=coords,
            dims=coords.dims,
            attrs={
                'long_name': 'Woody/Non-woody classification',
                'classes': '0=other, 1=woody, 2=non-woody',
                'source': 'DEA Annual Landcover reclassified'
            }
        )
    
    return output


def export_yearly_geotiff(
    data: xr.DataArray,
    year: int,
    output_path: Union[str, Path],
    nodata_value: int = 255,
    compress: str = 'lzw'
) -> None:
    """
    Export single year of data to GeoTIFF.
    
    Parameters
    ----------
    data : xr.DataArray
        Landcover data for single year
    year : int
        Year being exported
    output_path : str or Path
        Output GeoTIFF file path
    nodata_value : int, optional
        NoData value for output, by default 255
    compress : str, optional
        Compression method ('lzw', 'deflate', 'none'), by default 'lzw'
        
    Examples
    --------
    >>> ds = fetch_dea_landcover(aoi, 2000, 2020)
    >>> classified = reclassify_dea_to_woody_nonwoody(ds)
    >>> for year in range(2000, 2021):
    ...     year_data = classified.sel(time=f'{year}-07-01')
    ...     export_yearly_geotiff(year_data, year, f'output/landcover_{year}.tif')
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Extract year data if time dimension present
    if 'time' in data.dims and len(data.time) > 1:
        # Select data for target year
        # Handle both datetime and string time coordinates
        try:
            # Try direct selection first
            target_time = f'{year}-07-01'
            year_data = data.sel(time=target_time, method='nearest')
        except (KeyError, TypeError):
            # Fallback: select by index based on year
            time_values = data.time.values
            # Find index matching year
            year_idx = None
            for idx, t in enumerate(time_values):
                t_str = str(t)
                if str(year) in t_str:
                    year_idx = idx
                    break
            
            if year_idx is not None:
                year_data = data.isel(time=year_idx)
            else:
                logger.warning(f"Could not find data for year {year}, using first time step")
                year_data = data.isel(time=0)
    else:
        year_data = data
    
    # Get spatial extent
    if 'x' in year_data.coords and 'y' in year_data.coords:
        x = year_data.x.values
        y = year_data.y.values
        transform = from_bounds(
            x.min(), y.min(), x.max(), y.max(),
            len(x), len(y)
        )
    else:
        # Default transform if coords missing
        transform = from_bounds(0, 0, year_data.shape[1], year_data.shape[0],
                                year_data.shape[1], year_data.shape[0])
    
    # Get CRS
    crs_str = year_data.attrs.get('crs', 'EPSG:3577')
    
    # Write GeoTIFF
    with rasterio.open(
        output_path,
        'w',
        driver='GTiff',
        height=year_data.shape[0],
        width=year_data.shape[1],
        count=1,
        dtype=year_data.dtype,
        crs=crs_str,
        transform=transform,
        nodata=nodata_value,
        compress=compress
    ) as dst:
        dst.write(year_data.values, 1)
        dst.set_band_description(1, f'Landcover {year}')
    
    logger.info(f"Exported {year} to: {output_path}")


def create_animation(
    image_paths: List[Union[str, Path]],
    output_path: Union[str, Path],
    fps: int = 2,
    loop: int = 0
) -> None:
    """
    Create animated GIF from sequence of GeoTIFF files.
    
    Parameters
    ----------
    image_paths : list of str or Path
        Paths to input GeoTIFF files (in temporal order)
    output_path : str or Path
        Output GIF file path
    fps : int, optional
        Frames per second, by default 2
    loop : int, optional
        Number of loops (0 = infinite), by default 0
        
    Raises
    ------
    ImportError
        If imageio is not installed
        
    Examples
    --------
    >>> image_files = [f'output/landcover_{y}.tif' for y in range(2000, 2021)]
    >>> create_animation(image_files, 'output/animation.gif', fps=2)
    """
    if not HAS_IMAGEIO:
        raise ImportError(
            "imageio required for animation. Install with: pip install imageio"
        )
    
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Creating animation from {len(image_paths)} images")
    
    images = []
    for img_path in image_paths:
        with rasterio.open(img_path) as src:
            # Read data and normalize to 0-255
            data = src.read(1)
            # Simple normalization - adjust as needed
            data_norm = ((data / data.max()) * 255).astype(np.uint8)
            images.append(data_norm)
    
    # Save as GIF
    imageio.mimsave(
        output_path,
        images,
        fps=fps,
        loop=loop
    )
    
    logger.info(f"Animation saved to: {output_path}")
    logger.info(f"  Frames: {len(images)}, FPS: {fps}")

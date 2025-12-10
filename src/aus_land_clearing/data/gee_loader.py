"""
Google Earth Engine (GEE) data access module for land clearing analysis
"""
import warnings
from typing import List, Tuple, Optional, Dict, Any
import pandas as pd

try:
    import ee
    import geemap
    GEE_AVAILABLE = True
except ImportError:
    GEE_AVAILABLE = False


def initialize_gee(project: str = None) -> bool:
    """
    Initialize Google Earth Engine.
    
    Parameters
    ----------
    project : str, optional
        GEE project ID. If None, uses default credentials.
        
    Returns
    -------
    bool
        True if initialization successful
        
    Notes
    -----
    Requires authentication via:
    - `earthengine authenticate` (first time)
    - Valid GEE account
    
    See: https://developers.google.com/earth-engine/guides/python_install
    """
    if not GEE_AVAILABLE:
        warnings.warn(
            "Google Earth Engine not available. Install with:\n"
            "pip install earthengine-api geemap",
            UserWarning
        )
        return False
    
    try:
        if project:
            ee.Initialize(project=project)
        else:
            ee.Initialize()
        return True
    except Exception as e:
        warnings.warn(
            f"Failed to initialize GEE: {e}\n"
            "Run: earthengine authenticate",
            UserWarning
        )
        return False


def load_gee_landsat_fc(
    bbox: List[float],
    time_range: Tuple[str, str],
    cloud_cover: int = 30,
    scale: int = 30
) -> Dict[str, Any]:
    """
    Load Landsat fractional cover data from Google Earth Engine.
    
    Parameters
    ----------
    bbox : list
        Bounding box [min_lon, min_lat, max_lon, max_lat]
    time_range : tuple
        Time range as (start_date, end_date) in format 'YYYY-MM-DD'
    cloud_cover : int, optional
        Maximum cloud cover percentage (default: 30)
    scale : int, optional
        Spatial resolution in meters (default: 30)
        
    Returns
    -------
    dict
        Dictionary with 'collection' (ee.ImageCollection) and metadata
        
    Notes
    -----
    Uses Landsat Collection 2 data from GEE.
    Returns spectral indices that can be used to derive fractional cover.
    
    Example
    -------
    >>> bbox = [138.0, -29.2, 154.0, -10.0]  # Queensland
    >>> time_range = ('2020-01-01', '2020-12-31')
    >>> data = load_gee_landsat_fc(bbox, time_range)
    """
    if not GEE_AVAILABLE or not initialize_gee():
        warnings.warn("GEE not available. Returning empty result.", UserWarning)
        return {'collection': None, 'metadata': {}}
    
    # Define region of interest
    roi = ee.Geometry.Rectangle(bbox)
    
    # Load Landsat 8/9 Collection 2
    collection = (ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')
                  .filterBounds(roi)
                  .filterDate(time_range[0], time_range[1])
                  .filter(ee.Filter.lt('CLOUD_COVER', cloud_cover)))
    
    # Add NDVI, NDMI for vegetation analysis
    def add_indices(image):
        ndvi = image.normalizedDifference(['SR_B5', 'SR_B4']).rename('NDVI')
        ndmi = image.normalizedDifference(['SR_B5', 'SR_B6']).rename('NDMI')
        return image.addBands([ndvi, ndmi])
    
    collection = collection.map(add_indices)
    
    metadata = {
        'bbox': bbox,
        'time_range': time_range,
        'cloud_cover': cloud_cover,
        'scale': scale,
        'count': collection.size().getInfo(),
        'source': 'LANDSAT/LC08/C02/T1_L2'
    }
    
    return {
        'collection': collection,
        'metadata': metadata,
        'roi': roi
    }


def load_gee_sentinel2_fc(
    bbox: List[float],
    time_range: Tuple[str, str],
    cloud_cover: int = 30,
    scale: int = 10
) -> Dict[str, Any]:
    """
    Load Sentinel-2 data from Google Earth Engine for vegetation analysis.
    
    Parameters
    ----------
    bbox : list
        Bounding box [min_lon, min_lat, max_lon, max_lat]
    time_range : tuple
        Time range as (start_date, end_date) in format 'YYYY-MM-DD'
    cloud_cover : int, optional
        Maximum cloud cover percentage (default: 30)
    scale : int, optional
        Spatial resolution in meters (default: 10)
        
    Returns
    -------
    dict
        Dictionary with 'collection' (ee.ImageCollection) and metadata
        
    Notes
    -----
    Sentinel-2 data available from 2015-present with 10m resolution.
    Higher temporal frequency than Landsat.
    
    Example
    -------
    >>> bbox = [140.9, -38.0, 153.6, -28.1]  # NSW
    >>> time_range = ('2020-01-01', '2020-12-31')
    >>> data = load_gee_sentinel2_fc(bbox, time_range)
    """
    if not GEE_AVAILABLE or not initialize_gee():
        warnings.warn("GEE not available. Returning empty result.", UserWarning)
        return {'collection': None, 'metadata': {}}
    
    # Define region of interest
    roi = ee.Geometry.Rectangle(bbox)
    
    # Load Sentinel-2 Surface Reflectance
    collection = (ee.ImageCollection('COPERNICUS/S2_SR')
                  .filterBounds(roi)
                  .filterDate(time_range[0], time_range[1])
                  .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', cloud_cover)))
    
    # Add vegetation indices
    def add_indices(image):
        ndvi = image.normalizedDifference(['B8', 'B4']).rename('NDVI')
        ndmi = image.normalizedDifference(['B8', 'B11']).rename('NDMI')
        evi = image.expression(
            '2.5 * ((NIR - RED) / (NIR + 6 * RED - 7.5 * BLUE + 1))',
            {
                'NIR': image.select('B8'),
                'RED': image.select('B4'),
                'BLUE': image.select('B2')
            }
        ).rename('EVI')
        return image.addBands([ndvi, ndmi, evi])
    
    collection = collection.map(add_indices)
    
    metadata = {
        'bbox': bbox,
        'time_range': time_range,
        'cloud_cover': cloud_cover,
        'scale': scale,
        'count': collection.size().getInfo(),
        'source': 'COPERNICUS/S2_SR'
    }
    
    return {
        'collection': collection,
        'metadata': metadata,
        'roi': roi
    }


def export_gee_timeseries(
    collection_data: Dict[str, Any],
    variable: str = 'NDVI',
    output_path: str = None,
    format: str = 'csv'
) -> pd.DataFrame:
    """
    Export time series from GEE collection to local file.
    
    Parameters
    ----------
    collection_data : dict
        Dictionary returned from load_gee_landsat_fc or load_gee_sentinel2_fc
    variable : str, optional
        Variable to export (default: 'NDVI')
    output_path : str, optional
        Path to save exported data
    format : str, optional
        Output format: 'csv', 'geotiff', 'json'
        
    Returns
    -------
    pandas.DataFrame
        Time series data
        
    Notes
    -----
    For large exports, use GEE Export tasks to Google Drive/Cloud Storage.
    This function is for moderate-sized time series.
    
    Example
    -------
    >>> data = load_gee_landsat_fc(bbox, time_range)
    >>> ts = export_gee_timeseries(data, variable='NDVI', output_path='ndvi_ts.csv')
    """
    if not GEE_AVAILABLE:
        warnings.warn("GEE not available.", UserWarning)
        return pd.DataFrame()
    
    collection = collection_data.get('collection')
    roi = collection_data.get('roi')
    
    if collection is None or roi is None:
        return pd.DataFrame()
    
    # Reduce region for time series
    def reduce_image(image):
        stats = image.select(variable).reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=roi,
            scale=collection_data['metadata']['scale'],
            maxPixels=1e9
        )
        return ee.Feature(None, {
            'date': image.date().format('YYYY-MM-dd'),
            variable: stats.get(variable)
        })
    
    # Convert to feature collection
    fc = ee.FeatureCollection(collection.map(reduce_image))
    
    # Get data
    data = fc.getInfo()
    
    # Convert to DataFrame
    records = []
    for feature in data['features']:
        props = feature['properties']
        if props.get(variable) is not None:
            records.append({
                'date': props['date'],
                variable: props[variable]
            })
    
    df = pd.DataFrame(records)
    if not df.empty:
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
    
    if output_path:
        if format == 'csv':
            df.to_csv(output_path, index=False)
        elif format == 'json':
            df.to_json(output_path, orient='records', date_format='iso')
    
    return df


def export_gee_to_drive(
    collection_data: Dict[str, Any],
    variable: str,
    description: str = 'export',
    folder: str = 'GEE_Exports',
    scale: int = 30
) -> None:
    """
    Export GEE data to Google Drive (for large datasets).
    
    Parameters
    ----------
    collection_data : dict
        Dictionary returned from GEE load functions
    variable : str
        Variable/band to export
    description : str, optional
        Export task description
    folder : str, optional
        Google Drive folder name
    scale : int, optional
        Export resolution in meters
        
    Notes
    -----
    This creates an export task in GEE. Monitor progress at:
    https://code.earthengine.google.com/tasks
    
    Example
    -------
    >>> data = load_gee_landsat_fc(bbox, time_range)
    >>> export_gee_to_drive(data, 'NDVI', description='qld_ndvi_2020')
    """
    if not GEE_AVAILABLE:
        warnings.warn("GEE not available.", UserWarning)
        return
    
    collection = collection_data.get('collection')
    roi = collection_data.get('roi')
    
    if collection is None or roi is None:
        warnings.warn("No valid collection to export.", UserWarning)
        return
    
    # Create composite (mean)
    composite = collection.select(variable).mean().clip(roi)
    
    # Create export task
    task = ee.batch.Export.image.toDrive(
        image=composite,
        description=description,
        folder=folder,
        scale=scale,
        region=roi,
        maxPixels=1e13
    )
    
    task.start()
    print(f"Export task started: {description}")
    print(f"Monitor at: https://code.earthengine.google.com/tasks")

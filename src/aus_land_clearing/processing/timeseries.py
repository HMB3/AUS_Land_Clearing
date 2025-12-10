"""
Time-series processing and analysis module
"""
import xarray as xr
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from datetime import datetime


def extract_time_series(
    dataset: xr.Dataset,
    variable: str = None,
    method: str = 'mean',
    mask: Optional[xr.DataArray] = None
) -> pd.DataFrame:
    """
    Extract time series statistics from a dataset.
    
    Parameters
    ----------
    dataset : xarray.Dataset
        Input dataset with time dimension
    variable : str, optional
        Variable to extract. If None, uses first data variable
    method : str, optional
        Aggregation method: 'mean', 'median', 'sum', 'std'
    mask : xarray.DataArray, optional
        Boolean mask to apply before aggregation
        
    Returns
    -------
    pandas.DataFrame
        Time series with statistics
        
    Example
    -------
    >>> ds = load_dea_fractional_cover(bbox, time_range)
    >>> ts = extract_time_series(ds, variable='PV', method='mean')
    """
    if dataset.data_vars is None or len(dataset.data_vars) == 0:
        return pd.DataFrame()
    
    if variable is None:
        variable = list(dataset.data_vars)[0]
    
    data = dataset[variable]
    
    if mask is not None:
        data = data.where(mask)
    
    # Apply aggregation method
    if method == 'mean':
        ts = data.mean(dim=['x', 'y'])
    elif method == 'median':
        ts = data.median(dim=['x', 'y'])
    elif method == 'sum':
        ts = data.sum(dim=['x', 'y'])
    elif method == 'std':
        ts = data.std(dim=['x', 'y'])
    else:
        raise ValueError(f"Unknown method: {method}")
    
    # Convert to DataFrame
    df = ts.to_dataframe()
    df = df.reset_index()
    
    return df


def calculate_change_statistics(
    dataset: xr.Dataset,
    variable: str,
    baseline_period: Tuple[str, str],
    comparison_period: Tuple[str, str]
) -> Dict[str, float]:
    """
    Calculate change statistics between two time periods.
    
    Parameters
    ----------
    dataset : xarray.Dataset
        Input dataset with time dimension
    variable : str
        Variable to analyze
    baseline_period : tuple
        Baseline period as (start_date, end_date)
    comparison_period : tuple
        Comparison period as (start_date, end_date)
        
    Returns
    -------
    dict
        Dictionary with change statistics:
        - 'absolute_change': Absolute change
        - 'percent_change': Percentage change
        - 'baseline_mean': Mean value in baseline period
        - 'comparison_mean': Mean value in comparison period
        
    Example
    -------
    >>> baseline = ('1988-01-01', '1995-12-31')
    >>> comparison = ('2015-01-01', '2024-12-31')
    >>> stats = calculate_change_statistics(ds, 'PV', baseline, comparison)
    """
    if dataset.data_vars is None or len(dataset.data_vars) == 0:
        return {}
    
    # Select baseline period
    baseline_data = dataset[variable].sel(
        time=slice(baseline_period[0], baseline_period[1])
    )
    baseline_mean = float(baseline_data.mean().values)
    
    # Select comparison period
    comparison_data = dataset[variable].sel(
        time=slice(comparison_period[0], comparison_period[1])
    )
    comparison_mean = float(comparison_data.mean().values)
    
    # Calculate change
    absolute_change = comparison_mean - baseline_mean
    percent_change = (absolute_change / baseline_mean) * 100 if baseline_mean != 0 else 0
    
    return {
        'absolute_change': absolute_change,
        'percent_change': percent_change,
        'baseline_mean': baseline_mean,
        'comparison_mean': comparison_mean,
        'baseline_period': baseline_period,
        'comparison_period': comparison_period,
    }


def detect_clearing_events(
    dataset: xr.Dataset,
    variable: str = 'PV',
    threshold: float = -20.0,
    min_duration: int = 1
) -> pd.DataFrame:
    """
    Detect land clearing events based on vegetation decline.
    
    Parameters
    ----------
    dataset : xarray.Dataset
        Input dataset with vegetation data
    variable : str, optional
        Variable to analyze (default: 'PV' for photosynthetic vegetation)
    threshold : float, optional
        Threshold for change detection (default: -20% change)
    min_duration : int, optional
        Minimum number of time steps for event detection
        
    Returns
    -------
    pandas.DataFrame
        DataFrame with detected events:
        - 'start_date': Event start date
        - 'end_date': Event end date
        - 'magnitude': Change magnitude
        - 'location': Spatial coordinates
        
    Example
    -------
    >>> events = detect_clearing_events(ds, variable='PV', threshold=-25)
    """
    if dataset.data_vars is None or len(dataset.data_vars) == 0:
        return pd.DataFrame(columns=['start_date', 'end_date', 'magnitude', 'x', 'y'])
    
    # This is a simplified template
    # Full implementation would include:
    # 1. Calculate temporal differences
    # 2. Apply threshold
    # 3. Identify connected regions
    # 4. Extract event metadata
    
    events = pd.DataFrame(columns=['start_date', 'end_date', 'magnitude', 'x', 'y'])
    return events


def aggregate_by_period(
    dataset: xr.Dataset,
    variable: str,
    period: str = 'year'
) -> xr.Dataset:
    """
    Aggregate dataset by temporal period.
    
    Parameters
    ----------
    dataset : xarray.Dataset
        Input dataset with time dimension
    variable : str
        Variable to aggregate
    period : str, optional
        Aggregation period: 'year', 'season', 'month'
        
    Returns
    -------
    xarray.Dataset
        Aggregated dataset
        
    Example
    -------
    >>> annual_ds = aggregate_by_period(ds, 'PV', period='year')
    """
    if dataset.data_vars is None or len(dataset.data_vars) == 0:
        return xr.Dataset()
    
    if period == 'year':
        aggregated = dataset.resample(time='1Y').mean()
    elif period == 'season':
        aggregated = dataset.resample(time='QS-DEC').mean()
    elif period == 'month':
        aggregated = dataset.resample(time='1M').mean()
    else:
        raise ValueError(f"Unknown period: {period}")
    
    return aggregated


def calculate_vegetation_indices(
    fractional_cover: xr.Dataset
) -> xr.Dataset:
    """
    Calculate vegetation indices from fractional cover data.
    
    Parameters
    ----------
    fractional_cover : xarray.Dataset
        Fractional cover dataset with PV, NPV, BS bands
        
    Returns
    -------
    xarray.Dataset
        Dataset with additional vegetation indices:
        - 'total_vegetation': PV + NPV
        - 'green_fraction': PV / (PV + NPV + BS)
        - 'vegetation_health': PV / (PV + NPV)
        
    Example
    -------
    >>> fc_ds = load_dea_fractional_cover(bbox, time_range)
    >>> indices = calculate_vegetation_indices(fc_ds)
    """
    if fractional_cover.data_vars is None or len(fractional_cover.data_vars) == 0:
        return xr.Dataset()
    
    ds = fractional_cover.copy()
    
    # Check if required bands exist
    if 'PV' in ds and 'NPV' in ds and 'BS' in ds:
        # Total vegetation
        ds['total_vegetation'] = ds['PV'] + ds['NPV']
        
        # Green fraction
        total = ds['PV'] + ds['NPV'] + ds['BS']
        ds['green_fraction'] = ds['PV'] / total.where(total > 0)
        
        # Vegetation health (green vs dry)
        veg_sum = ds['PV'] + ds['NPV']
        ds['vegetation_health'] = ds['PV'] / veg_sum.where(veg_sum > 0)
    
    return ds

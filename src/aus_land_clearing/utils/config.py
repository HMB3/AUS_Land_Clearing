"""
Configuration management utilities
"""
import yaml
from pathlib import Path
from typing import Dict, Any


def load_config(config_path: str = None) -> Dict[str, Any]:
    """
    Load configuration from YAML file.
    
    Parameters
    ----------
    config_path : str, optional
        Path to configuration file. If None, uses default config.yaml
        
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
            raise FileNotFoundError("Could not find config.yaml in project directory")
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    return config


def get_study_area_bbox(state: str = None) -> list:
    """
    Get bounding box for study area.
    
    Parameters
    ----------
    state : str, optional
        State name ('queensland', 'new_south_wales'), or None for entire study area
        
    Returns
    -------
    list
        Bounding box as [min_lon, min_lat, max_lon, max_lat]
    """
    config = load_config()
    
    if state is None:
        return config['study_area']['bbox']
    else:
        state_lower = state.lower().replace(' ', '_')
        return config['study_area']['states'][state_lower]['bbox']


def get_time_range() -> tuple:
    """
    Get configured time range for analysis.
    
    Returns
    -------
    tuple
        (start_year, end_year)
    """
    config = load_config()
    return (
        config['time_period']['start_year'],
        config['time_period']['end_year']
    )


def get_data_source_info(source_name: str) -> Dict[str, Any]:
    """
    Get information about a data source.
    
    Parameters
    ----------
    source_name : str
        Data source name ('dea_land_cover', 'dea_fractional_cover', 'slats')
        
    Returns
    -------
    dict
        Data source configuration
    """
    config = load_config()
    return config['data_sources'][source_name]

"""
Data access module - supports both DEA and Google Earth Engine
"""
from .loader import (
    load_dea_land_cover,
    load_dea_fractional_cover,
    load_slats_data,
    load_boundary,
)

from .gee_loader import (
    initialize_gee,
    load_gee_landsat_fc,
    load_gee_sentinel2_fc,
    export_gee_timeseries,
    export_gee_to_drive,
)

__all__ = [
    # DEA loaders
    "load_dea_land_cover",
    "load_dea_fractional_cover",
    "load_slats_data",
    "load_boundary",
    # GEE loaders
    "initialize_gee",
    "load_gee_landsat_fc",
    "load_gee_sentinel2_fc",
    "export_gee_timeseries",
    "export_gee_to_drive",
]

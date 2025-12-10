"""
Data access module
"""
from .loader import (
    load_dea_land_cover,
    load_dea_fractional_cover,
    load_slats_data,
    load_boundary,
)

__all__ = [
    "load_dea_land_cover",
    "load_dea_fractional_cover",
    "load_slats_data",
    "load_boundary",
]

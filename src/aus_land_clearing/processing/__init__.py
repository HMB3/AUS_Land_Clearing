"""
Processing module for time-series analysis
"""
from .timeseries import (
    extract_time_series,
    calculate_change_statistics,
    detect_clearing_events,
    aggregate_by_period,
    calculate_vegetation_indices,
)

__all__ = [
    "extract_time_series",
    "calculate_change_statistics",
    "detect_clearing_events",
    "aggregate_by_period",
    "calculate_vegetation_indices",
]

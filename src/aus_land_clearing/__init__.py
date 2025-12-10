"""
AUS Land Clearing: Story-driven visualisations of land clearing across eastern Australia

This package provides tools for analyzing and visualizing land clearing patterns
in Queensland and New South Wales from 1988 to present using authoritative
data sources including DEA Land Cover, DEA Fractional Cover, and SLATS.
"""

__version__ = "0.1.0"
__author__ = "AUS Land Clearing Team"

from .data import (
    load_dea_land_cover,
    load_dea_fractional_cover,
    load_slats_data,
)

from .processing import (
    calculate_change_statistics,
    extract_time_series,
    detect_clearing_events,
)

from .visualization import (
    create_time_series_plot,
    create_animation,
    create_narrative_visualization,
)

__all__ = [
    # Data loading
    "load_dea_land_cover",
    "load_dea_fractional_cover",
    "load_slats_data",
    # Processing
    "calculate_change_statistics",
    "extract_time_series",
    "detect_clearing_events",
    # Visualization
    "create_time_series_plot",
    "create_animation",
    "create_narrative_visualization",
]

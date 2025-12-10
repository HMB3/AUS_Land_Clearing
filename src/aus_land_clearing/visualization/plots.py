"""
Visualization module for creating story-driven land clearing visualizations
"""
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import pandas as pd
import xarray as xr
from typing import Optional, List, Dict, Tuple
from pathlib import Path
import warnings


def create_time_series_plot(
    time_series: pd.DataFrame,
    variable: str,
    title: str = None,
    xlabel: str = 'Year',
    ylabel: str = None,
    output_path: str = None,
    figsize: Tuple[int, int] = (12, 6),
    style: str = 'seaborn-v0_8-darkgrid'
) -> plt.Figure:
    """
    Create a time series plot for land clearing analysis.
    
    Parameters
    ----------
    time_series : pandas.DataFrame
        Time series data with time index
    variable : str
        Variable to plot
    title : str, optional
        Plot title
    xlabel : str, optional
        X-axis label
    ylabel : str, optional
        Y-axis label
    output_path : str, optional
        Path to save figure
    figsize : tuple, optional
        Figure size (width, height)
    style : str, optional
        Matplotlib style
        
    Returns
    -------
    matplotlib.figure.Figure
        Generated figure
        
    Example
    -------
    >>> ts = extract_time_series(ds, 'PV')
    >>> fig = create_time_series_plot(ts, 'PV', title='Vegetation Cover Over Time')
    """
    if time_series.empty:
        warnings.warn("Empty time series data provided")
        return plt.figure()
    
    try:
        plt.style.use(style)
    except:
        pass  # Fall back to default style
    
    fig, ax = plt.subplots(figsize=figsize)
    
    if 'time' in time_series.columns:
        x = pd.to_datetime(time_series['time'])
    else:
        x = time_series.index
    
    if variable in time_series.columns:
        y = time_series[variable]
        ax.plot(x, y, linewidth=2, color='#2E7D32', marker='o', markersize=4)
    
    if title:
        ax.set_title(title, fontsize=14, fontweight='bold')
    
    ax.set_xlabel(xlabel, fontsize=12)
    
    if ylabel is None:
        ylabel = variable
    ax.set_ylabel(ylabel, fontsize=12)
    
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    
    if output_path:
        fig.savefig(output_path, dpi=300, bbox_inches='tight')
    
    return fig


def create_animation(
    dataset: xr.Dataset,
    variable: str,
    output_path: str,
    title_template: str = "Land Cover - {date}",
    fps: int = 2,
    dpi: int = 150,
    cmap: str = 'RdYlGn',
    vmin: float = None,
    vmax: float = None
) -> str:
    """
    Create an animation from time-series dataset.
    
    Parameters
    ----------
    dataset : xarray.Dataset
        Input dataset with time dimension
    variable : str
        Variable to animate
    output_path : str
        Output path for animation (e.g., 'animation.mp4' or 'animation.gif')
    title_template : str, optional
        Title template with {date} placeholder
    fps : int, optional
        Frames per second (default: 2)
    dpi : int, optional
        Resolution (default: 150)
    cmap : str, optional
        Colormap (default: 'RdYlGn')
    vmin, vmax : float, optional
        Color scale limits
        
    Returns
    -------
    str
        Path to saved animation
        
    Example
    -------
    >>> ds = load_dea_fractional_cover(bbox, time_range)
    >>> create_animation(ds, 'PV', 'vegetation_change.mp4', fps=2)
    """
    if dataset.data_vars is None or len(dataset.data_vars) == 0:
        warnings.warn("Empty dataset provided")
        return ""
    
    if variable not in dataset.data_vars:
        warnings.warn(f"Variable {variable} not found in dataset")
        return ""
    
    data = dataset[variable]
    
    # Determine color scale if not provided
    if vmin is None:
        vmin = float(data.min().values)
    if vmax is None:
        vmax = float(data.max().values)
    
    # Create figure
    fig, ax = plt.subplots(figsize=(12, 8))
    
    def animate(frame_idx):
        """Animation function for each frame"""
        ax.clear()
        
        # Get data for this time step
        time_slice = data.isel(time=frame_idx)
        
        # Plot
        im = time_slice.plot(
            ax=ax,
            cmap=cmap,
            vmin=vmin,
            vmax=vmax,
            add_colorbar=True
        )
        
        # Format title with date
        if 'time' in data.coords:
            date_str = pd.to_datetime(str(time_slice.time.values)).strftime('%Y-%m-%d')
            ax.set_title(title_template.format(date=date_str), fontsize=14, fontweight='bold')
        
        return [im]
    
    # Create animation
    n_frames = len(data.time) if 'time' in data.dims else 1
    anim = animation.FuncAnimation(
        fig, animate, frames=n_frames, interval=1000/fps, blit=False
    )
    
    # Save animation
    output_path = str(output_path)
    if output_path.endswith('.gif'):
        anim.save(output_path, writer='pillow', fps=fps, dpi=dpi)
    else:
        # Default to mp4
        anim.save(output_path, writer='ffmpeg', fps=fps, dpi=dpi)
    
    plt.close(fig)
    return output_path


def create_narrative_visualization(
    dataset: xr.Dataset,
    variable: str,
    narrative_type: str,
    output_path: str,
    figsize: Tuple[int, int] = (16, 10)
) -> str:
    """
    Create a narrative-driven visualization for land clearing stories.
    
    Parameters
    ----------
    dataset : xarray.Dataset
        Input dataset
    variable : str
        Variable to visualize
    narrative_type : str
        Type of narrative:
        - 'before_after': Before/after comparison
        - 'multi_temporal': Multiple time points
        - 'change_map': Change detection map
        - 'timeline': Timeline with key events
    output_path : str
        Output path for figure
    figsize : tuple, optional
        Figure size
        
    Returns
    -------
    str
        Path to saved figure
        
    Example
    -------
    >>> create_narrative_visualization(
    ...     ds, 'PV', 'before_after', 'clearing_narrative.png'
    ... )
    """
    if dataset.data_vars is None or len(dataset.data_vars) == 0:
        warnings.warn("Empty dataset provided")
        return ""
    
    if narrative_type == 'before_after':
        fig = _create_before_after(dataset, variable, figsize)
    elif narrative_type == 'multi_temporal':
        fig = _create_multi_temporal(dataset, variable, figsize)
    elif narrative_type == 'change_map':
        fig = _create_change_map(dataset, variable, figsize)
    elif narrative_type == 'timeline':
        fig = _create_timeline(dataset, variable, figsize)
    else:
        warnings.warn(f"Unknown narrative type: {narrative_type}")
        return ""
    
    fig.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close(fig)
    
    return output_path


def _create_before_after(
    dataset: xr.Dataset,
    variable: str,
    figsize: Tuple[int, int]
) -> plt.Figure:
    """Create before/after comparison visualization"""
    fig, axes = plt.subplots(1, 2, figsize=figsize)
    
    if 'time' in dataset.dims and len(dataset.time) >= 2:
        # First and last time steps
        before = dataset[variable].isel(time=0)
        after = dataset[variable].isel(time=-1)
        
        before.plot(ax=axes[0], cmap='RdYlGn')
        axes[0].set_title('Before', fontsize=14, fontweight='bold')
        
        after.plot(ax=axes[1], cmap='RdYlGn')
        axes[1].set_title('After', fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    return fig


def _create_multi_temporal(
    dataset: xr.Dataset,
    variable: str,
    figsize: Tuple[int, int]
) -> plt.Figure:
    """Create multi-temporal visualization"""
    n_times = min(6, len(dataset.time)) if 'time' in dataset.dims else 1
    
    fig, axes = plt.subplots(2, 3, figsize=figsize)
    axes = axes.flatten()
    
    for i in range(n_times):
        if 'time' in dataset.dims:
            data = dataset[variable].isel(time=i)
            date_str = pd.to_datetime(str(data.time.values)).strftime('%Y')
            data.plot(ax=axes[i], cmap='RdYlGn')
            axes[i].set_title(date_str, fontsize=12, fontweight='bold')
    
    plt.tight_layout()
    return fig


def _create_change_map(
    dataset: xr.Dataset,
    variable: str,
    figsize: Tuple[int, int]
) -> plt.Figure:
    """Create change detection map"""
    fig, ax = plt.subplots(figsize=figsize)
    
    if 'time' in dataset.dims and len(dataset.time) >= 2:
        # Calculate change
        before = dataset[variable].isel(time=0)
        after = dataset[variable].isel(time=-1)
        change = after - before
        
        change.plot(ax=ax, cmap='RdBu_r', center=0)
        ax.set_title('Change in Vegetation Cover', fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    return fig


def _create_timeline(
    dataset: xr.Dataset,
    variable: str,
    figsize: Tuple[int, int]
) -> plt.Figure:
    """Create timeline visualization with spatial context"""
    fig = plt.figure(figsize=figsize)
    
    # This would include a time series plot and spatial map
    # Simplified version here
    ax = fig.add_subplot(111)
    ax.set_title('Land Clearing Timeline', fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    return fig

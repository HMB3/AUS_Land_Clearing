# Example Script: Simple Land Clearing Analysis

"""
This script demonstrates a basic workflow for analyzing land clearing
using the AUS Land Clearing package.

Run this script from the project root directory:
    python examples/simple_analysis.py
"""

from aus_land_clearing.utils import (
    load_config,
    get_study_area_bbox,
    get_time_range,
    get_data_source_info
)
from aus_land_clearing.data import load_dea_fractional_cover
from aus_land_clearing.processing import (
    extract_time_series,
    calculate_change_statistics,
    aggregate_by_period
)
from aus_land_clearing.visualization import create_time_series_plot


def main():
    """Run a simple land clearing analysis for Queensland."""
    
    print("="*60)
    print("AUS Land Clearing - Simple Analysis Example")
    print("="*60)
    
    # 1. Load configuration
    print("\n1. Loading configuration...")
    config = load_config()
    print(f"   Study area: {config['study_area']['name']}")
    print(f"   Data sources: {', '.join(config['data_sources'].keys())}")
    
    # 2. Define study parameters
    print("\n2. Defining study parameters...")
    bbox = get_study_area_bbox('queensland')
    print(f"   Queensland bbox: {bbox}")
    
    start_year, end_year = get_time_range()
    time_range = (f'{start_year}-01-01', f'{end_year}-12-31')
    print(f"   Time range: {time_range[0]} to {time_range[1]}")
    
    # 3. Get data source info
    print("\n3. Checking data source information...")
    fc_info = get_data_source_info('dea_fractional_cover')
    print(f"   Source: {fc_info['name']}")
    print(f"   Resolution: {fc_info['spatial_resolution']}")
    print(f"   Bands: {', '.join(fc_info['bands'])}")
    
    # 4. Load data (note: requires DEA setup)
    print("\n4. Loading DEA Fractional Cover data...")
    print("   Note: This requires DEA datacube configuration")
    
    try:
        fc_data = load_dea_fractional_cover(
            bbox=bbox,
            time_range=time_range,
            bands=['PV']
        )
        
        # 5. Extract time series
        print("\n5. Extracting time series...")
        pv_ts = extract_time_series(fc_data, variable='PV', method='mean')
        print(f"   Extracted {len(pv_ts)} time steps")
        
        # 6. Calculate statistics
        print("\n6. Calculating change statistics...")
        baseline = (f'{start_year}-01-01', f'{start_year+7}-12-31')
        comparison = (f'{end_year-10}-01-01', f'{end_year}-12-31')
        
        stats = calculate_change_statistics(
            fc_data,
            variable='PV',
            baseline_period=baseline,
            comparison_period=comparison
        )
        
        print(f"   Baseline mean: {stats.get('baseline_mean', 'N/A'):.2f}")
        print(f"   Comparison mean: {stats.get('comparison_mean', 'N/A'):.2f}")
        print(f"   Change: {stats.get('percent_change', 'N/A'):.2f}%")
        
        # 7. Create visualization
        print("\n7. Creating visualization...")
        output_path = 'data/outputs/simple_analysis_result.png'
        
        create_time_series_plot(
            pv_ts,
            variable='PV',
            title='Photosynthetic Vegetation - Queensland',
            ylabel='PV Cover (%)',
            output_path=output_path
        )
        
        print(f"   Saved to: {output_path}")
        
    except Exception as e:
        print(f"\n   Warning: {e}")
        print("\n   To use this script with real data:")
        print("   1. Set up DEA datacube (see docs/DATA_SOURCES.md)")
        print("   2. Configure datacube connection")
        print("   3. Run this script again")
    
    print("\n" + "="*60)
    print("Analysis complete!")
    print("="*60)
    print("\nNext steps:")
    print("  - Explore notebooks/ for more examples")
    print("  - See docs/ for detailed documentation")
    print("  - Customize config.yaml for your analysis")


if __name__ == '__main__':
    main()

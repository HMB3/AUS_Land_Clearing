#!/usr/bin/env python3
"""
Run DEA Annual Land Cover Processing

This script processes DEA annual land cover data for NSW and Queensland,
reclassifying it into woody/non-woody categories and generating time-series
outputs.

Usage:
    python scripts/run_dea_processing.py [--state nsw|qld|all] [--years YYYY-YYYY]

Examples:
    # Process all years for both states
    python scripts/run_dea_processing.py
    
    # Process only NSW
    python scripts/run_dea_processing.py --state nsw
    
    # Process specific year range
    python scripts/run_dea_processing.py --years 2020-2023
"""

import sys
import argparse
from pathlib import Path

# Add src to path and import dea_processor directly
repo_root = Path(__file__).parent.parent
sys.path.insert(0, str(repo_root / "src" / "aus_land_clearing"))

import dea_processor


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Process DEA annual land cover data for NSW and QLD',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process all years for both states
  %(prog)s
  
  # Process only NSW
  %(prog)s --state nsw
  
  # Process specific year range
  %(prog)s --years 2020-2023
  
  # Process single year
  %(prog)s --years 2020
        """
    )
    
    parser.add_argument(
        '--state',
        choices=['nsw', 'qld', 'all'],
        default='all',
        help='State to process (default: all)'
    )
    
    parser.add_argument(
        '--years',
        type=str,
        default=None,
        help='Year range to process (e.g., "2020-2023" or "2020")'
    )
    
    parser.add_argument(
        '--config',
        type=str,
        default=None,
        help='Path to config file (default: config.yaml in repo root)'
    )
    
    return parser.parse_args()


def parse_year_range(year_str):
    """
    Parse year range string.
    
    Parameters
    ----------
    year_str : str
        Year range string (e.g., "2020-2023" or "2020")
        
    Returns
    -------
    list
        List of years
    """
    if '-' in year_str:
        start, end = year_str.split('-')
        return list(range(int(start), int(end) + 1))
    else:
        return [int(year_str)]


def main():
    """Main execution function."""
    args = parse_args()
    
    print("=" * 70)
    print("DEA Annual Land Cover Processing")
    print("=" * 70)
    
    # Load config to get year range
    config = dea_processor.load_config(args.config)
    dea_config = config['dea_profile']
    
    # Determine years to process
    if args.years is not None:
        years = parse_year_range(args.years)
        print(f"\nProcessing years: {min(years)}-{max(years)}")
    else:
        years = None
        print(f"\nProcessing years: {dea_config['start_year']}-{dea_config['end_year']}")
    
    # Determine states to process
    if args.state == 'all':
        states = ['nsw', 'qld']
    else:
        states = [args.state]
    
    print(f"Processing states: {', '.join(s.upper() for s in states)}")
    print()
    
    # Check if boundary files exist
    print("Checking for boundary files...")
    missing_boundaries = []
    for state in states:
        aoi_path = dea_config['aoi_paths'].get(state)
        if aoi_path and not Path(aoi_path).exists():
            missing_boundaries.append(state)
            print(f"  ✗ {state.upper()}: {aoi_path} not found")
        else:
            print(f"  ✓ {state.upper()}: {aoi_path}")
    
    if missing_boundaries:
        print("\n⚠ Missing boundary files!")
        print("Run the following command to download state boundaries:")
        print("  python scripts/fetch_australian_state_geojson.py")
        sys.exit(1)
    
    print()
    
    # Process each state
    results = {}
    for state in states:
        try:
            print("=" * 70)
            result = dea_processor.process_dea_timeseries(
                state_code=state,
                config_path=args.config,
                years=years
            )
            results[state] = result
            
        except NotImplementedError as e:
            print("\n" + "=" * 70)
            print("⚠ DATA FETCHING NOT YET IMPLEMENTED")
            print("=" * 70)
            print(str(e))
            print("\nThis is a template implementation for sweep-1.")
            print("The data fetching backend will be implemented in sweep-2.")
            sys.exit(1)
            
        except Exception as e:
            print(f"\n✗ Error processing {state.upper()}: {e}")
            import traceback
            traceback.print_exc()
            results[state] = {'error': str(e)}
    
    # Summary
    print("\n" + "=" * 70)
    print("PROCESSING SUMMARY")
    print("=" * 70)
    
    for state, result in results.items():
        if 'error' in result:
            print(f"\n{state.upper()}: ✗ Failed - {result['error']}")
        else:
            years_proc = result.get('years_processed', [])
            print(f"\n{state.upper()}:")
            print(f"  Years processed: {len(years_proc)}")
            print(f"  Output directory: {result.get('output_dir', 'N/A')}")
            if years_proc:
                print(f"  Year range: {min(years_proc)}-{max(years_proc)}")
    
    print()


if __name__ == "__main__":
    main()

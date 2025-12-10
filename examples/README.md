# Examples

This directory contains example scripts demonstrating how to use the AUS Land Clearing package.

## Running Examples

First, install the package and dependencies:

```bash
# From project root
pip install -r requirements.txt
pip install -e .
```

Then run examples:

```bash
# Run simple analysis
python examples/simple_analysis.py
```

## Available Examples

### simple_analysis.py

A basic workflow demonstrating:
- Loading configuration
- Defining study parameters
- Accessing data sources
- Processing time series
- Creating visualizations

**Note**: Requires DEA datacube setup for actual data access.

## Example Output

When run successfully, examples will:
- Print analysis progress to console
- Save visualizations to `data/outputs/`
- Display statistics and results

## More Examples

For interactive examples with detailed explanations, see the Jupyter notebooks in the `notebooks/` directory:

- `01_data_access.ipynb`
- `02_time_series_analysis.ipynb`
- `03_visualization.ipynb`
- `04_narrative_stories.ipynb`

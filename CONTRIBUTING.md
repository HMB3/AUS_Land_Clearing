# Contributing to AUS Land Clearing

Thank you for your interest in contributing to the AUS Land Clearing project! This document provides guidelines for contributing to the project.

## How to Contribute

### Reporting Issues

If you find a bug or have a suggestion:

1. Check existing issues to avoid duplicates
2. Create a new issue with a clear title and description
3. Include:
   - Steps to reproduce (for bugs)
   - Expected vs actual behavior
   - Your environment (Python version, OS, etc.)
   - Relevant code snippets or error messages

### Suggesting Enhancements

We welcome suggestions for:
- New data sources
- Additional processing algorithms
- Visualization improvements
- Documentation enhancements
- Performance optimizations

### Pull Requests

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**
   - Follow the code style (see below)
   - Add tests if applicable
   - Update documentation

4. **Commit your changes**
   ```bash
   git commit -m "Add feature: description of feature"
   ```

5. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Open a pull request**
   - Provide a clear description
   - Reference related issues
   - Include screenshots for UI changes

## Development Setup

### Prerequisites

- Python 3.8+
- Git
- Virtual environment tool (venv, conda, etc.)

### Setup Steps

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/AUS_Land_Clearing.git
cd AUS_Land_Clearing

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -r requirements.txt
pip install -e .

# Install development dependencies
pip install pytest black flake8 mypy
```

## Code Style

### Python Code

- Follow PEP 8
- Use meaningful variable names
- Add docstrings to all functions and classes
- Use type hints where appropriate

Example:
```python
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
        Dictionary with change statistics
    """
    # Implementation here
    pass
```

### Documentation

- Use NumPy-style docstrings
- Include examples in docstrings
- Update README.md for major features
- Add or update relevant docs/*.md files

### Commit Messages

Format:
```
<type>: <subject>

<body>

<footer>
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

Example:
```
feat: Add SLATS data loader for Queensland

Implements loading of SLATS woody vegetation data for Queensland
regions. Includes support for clearing, regrowth, and extent products.

Closes #123
```

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_processing.py

# Run with coverage
pytest --cov=aus_land_clearing tests/

# Run DEA processor tests specifically
pytest tests/test_dea_processor.py -v
```

### Writing Tests

- Place tests in `tests/` directory
- Name test files `test_*.py`
- Use descriptive test names
- Test edge cases and error conditions
- For DEA processing, use mocked data to avoid external dependencies

Example:
```python
def test_extract_time_series_empty_dataset():
    """Test time series extraction with empty dataset."""
    ds = xr.Dataset()
    result = extract_time_series(ds, variable='PV')
    assert result.empty
```

### Testing DEA Processing

The DEA processor tests use mocked datacube responses to avoid requiring actual DEA credentials:

```python
# Example test structure
def test_dea_processor_reclassify():
    """Test DEA class reclassification to woody/non-woody."""
    # Mock DEA classes
    input_classes = np.array([[1, 2, 3], [4, 5, 6]])
    
    # Apply reclassification
    result = reclassify_dea_to_woody_nonwoody(input_classes)
    
    # Check output
    assert result.shape == input_classes.shape
    assert set(np.unique(result)).issubset({0, 1, 2})
```

### Adding New Data Sources

When adding support for new data sources or processing capabilities:

1. **Add configuration** to `config.yaml`:
   ```yaml
   new_data_source:
     product_id: "source_product_name"
     start_year: 1988
     end_year: 2024
     # ... other parameters
   ```

2. **Create loader function** in appropriate module:
   ```python
   # In src/aus_land_clearing/data/ or new module
   def load_new_data_source(bbox, time_range, **kwargs):
       """
       Load data from new source.
       
       Parameters
       ----------
       bbox : tuple
           Bounding box (min_lon, min_lat, max_lon, max_lat)
       time_range : tuple
           Time range (start_date, end_date)
       
       Returns
       -------
       xarray.Dataset
           Loaded data
       """
       # Implementation
       pass
   ```

3. **Add tests** with mocked responses:
   ```python
   # In tests/test_new_data_source.py
   @pytest.fixture
   def mock_data():
       """Mock data for testing."""
       return create_mock_dataset()
   
   def test_load_new_data_source(mock_data):
       """Test loading from new data source."""
       result = load_new_data_source(bbox, time_range)
       assert result is not None
   ```

4. **Update documentation**:
   - Add to `docs/DATA_SOURCES.md`
   - Add example to notebooks
   - Update README.md

5. **Create example script** in `scripts/` if appropriate

### Adding Processing Functions

When adding new processing capabilities:

1. **Create well-documented function**:
   ```python
   def new_processing_function(
       data: xr.Dataset,
       param1: str,
       param2: int = 10
   ) -> xr.Dataset:
       """
       Brief description of what this function does.
       
       Parameters
       ----------
       data : xarray.Dataset
           Input dataset
       param1 : str
           Description of param1
       param2 : int, optional
           Description of param2, by default 10
       
       Returns
       -------
       xarray.Dataset
           Processed dataset
           
       Examples
       --------
       >>> ds = load_data()
       >>> result = new_processing_function(ds, 'value')
       """
       # Implementation
       pass
   ```

2. **Add comprehensive tests**:
   - Test with valid inputs
   - Test with edge cases
   - Test error handling
   - Test with different data types

3. **Add to module exports**:
   ```python
   # In module __init__.py
   from .module import new_processing_function
   
   __all__ = ['new_processing_function', ...]
   ```

4. **Document in notebook** with example usage

### Data Quality Checks

When processing external data sources, include quality checks:

```python
def validate_dea_data(ds: xr.Dataset) -> bool:
    """
    Validate DEA data quality.
    
    Checks:
    - Data arrays are not empty
    - CRS information is present
    - Time dimension is valid
    - No excessive missing data
    """
    if len(ds.data_vars) == 0:
        raise ValueError("Dataset is empty")
    
    if 'time' not in ds.dims:
        raise ValueError("Missing time dimension")
    
    # Additional checks...
    return True
```

## Code Review Process

1. All changes require review before merging
2. Address reviewer feedback
3. Keep discussions respectful and constructive
4. Reviewers check for:
   - Code quality and style
   - Test coverage
   - Documentation updates
   - Performance implications

## Project Structure

```
AUS_Land_Clearing/
├── src/aus_land_clearing/    # Main package
│   ├── data/                 # Data access modules
│   ├── processing/           # Processing algorithms
│   ├── visualization/        # Visualization tools
│   └── utils/                # Utilities
├── tests/                    # Test suite
├── notebooks/                # Example notebooks
├── examples/                 # Example scripts
├── docs/                     # Documentation
└── data/                     # Data directories
```

## Adding New Features

### Adding a Data Source

1. Create loader function in `src/aus_land_clearing/data/loader.py`
2. Add configuration in `config.yaml`
3. Update `docs/DATA_SOURCES.md`
4. Add example in notebooks
5. Update README.md

### Adding a Processing Function

1. Add function to appropriate module in `src/aus_land_clearing/processing/`
2. Include comprehensive docstring
3. Add to module's `__init__.py`
4. Create example in notebook
5. Write tests

### Adding a Visualization

1. Add function to `src/aus_land_clearing/visualization/plots.py`
2. Include parameters for customization
3. Add example output to documentation
4. Create demonstration in notebook

## Documentation

### Building Documentation

```bash
# Install documentation dependencies
pip install sphinx sphinx-rtd-theme

# Build documentation
cd docs
make html
```

### Documentation Standards

- Clear, concise explanations
- Include code examples
- Add screenshots for visualizations
- Keep examples up-to-date
- Cross-reference related topics

## Performance Considerations

- Profile code for bottlenecks
- Use appropriate data structures
- Consider memory usage for large datasets
- Document computational complexity
- Use Dask for parallel processing where appropriate

## Security

- Don't commit credentials or API keys
- Use environment variables for sensitive data
- Validate user inputs
- Document security considerations

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Questions?

- Open an issue for questions
- Tag with "question" label
- Provide context for your question

## Recognition

Contributors will be acknowledged in:
- README.md (major contributions)
- Release notes
- Git commit history

Thank you for contributing to AUS Land Clearing! 🌏🌳

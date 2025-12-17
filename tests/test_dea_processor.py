"""
Unit Tests for DEA Processor Module

Tests for the DEA annual landcover processing functions using mocked data
to avoid external dependencies on datacube or STAC services.

Run with:
    pytest tests/test_dea_processor.py -v
    pytest tests/test_dea_processor.py::test_reclassify -v
"""

import tempfile
from pathlib import Path

import numpy as np
import pytest
import xarray as xr

# Import functions to test
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from aus_land_clearing.dea_processor import (
    load_dea_config,
    reclassify_dea_to_woody_nonwoody,
    _create_mock_dea_data
)


@pytest.fixture
def mock_config_file(tmp_path):
    """Create a mock config file for testing."""
    config_content = """
dea_annual_landcover:
  product_id: "ga_ls_landcover_class_cyear_2"
  start_year: 2000
  end_year: 2020
  crs: "EPSG:3577"
  resolution: 25
  output_dir: "data/outputs/dea_landcover"
  aoi_paths:
    nsw: "data/nsw.geojson"
    qld: "data/qld.geojson"
  classes_map:
    woody:
      - 2
    non_woody:
      - 1
      - 3
    other:
      - 0
      - 4
      - 5
      - 6
  stac:
    catalog_url: "https://explorer.dea.ga.gov.au/stac"
  processing:
    buffer_distance: 0
    chunk_size: 2048
    nodata_value: 255
  animation:
    fps: 2
    loop: 0
"""
    config_file = tmp_path / "test_config.yaml"
    config_file.write_text(config_content)
    return config_file


@pytest.fixture
def mock_dea_data():
    """Create mock DEA landcover data."""
    # Create synthetic data
    bounds = (140.0, -38.0, 141.0, -37.0)
    data = _create_mock_dea_data(
        bounds=bounds,
        start_year=2000,
        end_year=2005,
        resolution=100,
        crs='EPSG:3577'
    )
    return data


@pytest.fixture
def sample_landcover_array():
    """Create sample landcover array for testing."""
    # Create array with known class distribution
    # 0=nodata, 1=crops, 2=woody, 3=wetland, 4=urban, 5=bare, 6=water
    arr = np.array([
        [0, 1, 2, 3],
        [4, 5, 6, 2],
        [1, 1, 2, 2],
        [3, 3, 0, 0]
    ], dtype=np.uint8)
    return arr


def test_load_config(mock_config_file):
    """Test loading DEA configuration from YAML."""
    config = load_dea_config(mock_config_file)
    
    assert config is not None
    assert 'product_id' in config
    assert config['product_id'] == 'ga_ls_landcover_class_cyear_2'
    assert config['start_year'] == 2000
    assert config['end_year'] == 2020
    assert config['resolution'] == 25


def test_load_config_missing_file():
    """Test loading config with non-existent file."""
    with pytest.raises(FileNotFoundError):
        load_dea_config('nonexistent_config.yaml')


def test_reclassify_numpy_array(sample_landcover_array):
    """Test reclassification with numpy array."""
    result = reclassify_dea_to_woody_nonwoody(sample_landcover_array)
    
    # Check output type
    assert isinstance(result, np.ndarray)
    assert result.dtype == np.uint8
    
    # Check output shape matches input
    assert result.shape == sample_landcover_array.shape
    
    # Check only valid output classes (0, 1, 2)
    unique_classes = np.unique(result)
    assert set(unique_classes).issubset({0, 1, 2})
    
    # Check specific reclassifications based on default mapping
    # Class 2 (woody) -> 1
    assert result[0, 2] == 1
    assert result[1, 3] == 1
    
    # Class 1, 3 (non-woody) -> 2
    assert result[0, 1] == 2  # crops
    assert result[0, 3] == 2  # wetland
    
    # Class 0, 4, 5, 6 (other) -> 0
    assert result[0, 0] == 0  # nodata
    assert result[1, 0] == 0  # urban
    assert result[1, 1] == 0  # bare
    assert result[1, 2] == 0  # water


def test_reclassify_with_custom_mapping(sample_landcover_array):
    """Test reclassification with custom class mapping."""
    custom_map = {
        'woody': [2, 3],  # Include wetland as woody
        'non_woody': [1],  # Only crops
        'other': [0, 4, 5, 6]
    }
    
    result = reclassify_dea_to_woody_nonwoody(sample_landcover_array, custom_map)
    
    # With custom mapping, class 3 should be woody (1)
    assert result[0, 3] == 1
    assert result[3, 0] == 1


def test_reclassify_xarray_dataarray():
    """Test reclassification with xarray DataArray."""
    # Create DataArray
    data = np.array([
        [[1, 2], [3, 4]],
        [[2, 1], [4, 5]]
    ], dtype=np.uint8)
    
    da = xr.DataArray(
        data,
        coords={
            'time': ['2000-01-01', '2001-01-01'],
            'y': [0, 1],
            'x': [0, 1]
        },
        dims=['time', 'y', 'x']
    )
    
    result = reclassify_dea_to_woody_nonwoody(da)
    
    # Check output is DataArray
    assert isinstance(result, xr.DataArray)
    
    # Check coordinates preserved
    assert 'time' in result.coords
    assert 'y' in result.coords
    assert 'x' in result.coords
    
    # Check values
    assert set(np.unique(result.values)).issubset({0, 1, 2})


def test_reclassify_xarray_dataset(mock_dea_data):
    """Test reclassification with xarray Dataset."""
    result = reclassify_dea_to_woody_nonwoody(mock_dea_data)
    
    # Check output is DataArray
    assert isinstance(result, xr.DataArray)
    
    # Check coordinates
    assert 'time' in result.coords
    assert 'x' in result.coords
    assert 'y' in result.coords
    
    # Check only valid classes
    unique_classes = np.unique(result.values)
    assert set(unique_classes).issubset({0, 1, 2})


def test_mock_dea_data_structure():
    """Test the structure of mock DEA data."""
    bounds = (140.0, -38.0, 141.0, -37.0)
    data = _create_mock_dea_data(
        bounds=bounds,
        start_year=2010,
        end_year=2015,
        resolution=50,
        crs='EPSG:4326'
    )
    
    # Check it's a Dataset
    assert isinstance(data, xr.Dataset)
    
    # Check dimensions
    assert 'time' in data.dims
    assert 'x' in data.dims
    assert 'y' in data.dims
    
    # Check time dimension
    assert len(data.time) == 6  # 2010-2015 inclusive
    
    # Check data variable exists
    assert 'landcover_class' in data.data_vars
    
    # Check attributes
    assert 'crs' in data.attrs
    assert data.attrs['crs'] == 'EPSG:4326'


def test_mock_data_bounds():
    """Test that mock data respects spatial bounds."""
    bounds = (150.0, -30.0, 151.0, -29.0)
    data = _create_mock_dea_data(
        bounds=bounds,
        start_year=2020,
        end_year=2020,
        resolution=100,
        crs='EPSG:3577'
    )
    
    x = data.x.values
    y = data.y.values
    
    # Check x coordinates within bounds
    assert x.min() >= bounds[0]
    assert x.max() <= bounds[2]
    
    # Check y coordinates within bounds
    assert y.min() >= bounds[1]
    assert y.max() <= bounds[3]


def test_reclassify_all_classes():
    """Test that all DEA classes are handled correctly."""
    # Test with all possible DEA classes (0-6)
    all_classes = np.arange(0, 7, dtype=np.uint8).reshape(1, -1)
    
    result = reclassify_dea_to_woody_nonwoody(all_classes)
    
    # Expected mapping (default):
    # 0 -> 0 (other)
    # 1 -> 2 (non-woody crops)
    # 2 -> 1 (woody)
    # 3 -> 2 (non-woody wetland)
    # 4 -> 0 (other urban)
    # 5 -> 0 (other bare)
    # 6 -> 0 (other water)
    
    expected = np.array([[0, 2, 1, 2, 0, 0, 0]], dtype=np.uint8)
    np.testing.assert_array_equal(result, expected)


def test_reclassify_empty_array():
    """Test reclassification with empty array."""
    empty = np.array([], dtype=np.uint8)
    result = reclassify_dea_to_woody_nonwoody(empty)
    
    assert result.shape == empty.shape
    assert len(result) == 0


def test_class_distribution():
    """Test that reclassification preserves spatial patterns."""
    # Create array with distinct regions
    arr = np.ones((10, 10), dtype=np.uint8)
    arr[:5, :] = 2  # Top half woody
    arr[5:, :] = 1  # Bottom half non-woody
    
    result = reclassify_dea_to_woody_nonwoody(arr)
    
    # Check top half is woody (1)
    assert np.all(result[:5, :] == 1)
    
    # Check bottom half is non-woody (2)
    assert np.all(result[5:, :] == 2)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

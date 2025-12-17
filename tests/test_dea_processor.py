"""
Unit tests for DEA processor module.

Tests the reclassification logic for converting DEA land cover classes
to woody/non-woody categories.
"""

import numpy as np
import pytest
import sys
from pathlib import Path

# Add src to path and import dea_processor directly
repo_root = Path(__file__).parent.parent
sys.path.insert(0, str(repo_root / "src" / "aus_land_clearing"))

import dea_processor


class TestReclassifyDEAClasses:
    """Test suite for DEA class reclassification."""
    
    def test_simple_reclassification(self):
        """Test basic woody/non-woody reclassification."""
        # Input data with DEA class IDs
        data = np.array([[111, 124], [214, 215]])
        
        # Classes map
        classes_map = {
            'woody': [111, 124],
            'non_woody': [214, 215]
        }
        
        # Expected output: woody=1, non-woody=0
        expected = np.array([[1, 1], [0, 0]], dtype=np.float32)
        
        result = dea_processor.reclassify_dea_classes(data, classes_map)
        
        np.testing.assert_array_equal(result, expected)
    
    def test_mixed_classes(self):
        """Test reclassification with mixed woody and non-woody classes."""
        data = np.array([[111, 214], [124, 215], [112, 216]])
        
        classes_map = {
            'woody': [111, 112, 124],
            'non_woody': [214, 215, 216]
        }
        
        expected = np.array([[1, 0], [1, 0], [1, 0]], dtype=np.float32)
        
        result = dea_processor.reclassify_dea_classes(data, classes_map)
        
        np.testing.assert_array_equal(result, expected)
    
    def test_unknown_classes_as_nan(self):
        """Test that unknown classes are set to NaN."""
        data = np.array([[111, 999], [124, 888]])
        
        classes_map = {
            'woody': [111, 124],
            'non_woody': [214, 215]
        }
        
        result = dea_processor.reclassify_dea_classes(data, classes_map)
        
        # Check that known classes are correct
        assert result[0, 0] == 1
        assert result[1, 0] == 1
        
        # Check that unknown classes are NaN
        assert np.isnan(result[0, 1])
        assert np.isnan(result[1, 1])
    
    def test_large_array(self):
        """Test reclassification with larger array."""
        # Create a larger test array
        data = np.random.choice([111, 124, 214, 215], size=(100, 100))
        
        classes_map = {
            'woody': [111, 124],
            'non_woody': [214, 215]
        }
        
        result = dea_processor.reclassify_dea_classes(data, classes_map)
        
        # Check output shape matches input
        assert result.shape == data.shape
        
        # Check that all values are either 0, 1, or NaN
        valid_mask = ~np.isnan(result)
        assert np.all((result[valid_mask] == 0) | (result[valid_mask] == 1))
    
    def test_empty_classes_map(self):
        """Test behavior with empty classes map."""
        data = np.array([[111, 124], [214, 215]])
        
        classes_map = {
            'woody': [],
            'non_woody': []
        }
        
        result = dea_processor.reclassify_dea_classes(data, classes_map)
        
        # All values should be NaN
        assert np.all(np.isnan(result))
    
    def test_only_woody_classes(self):
        """Test with only woody classes defined."""
        data = np.array([[111, 124], [214, 215]])
        
        classes_map = {
            'woody': [111, 124],
            'non_woody': []
        }
        
        result = dea_processor.reclassify_dea_classes(data, classes_map)
        
        # Woody classes should be 1, others NaN
        assert result[0, 0] == 1
        assert result[0, 1] == 1
        assert np.isnan(result[1, 0])
        assert np.isnan(result[1, 1])
    
    def test_only_non_woody_classes(self):
        """Test with only non-woody classes defined."""
        data = np.array([[111, 124], [214, 215]])
        
        classes_map = {
            'woody': [],
            'non_woody': [214, 215]
        }
        
        result = dea_processor.reclassify_dea_classes(data, classes_map)
        
        # Non-woody classes should be 0, others NaN
        assert np.isnan(result[0, 0])
        assert np.isnan(result[0, 1])
        assert result[1, 0] == 0
        assert result[1, 1] == 0
    
    def test_dtype_preservation(self):
        """Test that output dtype is float32."""
        data = np.array([[111, 124]], dtype=np.int32)
        
        classes_map = {
            'woody': [111, 124],
            'non_woody': []
        }
        
        result = dea_processor.reclassify_dea_classes(data, classes_map)
        
        assert result.dtype == np.float32


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

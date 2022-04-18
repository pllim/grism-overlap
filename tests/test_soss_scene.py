"""
Tests for soss_scene.py module
"""
import numpy as np

from grism_overlap import soss_scene as sc


def test_soss_scene():
    """Test soss_scene function"""
    # Correct data shape
    good_scene = np.ones((4231, 4231))
    bad_scene = np.ones((100, 200))

    # Returns None if wrong shape
    assert sc.soss_scene(bad_scene) is None

    # Return scene is correct shape
    assert sc.soss_scene(good_scene).shape == (2322, 2322)


def test_get_gr700_psf():
    """Test get_gr700_psf function"""
    assert sc.get_gr700_psf().shape == (8192, 8192)
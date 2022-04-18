"""
Tests for wfss_scene.py module
"""
import numpy as np

from grism_overlap import wfss_scene as sc


def test_wfss_scene():
    """Test wfss_scene function"""
    # Valid filters and grisms
    grisms = ['GR150R', 'GR150C']
    filters = ['F090W', 'F115W', 'F140M', 'F150W', 'F158M', 'F200W']

    # Valid offsets
    x0, y0 = 0, 0

    # Correct data shape
    good_scene = np.ones((4231, 4231))
    bad_scene = np.ones((100, 200))

    # Returns None if wrong shape
    assert sc.wfss_scene(bad_scene, filters[0], grisms[0], x0, y0) is None

    # Returns None if bad filter or grism name
    assert sc.wfss_scene(good_scene, 'foobar', grisms[0], x0, y0) is None
    assert sc.wfss_scene(good_scene, filters[0], 'foobar', x0, y0) is None

    # Returns None if bad offsets
    bad_offsets = [[-10, -10], [0, -10], [-10, 0], [10000, 0], [0, 10000], [10000, 10000]]
    for x, y in bad_offsets:
        assert sc.wfss_scene(good_scene, filters[0], grisms[0], x, y) is None

    # Good grism+filter combos
    for grism in grisms:
        for filter in filters:
            assert sc.wfss_scene(good_scene, filter, grism, x0, y0).shape == (2322, 2322)

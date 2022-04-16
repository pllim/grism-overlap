"""
Tests for soss_scene.py module
"""
from pkg_resources import resource_filename

from grism_overlap import scene_image as si


def test_make_star_image():
    """Test of the make_star_image function"""
    # Get the input
    file = resource_filename('grism_overlap', 'grism_overlap/files/stars_bd60d1753_gaiadr3_allfilters.txt')
    pos = 	261.21781401047, 60.43076384536

    # Valid filters
    filters = ['F090W', 'F115W', 'F140M', 'F150W', 'F158M', 'F200W', 'F277W', 'F356W', 'F380M', 'F430M', 'F444W', 'F480M']

    # Bad file
    scene, stars = si.make_star_image('foo/bar.txt', pos, filters[0])
    assert scene is None
    assert all([i is None for i in stars])

    # Bad filter
    scene, stars = si.make_star_image(file, pos, 'foobar')
    assert scene is None
    assert all([i is None for i in stars])

    # Good filters
    for n, filt in enumerate(filters):
        scene, stars = si.make_star_image(file, pos, filt)
        if n <= 5:
            assert scene is not None
            assert all([i is not None for i in stars])
        else:
            assert scene is None
            assert all([i is None for i in stars])


def test_make_galaxy_image():
    """Test of make_galaxy_image function"""
    # Get the input
    file = resource_filename('grism_overlap', 'files/stars_bd60d1753_gaiadr3_allfilters.txt')
    pos = 	261.21781401047, 60.43076384536

    # Valid filters
    filters = ['F090W', 'F115W', 'F140M', 'F150W', 'F158M', 'F200W', 'F277W', 'F356W', 'F380M', 'F430M', 'F444W', 'F480M']

    # Bad file
    scene = si.make_galaxy_image('foo/bar.txt', pos, filters[0])
    assert scene is None

    # Bad filter
    scene = si.make_galaxy_image(file, pos, 'foobar')
    assert scene is None

    # Good filters
    for n, filt in enumerate(filters):
        scene = si.make_galaxy_image(file, pos, filt)
        if n <= 5:
            assert scene.shape == (4231, 4231)
        else:
            assert scene is None

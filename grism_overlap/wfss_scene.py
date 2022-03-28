"""
The code here takes a scene image and convolves with the NIRISS WFSS "PSF"
image to produce a simulated dispersed scene.
"""
import numpy
from astropy.io import fits
from scipy import signal


def wfss_scene(scene_image, filtername, grismname, x0, y0, psffile=None, throughput=0.8):
    """
    Convolve a scene image with the WFSS PSF and return dispersed image over
    the 2322x2322 pixel POM image area. The scene image is multiplied by the spot
    mask before the convolution in the area that corresponds to the output pixels.

    Parameters
    ----------
    scene_image: sequence
        A 2322x2322 imaging scene to disperse
    filtername: str
       A WFSS blocking filter name
    grimsname: str
        The NIRISS GR150 grism name, either 'GR150R' or 'GR150C'
    x0: int
        The lower left corner x pixel value for the POM image read-out area
    y0: int
        The lower left corner y pixel value for the POM image read-out area
    psffile: str
        The path to alternate WFSS PSF images
    throughput: float
        The grism throughput

    Returns
    -------
    outimage: np.ndarray, None
        The dispersed 2322x2322 scene
    """
    # Valid grisms and filters
    grisms = ['GR150R', 'GR150C']
    filters = ['F090W', 'F115W', 'F140M', 'F150W', 'F158M', 'F200W']
    if not grismname.upper() in grisms:
        print('Error: bad grism name %s passed to wfss_scene'.format(grismname))
        return None
    if not filtername.upper() in filters:
        print('Error: bad grism name %s passed to wfss_scene'.format(filtername))
        return None

    # Check data shape
    imshape = scene_image.shape
    if (x0 < 0) or (y0 < 0) or (x0 + 2322 > imshape[1]) or (y0 + 2322 > imshape[0]):
        print('Error in wfss_scene: bad image offset values' + \
              '(%d, %d) passed to the routine.'.format(x0, y0))
        return None

    # Get the spot mask data
    spotpath = resource_filename('grism_overlap', 'files/occulting_spots_mask.fits')
    spotmask = fits.getdata(spotpath)

    # Get the psf image
    if psffile is None:
        psffile = resource_filename('grism_overlap', 'files/{}_{}_psfimage.fits'.format(filtername, grismname).lower())
    psfimage = fits.getdata(psffile)

    # Make the final image
    field_image = numpy.copy(scene_image[y0:y0 + 2322, x0:x0 + 2322])
    y1 = y0 + 137
    x1 = x0 + 137
    field_image[y1:y1 + 2048, x1:x1 + 2048] = field_image[y1:y1 + 2048, x1:x1 + 2048] * spotmask

    # Convolve with the psf with the field
    newimage = signal.fftconvolve(field_image, psfimage, mode='same')

    return newimage * throughput

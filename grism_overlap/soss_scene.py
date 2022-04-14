"""
The code here takes a scene image and convolves with the NIRISS SOSS "PSF"
image to produce a simulated dispersed scene.
"""
from glob import glob
from pkg_resources import resource_filename

from astropy.io import fits
import numpy as np
from scipy import signal


def soss_scene(scene_image, sossoffset=True, psffile=None, throughput=0.8):
    """
    Convolve a scene image with the SOSS PSF and return dispersed image over
    the 2322x2322 pixel POM image area. The scene image is multiplied by the
    spot mask before the convolution in the area that corresponds to the output pixels.

    Parameters
    ----------
    scene_image: sequence
        A numpy 2-d image (float) of an imaging scene to disperse.
        Must be the full 4231x4231 pixel work scene image
    sossoffset: bool
        Offset the reference position to the SOSS acquisition position or not
    psffile: str
        An alternate path to the SOSS PSF image
    throughput: float
        The grism throughput value

    Returns
    -------
    outimage: np.ndarray
         The dispersed 2322x2322 scene
    """
    imshape = scene_image.shape
    if (imshape[0] != 4231) or (imshape[1] != 4231):
        print('Error in soss_scene: wrong size image (%d, %d) passed to the routine.' % (imshape[1], imshape[0]))
        return None

    # Get the spot mask data
    spotpath = resource_filename('grism_overlap', 'grism_overlap/files/occulting_spots_mask.fits')
    spotmask = fits.getdata(spotpath)

    # Get the psf image
    if psffile is not None:
        psfimage = fits.getdata(psffile)
    else:
        psfimage = get_gr700_psf()

    # Check for offset
    if not sossoffset:
        new_image = scene_image
    else:
        new_image = scene_image * 0.
        new_image[174:, 930:] = scene_image[0:4057, 0:3301]

    # Make the final image
    field_image = np.copy(new_image[955:3277, 955:3277])
    y1 = 137
    x1 = 137
    field_image[y1:y1 + 2048, x1:x1 + 2048] = field_image[y1:y1 + 2048, x1:x1 + 2048] * spotmask

    # Convolve with the psf with the field
    outimage = signal.fftconvolve(field_image, psfimage, mode='same')

    return outimage * throughput


def get_gr700_psf(files=None):
    """
    Retrieve SOSS psf pieces and stitch them together into one 8192x8192 frame

    Parameters
    ----------
    file: str
        The path to the files to stitch

    Returns
    -------
    np.ndarray
        The SOSS psf frame
    """
    if files is None:
        files = sorted(glob(resource_filename('grism_overlap', 'grism_overlap/files/gr700xd_psfimage*')))

    # Combine files into one image
    fullframe = np.concatenate([np.load(file) for file in files], axis=0)

    return fullframe


def save_gr700_psf(psfname, nfiles=16):
    """
    Parameters
    ----------
    fits_file: str
        The path to the large 8192x8192 frame FITS data
    nfiles: int
        The number of files to split the data into
    """
    # Read the data from the FITS file
    psfimage = fits.getdata(psfname)

    # Chop it up into parts and save locally
    filename = resource_filename('grism_overlap', 'grism_overlap/files/gr700xd_psfimage*.npy')
    ydim = int(8192 / 16)
    for filenum in range(nfiles):
        fname = filename.replace('*', '{:02d}'.format(filenum))
        np.save(fname, psfimage[ydim * filenum:ydim * (1 + filenum), :])

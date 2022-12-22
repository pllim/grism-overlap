#! /usr/bin/env python
#
"""
Tool to access the possibility of overlap of spectra for a field of view.

This code takes as input either a pair or Mirage source input files (one for
stars and one for galaxies) or a scene image made from such input files and
allows the user to investigate the resulting scene at arbitrary rotations
to determine if spectral order overlap will be an issue for any given source
in the field.

"""
import os
from functools import partial
from pkg_resources import resource_filename
from multiprocessing.pool import ThreadPool
from multiprocessing import cpu_count
import time
import sys

from astropy.table import vstack
from bokeh.plotting import show
from bokeh.models import LabelSet, ColumnDataSource, Patch
from hotsoss.plotting import plot_frame
from mirage.catalogs import create_catalog as cc
from mirage.catalogs import catalog_generator as cg
import numpy as np

from . import scene_image as si
from . import soss_scene as ss


def grism_overlap_soss_contam(ra, dec, subarray='SUBSTRIP256', skip_PA=10, plot=True, **kwargs):
    """
    Generate a contamination figure for all PA values for given coordinates

    Parameters
    ----------
    ra: float
        The RA in decimal degrees
    dec: float
        The Declination in decimal degrees

    Returns
    -------
    np.ndarray
        The contamination figure
    """
    start = time.time()
    print('Starting contam calculation...')

    # Make a scene of only the target
    targ_frame = grism_overlap_soss(ra, dec, 0, exclude=np.arange(2, 1000), subarray=subarray, plot=False, **kwargs)

    # Prepare the scene without the target
    scene_image, star_table = prepare_scene(ra, dec, exclude=[0, 1], **kwargs)

    # Exclude PAs where target is not visible to speed up calculation
    minPA, maxPA, _, _, _, badPAs = using_gtvt(ra, dec, instrument='NIRISS')
    pa_list = [pa for pa in np.arange(0, 360, skip_PA) if pa not in badPAs]

    # Generate the contamination at each PA (skip some and interpolate for speed)
    pool = ThreadPool(cpu_count())
    func = partial(rotate_disperse_trim, scene_image=scene_image, subarray=subarray, star_table=star_table)
    results = pool.map(func, pa_list)
    pool.close()
    pool.join()
    del pool

    # Add all star locations to star table
    star_table_final = vstack([i[1] for i in results])

    # Sum along y-axis to make a plot of wavelength (x-axis) vs. PA
    contam_frames = np.array([i[0] for i in results])
    contam_final = np.nansum(contam_frames, axis=1)

    print('Finished: {}'.format(round(time.time() - start, 3), 's'))

    # if plot:
    #     show(plot_frame(final))

    return contam_frames, targ_frame, star_table_final

def rotate_disperse_trim(pa, scene_image, subarray, star_table, angle=None, psffile=None):
    """
    Rotate, disperse, and trim the scene image for the given PA

    Parameters
    ----------
    pa: float
        The position angle in degrees
    scene_image: np.ndarray
        The oversized scene image of point sources
    subarray: str
        The subarray, ['FULL', 'SUBSTRIP256', 'SUBSTRIP96']
    star_table: astropy.table.Table
        The table of sources

    Returns
    -------
    newimage, star_table
        The rotated, dispersed, and trimmed scene and the modified table of sources
    """
    print('Generating dispersed image at PA={}'.format(pa))

    # Rotate to the desired PA
    rotated_image = si.rotate_image(scene_image, pa)

    # Generate the GR700XD dispersed image from the rotated scene
    dispersed_image = ss.soss_scene(rotated_image, sossoffset=True, angle=angle, psffile=psffile)
    fov = np.zeros_like(rotated_image)
    fov[955:3277, 955:3277] = dispersed_image

    # Trim to appropriate size
    newimage = np.copy(fov)
    if subarray in ['FULL', 'SUBSTRIP256', 'SUBSTRIP96']:
        newimage = newimage[1092:3140, 1092:3140]
        star_table['xloc'] -= 1092
        star_table['yloc'] -= 1092
    if subarray in ['SUBSTRIP96', 'SUBSTRIP256']:
        newimage = newimage[-256:, :]
        star_table['xloc'] -= 1792
        star_table['yloc'] -= 1792
    if subarray == 'SUBSTRIP96':
        newimage = newimage[:96, :]

    # Add PA to star table
    star_table['PA'] = pa

    return newimage, star_table


def grism_overlap_soss(ra, dec, pa, old=False, exclude=None, starname=None, source_file=None, background=0.1, angle=None, psffile=None, subarray='SUBSTRIP256', plot=True, simple=False, **kwargs):
    """
    Generate contamination image for SOSS mode without using GUI

    Parameters
    ----------
    ra: float
       The RA of the field
    def: float
        The DEC of the field
    pa: float
        The position angle of the field, [0, 360]
    source_file: str
        A source file to use
    background: float
        The background level

    Returns
    -------
    np.ndarray
        The final contamination image
    """
    # Prepare the scene
    scene_image, star_table = prepare_scene(ra, dec, old=old, exclude=exclude, starname=starname, source_file=source_file, background=background, simple=simple)

    # Rotate and trim scene
    newimage, star_table = rotate_disperse_trim(pa, scene_image, subarray, star_table, angle=angle, psffile=psffile)

    # Plot
    if plot:

        fig = plot_frame(newimage, tabs=False, **kwargs)
        # source = ColumnDataSource(data=dict(star_table))
        # labels = LabelSet(x='xloc', y='yloc', text='name', x_offset=0, y_offset=0, source=source, render_mode='canvas', text_color='red')
        # fig.add_layout(labels)
        show(fig)

        print(star_table[['name', 'xloc', 'yloc', 'niriss_f200w_magnitude', 'flux', 'distance']])

    return newimage


def prepare_scene(ra, dec, old=False, exclude=None, starname=None, source_file=None, background=0.1, simple=False):
    """
    Generate contamination image for SOSS mode without using GUI

    Parameters
    ----------
    ra: float
       The RA of the field
    def: float
        The DEC of the field
    pa: float
        The position angle of the field, [0, 360]
    source_file: str
        A source file to use
    background: float
        The background level

    Returns
    -------
    np.ndarray
        The final contamination image
    """
    # Name for target
    starname = starname or '{}_{}.txt'.format(ra, dec)

    if source_file is None:

        # See if file is already generated
        if not os.path.exists(starname):

            # Make the PSC for these coordinates
            tab = cg.PointSourceCatalog(ra=[ra], dec=[dec])
            filters = ['F277W', 'F356W', 'F380M', 'F430M', 'F444W', 'F480M', 'F090W', 'F115W', 'F158M', 'F140M', 'F150W', 'F200W']
            cats, filter_names = cc.get_all_catalogs(ra, dec, 250, instrument='niriss', filters=filters)
            tab.add_catalog(cats)
            tab.table.write(starname, format='ascii', overwrite=True)

        source_file = starname

    print("Using source file {}".format(source_file))

    # Make the star image
    if old:
        stars_image, star_table = si.make_star_image(source_file, (ra, dec), filter1='F200W')
    else:
        stars_image, star_table = si.make_star_image_and_table(source_file, (ra, dec), filter1='F200W', exclude=exclude, simple=simple)

    # TODO: Make galaxy image
    galaxy_image = np.zeros_like(stars_image)

    # Combine star and galaxy images
    scene_image = stars_image + galaxy_image + background

    return scene_image, star_table


def disperse_image(work_image, image_option=1, sossoffset=False, display_option=-1, subarray='FULL'):
    """
    Take a rotated unconvolved image and make the output image requested.

    Parameters
    ----------
    work_image:   np.ndarray
        The image to disperse, [4031, 4031]

    Returns
    -------
    np.ndarray
        The dispersed image
    """
    if image_option == 0:
        dispersed_image = ss.soss_scene(work_image, sossoffset)
        big_image = work_image * 0.
        big_image[955:3277, 955:3277] = dispersed_image
        extracted = big_image
    elif image_option == 1:
        dispersed_image = ss.soss_scene(work_image, sossoffset)
        big_image = work_image * 0.
        big_image[955:3277, 955:3277] = dispersed_image
        extracted = extract_image(big_image, display_option, subarray=subarray)
    else:
        extracted = extract_image(work_image, display_option)

    return extracted


def extract_image(work_image, display_option, subarray='FULL'):
    """
    Extract the image are according the typevar value, and set the
    image display to this area.

    Parameters
    ----------
    work_image:   a scene image, numpy 2-d float array 3631x3631 pixels
    """
    if display_option == 0:
        newimage = work_image
    elif display_option == 1:
        newimage = work_image[955:3277, 955:3277]
    else:
        newimage = work_image[1092:3140, 1092:3140]

    if subarray in ['SUBSTRIP96', 'SUBSTRIP256']:
        newimage = newimage[-256:, :]
    if subarray == 'SUBSTRIP96':
        newimage = newimage[:96, :]

    return newimage

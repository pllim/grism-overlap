#!/usr/bin/env python
import os
from setuptools import setup, find_packages

REQUIRES = ['tkinter', 'numpy', 'scipy', 'matplotlib', 'pysiaf', 'astropy']

FILES = []
for root, _, files in os.walk("grism_overlap"):
    FILES += [os.path.join(root.replace("grism_overlap/", ""), fname)
              for fname in files if not fname.endswith(".py") and not fname.endswith(".pyc")]

setup(
    name='grism_overlap',
    version='0.1',
    description='A tool to allow evaluation of of which telescope orientations may cause overlap for the NIRISS slitless spectroscopy modes',
    packages=find_packages(
        ".",
        exclude=["*.tests"]),
    package_data={
        'exoctk': FILES},
    install_requires=REQUIRES,
    author='Kevin Volk',
    license='MIT',
    url='https://github.com/KevinVolkSTScI/grism_overlap',
    long_description='',
    zip_safe=True,
    use_2to3=False)
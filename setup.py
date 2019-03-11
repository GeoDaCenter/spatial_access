import sys, os
from setuptools.extension import Extension
from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

ouff_mac = []
extra_dependency = []
if sys.platform == "darwin":
    ouff_mac = ['-mmacosx-version-min=10.9']
    extra_dependency = ['rtree>=0.8.3']

EXTENSION = [Extension(
    name = 'transitMatrixAdapterSxS', language = 'c++',
    sources = ['spatial_access/transitMatrixAdapterSxS.cpp'],
    extra_compile_args = ['--std=c++11', '-Wall', '-O3'
                          ] + ouff_mac,
    undef_macros       = ["NDEBUG"],
    extra_link_args    = ouff_mac
    ),Extension(
    name = 'transitMatrixAdapterIxI', language = 'c++',
    sources = ['spatial_access/transitMatrixAdapterIxI.cpp'],
    extra_compile_args = ['--std=c++11', '-Wall', '-O3'
                          ] + ouff_mac,
    undef_macros       = ["NDEBUG"],
    extra_link_args    = ouff_mac
    ),Extension(
    name = 'transitMatrixAdapterSxI', language = 'c++',
    sources = ['spatial_access/transitMatrixAdapterSxI.cpp'],
    extra_compile_args = ['--std=c++11', '-Wall', '-O3'
                          ] + ouff_mac,
    undef_macros       = ["NDEBUG"],
    extra_link_args    = ouff_mac
    ),Extension(
    name = 'transitMatrixAdapterIxS', language = 'c++',
    sources = ['spatial_access/transitMatrixAdapterIxS.cpp'],
    extra_compile_args = ['--std=c++11', '-Wall', '-O3'
                          ] + ouff_mac,
    undef_macros       = ["NDEBUG"],
    extra_link_args    = ouff_mac
    )]


REQUIRED_DEPENDENCIES = ['fiona>=1.7.12',
                         'cython>=0.28.2',
                         'matplotlib>=2.0.2',
                         'jellyfish>=0.5.6',
                         'geopandas>=0.3.0',
                         'psutil>=5.4.3',
                         'pandas>=0.19.2',
                         'numpy==1.15.4',
                         'osmnet>=0.1.5',
                         'scipy>=0.18.1',
                         'geopy>=1.11.0',
                         'shapely',
                         'tables==3.4.2',
                         'scikit_learn>=0.19.1',
                         'atlas>=0.27.0',
                         'descartes>=1.1.0',
                         'rtree>=0.8.3',
                         'h5py>=2.8.0']

REQUIRED_DEPENDENCIES += extra_dependency

SUBMODULE_NAMES = ['spatial_access.p2p',
                   'spatial_access.BaseModel',
                   'spatial_access.Models',
                   'spatial_access.ConfigInterface',
                   'spatial_access.NetworkInterface',
                   'spatial_access.MatrixInterface',
'spatial_access.SpatialAccessExceptions']

setup(
    name = 'spatial_access',
    author = 'Logan Noel (lmnoel)',
    url='https://github.com/GeoDaCenter/spatial_access',
    author_email='lnoel@uchicago.edu',
    version='0.1.6.12',
    ext_modules=EXTENSION,
    py_modules=SUBMODULE_NAMES,
    install_requires=REQUIRED_DEPENDENCIES,
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="GPL"
    )


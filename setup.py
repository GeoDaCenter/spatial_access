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
    name = 'transitMatrixAdapter', language = 'c++',
    sources = ['spatial_access/transitMatrixAdapter.cpp',
               'spatial_access/src/Graph.cpp',
               'spatial_access/src/MinHeap.cpp',
               'spatial_access/src/userDataContainer.cpp',
               'spatial_access/src/dataFrame.cpp',
               'spatial_access/src/threadUtilities.cpp',
               'spatial_access/src/transitMatrix.cpp'],
    extra_compile_args = ['--std=c++11', '-Wall', '-O3'
                          ] + ouff_mac,
    undef_macros       = ["NDEBUG"],
    extra_link_args    = ouff_mac + ['-lprotobuf']
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
                         'tables>=3.3.4',
                         'scikit_learn>=0.19.1',
                         'atlas>=0.27.0',
                         'descartes>=1.1.0',
                         'rtree>=0.8.3']

REQUIRED_DEPENDENCIES += extra_dependency

SUBMODULE_NAMES = ['spatial_access.p2p',
                   'spatial_access.ScoreModel',
                   'spatial_access.CommunityAnalytics',
                   'spatial_access.ConfigInterface',
                   'spatial_access.NetworkInterface',
                   'spatial_access.MatrixInterface',
                   'spatial_access.SpatialAccessExceptions']

setup(
    name = 'spatial_access',
    author = 'Logan Noel (lmnoel)',
    url='https://github.com/GeoDaCenter/spatial_access',
    author_email='lnoel@uchicago.edu',
    version='0.1.6.3',
    ext_modules=EXTENSION,
    install_requires=REQUIRED_DEPENDENCIES,
    py_modules=SUBMODULE_NAMES,
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="GPL",
    tests_require=['pytest']
    )
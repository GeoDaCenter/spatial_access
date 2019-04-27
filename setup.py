import sys, os
from setuptools.extension import Extension
from setuptools import setup

with open("README.md", "r") as fh:
    LONG_DESCRIPTION = fh.read()

ouff_mac = []
extra_dependency = []
if sys.platform == "darwin":
    ouff_mac = ['-mmacosx-version-min=10.9']
    extra_dependency = ['rtree>=0.8.3']

SRC_PATH = "spatial_access/src/"

MATRIX_INTERFACE_SOURCES = ["dataFrame.cpp",
                            "Serializer.cpp",
                            "userDataContainer.cpp",
                            "Graph.cpp",
                            "threadUtilities.cpp"]


def build_extension(extension_name, sources):
    full_path_sources = [SRC_PATH + src for src in sources]
    return Extension(name=extension_name, language='c++',
                     sources=full_path_sources,
                     extra_compile_args=['--std=c++11', '-Ofast', '-fomit-frame-pointer', "-g0"] + ouff_mac,
                     undef_macros=["NDEBUG"],
                     extra_link_args=ouff_mac)

EXTENSION_SOURCES = [('_p2pExtension', ['_p2pExtension.cpp'] + MATRIX_INTERFACE_SOURCES)]


EXTENSIONS = [build_extension(extension_name=extension_name, sources=sources) for extension_name, sources in EXTENSION_SOURCES]

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
                         'tables>=3.4.2',
                         'scikit_learn>=0.19.1',
                         'atlas>=0.27.0',
                         'descartes>=1.1.0',
                         'rtree>=0.8.3']

REQUIRED_DEPENDENCIES += extra_dependency

SUBMODULE_NAMES = ['spatial_access.p2p',
                   'spatial_access.BaseModel',
                   'spatial_access.Models',
                   'spatial_access.Configs',
                   'spatial_access.NetworkInterface',
                   'spatial_access.MatrixInterface',
                   'spatial_access.SpatialAccessExceptions']


if 'READTHEDOCS' in os.environ:
    REQUIRED_DEPENDENCIES = []
    EXTENSIONS = []

setup(
    name = 'spatial_access',
    author = 'Logan Noel (lmnoel)',
    url='https://github.com/GeoDaCenter/spatial_access',
    author_email='lnoel@uchicago.edu',
    version='0.1.7.12',
    ext_modules=EXTENSIONS,
    py_modules=SUBMODULE_NAMES,
    install_requires=REQUIRED_DEPENDENCIES,
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    license="GPL"
    )


import platform, distutils.core, distutils.extension, setuptools, sys, os
from setuptools.command.install import install
try:
    import Cython.Build
except:
    os.system('pip3 install Cython')
    import Cython.Build

class CustomInstallCommand(install):
    """Customized setuptools install command"""
    def run(self):
        if sys.platform == "darwin":
            os.system('brew install spatialindex')
        elif sys.platform.startswith('linux'):
            os.system('sudo apt install python3-rtree')
        else:
            exception_message = '''You are trying to install spatial_access on an unsupported 
                                   platform. Note: We DO NOT support Windows.'''

            raise Exception(exception_message, os.system)
        install.run(self)

ouff_mac = []
extra_dependency = []
if sys.platform == "darwin":
  ouff_mac = ['-mmacosx-version-min=10.9']
  extra_dependency = ['rtree>=0.8.3']

EXTENSION = distutils.extension.Extension(
    name = 'transitMatrixAdapter', language = 'c++',
    sources = ['spatial_access/transitMatrixAdapter.pyx'],
    extra_compile_args = ['-Wno-unused-function', 
                          '-std=c++11', '-Wall', '-O3'
                          ] + ouff_mac,
    undef_macros       = ["NDEBUG"],
    extra_link_args    = ouff_mac
    )

EXT_MODULES=Cython.Build.cythonize([EXTENSION],
                                    #include_path = ["/usr/local/include/"],
                                   language='c++')

REQUIRED_DEPENDENCIES = ['fiona>=1.7.12',
                         'cython>=0.28.2',
                         'matplotlib>=2.0.2',
                         'jellyfish>=0.5.6',
                         'geopandas>=0.3.0',
                         'psutil>=5.4.3',
                         'pandas>=0.19.2',
                         'numpy>=1.12.0',
                         'osmnet>=0.1.4'
                         'pandana>=0.4.0',
                         'scipy>=0.18.1',
                         'geopy>=1.11.0',
                         'Shapely>=1.6.1',
                         'scikit_learn>=0.19.1',
                         'atlas>=0.27.0',
                         'jupyter_contrib_nbextensions>=0.5.0',
                         'jupyter_nbextensions_configurator>=0.1.7']

REQUIRED_DEPENDENCIES += extra_dependency

SUBMODULE_NAMES = ['spatial_access.p2p', 
                   'spatial_access.ScoreModel', 
                   'spatial_access.CommunityAnalytics',
                   'spatial_access.ConfigInterface',
                   'spatial_access.NetworkInterface',
                   'spatial_access.MatrixInterface']

setuptools.setup(
    cmdclass = {'install':CustomInstallCommand},
    name = 'spatial_access',
    author = 'Logan Noel (lmnoel)',
    url='https://github.com/GeoDaCenter/spatial_access',
    author_email='lnoel@uchicago.edu',
    version='0.1.0',
    ext_modules=EXT_MODULES,
    install_requires=REQUIRED_DEPENDENCIES,
    py_modules=SUBMODULE_NAMES
    )

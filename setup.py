import platform, distutils.core, distutils.extension, Cython.Build, setuptools
from setuptools.command.install import install

import sys, subprocess
import os

class CustomInstallCommand(install):
    """Customized setuptools install command"""
    def run(self):
        os.system('pip3 install -r requirements.txt')
        print('running...')
        if sys.platform == "darwin":
            os.system('brew install spatialindex')
            print('installing on osx')
        elif sys.platform.startswith('linux'):
            sos.system('curl -L https://github.com/libspatialindex/libspatialindex/archive/1.8.5.tar.gz | tar xz')
            os.system('cd spatialindex-src-1.8.5')
            os.system('./configure')
            os.system('make')
            os.system('sudo make install')
            os.system('sudo ldconfig')
            print('installing on linux')
        else:
            raise Exception('You are trying to install spatial_access on an unsupported platform')
        subprocess.call(['pip3 install rtree'])
        install.run(self)

## Macs require this extra build option.
ouff_mac = []
if sys.platform == "darwin":
  ouff_mac = ['-mmacosx-version-min=10.9']

EXTENSION = distutils.extension.Extension(
    name = 'pyengine', language = 'c++',
    sources = ['spatial_access/pyengine.pyx'],
    extra_compile_args = ['-Wno-unused-function', 
                          '-std=c++11', '-Wall', '-O3'
                          ] + ouff_mac,
    undef_macros       = ["NDEBUG"],
    extra_link_args    = ouff_mac,
    #include_path       = ["/usr/local/include/"],
    # libraries          = ["armadillo"]
    )

EXT_MODULES=Cython.Build.cythonize([EXTENSION],
                                    #include_path = ["/usr/local/include/"],
                                   language='c++')

setuptools.setup(
    cmdclass = {'install':CustomInstallCommand},
    name = 'spatial_access',
    version='0.1.0',
    ext_modules=EXT_MODULES,
    py_modules=['spatial_access.p2p', 'spatial_access.ScoreModel', 'spatial_access.CommunityAnalytics']
    )

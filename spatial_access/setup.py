import platform, distutils.core, distutils.extension, Cython.Build

import sys

## Macs require this extra build option.
ouff_mac = []
if sys.platform == "darwin":
  ouff_mac = ['-mmacosx-version-min=10.9']

EXTENSION = distutils.extension.Extension(
    name = 'pyengine', language = 'c++',
    sources = ['pyengine.pyx'],
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
                                   language='c++')#, gdb_debug=True)

distutils.core.setup(
    name = 'simple',
    ext_modules=EXT_MODULES,
    )

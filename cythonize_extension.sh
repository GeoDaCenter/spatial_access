#!/usr/bin/env bash
python3 spatial_access/src/generate_extension_source.py spatial_access/src/
cython --cplus spatial_access/src/*.pyx

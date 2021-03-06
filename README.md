

# spatial_access: Compute travel times and spatial access metrics at scale
Compute travel times and spatial access measures at scale (millions of origin-destination pairs in minutes).
Travel times for three modes: walking, biking, driving.
Spatial access measures: provider-to-people ratio, avg. time to nearest provider, count/attribute sum of nearby providers, weighted access scores and floating catchment areas.
<table>
<tr>
  <td>Latest Release</td>
  <td>
    <a href="https://pypi.org/project/spatial-access/">
    <img src="https://img.shields.io/pypi/v/spatial-access.svg" alt="latest release" />
    </a>
  </td>
</tr>    
<tr>
  <td>Build Status</td>
  <td>
    <a href="https://travis-ci.org/GeoDaCenter/spatial_access">
    <img src="https://travis-ci.org/GeoDaCenter/spatial_access.svg?branch=master" alt="travis build status" />
  </td>
</tr>

<tr>
  <td>Documentation</td>
  <td>
      <a href="https://readthedocs.org/projects/spatial-acccess">
    <img src="https://readthedocs.org/projects/spatial-acccess/badge" alt="read the docs" />
  </td>
</tr>

<tr>
  <td>Tested Operating Systems</td>
  <td>
       Ubuntu, macOS
  </td>
</tr>
</table>


Components of spatial_access :
----
spatial_access has two submodules:
- p2p: Generate many to many matrices with travel times for sets of coordinates. Use `walk` ,`bike` or `drive` network types (import `transit` from other sources), or get the distance in meters.
- Models: Contains a suite of models for calculating spatial accessibility to amenities.

To use this service as a ReST API, see: https://github.com/GeoDaCenter/spatial_access_api

If you are a Windows user, instructions for installing Ubuntu on a virtual machine are at the bottom of the Readme.


Installation
----
0. A modern compiler like `gcc` or `clang`.

1. Dependencies

    - MacOS:

        `brew install spatialindex`

    - Ubuntu:

        `sudo apt-get install libspatialindex-dev`

        `sudo apt-get install python-tk`

2. Package

    `pip3 install spatial_access`

**More detailed instructions for installing in [0_Reqs_Install.ipynb](./docs/notebooks/0_Reqs_Install.ipynb)**

Usage
---
See the iPython notebooks in `docs/` for example usage, The first two notebooks contain installation instructions and run through a simple demo to make sure you have the setup successfully installed:

* [0_Reqs_Install.ipynb](https://github.com/GeoDaCenter/spatial_access/tree/master/docs/notebooks/0_Reqs_Install.ipynb): Installation requirements to run the notebook demos  
* [1_Simple_Test_Demo](https://github.com/GeoDaCenter/spatial_access/tree/master/docs/notebooks/1_Simple_Test_Demo.ipynb): Simple demo to test your setup installation works   


The remaining notebooks walk through how to run the travel time matrix and spatial access metrics, including main functions and parameters:  

* [2_Methods](https://github.com/GeoDaCenter/spatial_access/tree/master/docs/notebooks/2_Methods.ipynb): Purpose and structure of the package + methodology for estimating travel time matrices and spatial access metrics  
* [3_Travel_Time_Matrix.ipynb](https://github.com/GeoDaCenter/spatial_access/tree/master/docs/notebooks/3_Travel_Time_Matrix.ipynb): How to run the travel time matrices using [p2p.py](https://github.com/GeoDaCenter/spatial_access/blob/master/spatial_access/p2p.py)
* [4_Access_Metrics.ipynb](https://github.com/GeoDaCenter/spatial_access/tree/master/docs/notebooks/4_Access_Metrics.ipynb): How to run the access metrics (origin-based) using  [Models.py](https://github.com/GeoDaCenter/spatial_access/blob/master/spatial_access/Models.py)  
* [5_Coverage_Metrics.ipynb](https://github.com/GeoDaCenter/spatial_access/tree/master/docs/notebooks/5_Coverage_Metrics.ipynb): How to run the coverage metrics (destination-based) using [Models.py](https://github.com/GeoDaCenter/spatial_access/blob/master/spatial_access/Models.py)
* [6_TSFCA.ipynb](https://github.com/GeoDaCenter/spatial_access/tree/master/docs/notebooks/6_TSFCA.ipynb): How to run a two-stage floating catchment area model (origin-based) using [Models.py](https://github.com/GeoDaCenter/spatial_access/blob/master/spatial_access/Models.py)


The **data** folder contains the input_data needed to estimate the metrics under **sources** (for origins) and **destinations** (for destinations).  
In output_data, the **matrices** folder stores the estimated symmetric and asymmetric matrices.  
The **models** folder contains the results of the models' analyses.  
Finally, **figures** stores the results of maps and plots calculated during the process.

You can also download all of the notebooks in one PDF file [here](https://github.com/GeoDaCenter/spatial_access/tree/master/docs/notebooks/spatial_access_documentation081219.pdf).

### Overwriting default configuration values
p2p provides default configuration values for edge weights and node impedance (see spatial_access/configs.py).
You can overwrite these as follows:
```
from spatial_access.p2p import TransitMatrix
from spatial_access.Configs import Configs
custom_config = Configs()
# set fields of custom_cofig
tm = TransitMatrix(..., configs=custom_config)
# continue with computation
```

Maintainance
---

### Instructions for building locally (only for developers):

- Additional requirements: `cython` and `jinja2`
- To regenerate .pyx files, run: `bash cythonize_extension.sh` (TravisCI will do this automatically on deployment)
- To install locally, run: `sudo python3 setup.py install ` from spatial_access root directory
- Unit tests require the `pytest` package. From package root directory, run `python3 -m pytest tests/` to run all unit tests.

### PyPi Maintenance
The package lives at: `https://pypi.org/project/spatial-access/`

When a branch is pulled into Master and builds/passes all unit tests,
Travis CI will automatically deploy the build to PyPi.


To update PyPi access credentials, see .travis.yml and follow the instructions at https://docs.travis-ci.com/user/deployment/pypi/
to generate a new encrypted password.


### Installing Ubuntu 18 LTS with dependencies from scratch (recommended for Windows users)

1. Follow the instructions at this link: https://linus.nci.nih.gov/bdge/installUbuntu.html to set up a virtual machine
2. `sudo apt-get update`
3. `sudo add-apt-repository universe`
4. `sudo apt-get -y install python3-pip`
5. Continue with Installation Instructions (above)

### Questions/Feedback?

spatial@uchicago.edu

### Acknowledgments

Developed by Logan Noel at the University of Chicago's Center for Spatial Data Science (CSDS) with support from the Public Health National Center for Innovations (PHNCI), the University of Chicago, and CSDS.

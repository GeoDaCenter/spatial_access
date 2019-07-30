

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

**More detailed instructions for installing in [reqs_install.ipynb](./docs/notebooks/reqs_install.ipynb)**

Usage
---
See the iPython notebooks in `docs/` for example usage, or https://readthedocs.org/projects/spatial-acccess/ for technical documentation.

Under the **docs** folder, the notebooks run through Hyde Park's amenities simple demo, to make sure you have the setup successfully installed: 
* [reqs_install.ipynb](./docs/notebooks/reqs_install.ipynb)  : This notebook shows the installation requirements in order to run the demos.  
* [simple_demo.ipynb](./docs/notebooks/simple_demo.ipynb)  : This notebook shows a simple example which runs the walking matrix and metrics for amenities in Hyde Park, Chicago.  

For a more detailed explanation of the spatial_access packages, the estimation of the matrices, and the calculation of the metrics, please check the following notebooks:
* [0_master.ipynb](./docs/notebooks/0_master.ipynb)  : These notes explain the structure of spatial_access and the logic behind the estination of matrices and metrics.  
* [1_matrix.ipynb](./docs/notebooks/1_matrix.ipynb)  : This notebook shows how to run the travel time distance matrices.  It uses the [p2p.py](./scripts/p2p.py) script.  
* [2_access_score.ipynb](./docs/notebooks/2_access_score.ipynb)  : This notebook shows how to run the access metrics (origin-based) and the specific parameters that might be tweaked depending on the user's interest.  It uses the [BaseModel.py](./spatial_access/BaseModel.py) and [Models.py](./scripts/Models.py) scripts.  
* [3_coverage_score.ipynb](./docs/notebooks/3_coverage_score.ipynb)  : This notebook shows how to run the coverage metrics (destination-based) and the specific parameters that might be tweaked depending on the user's interest. It uses the [BaseModel.py](./spatial_access/BaseModel.py) and [Models.py](./spatial_access/Models.py) scripts. 
* [4_tsfca.ipynb](./docs/notebooks/4_tsfca.ipynb)  : This notebook shows how to run a two-stage floating catchment area metric access (origin and destination -based) and the specific parameters that might be tweaked depending on the user's interest.  It uses the [BaseModel.py](./spatial_access/BaseModel.py) and [Models.py](./spatial_access/Models.py) scripts.


The **data** folder contains the [input_data](./data/input_data/) needed for the estimation of the metrics under **sources** (for origins) and **destinations** (for destinations). In [output_data](./data/input_data/), the **matrices** folder contains the estimated symmetric and asymmetric matrices. The **modelss** folder contain the results of the models' analyses. Finally, **figures** contain the results of maps and plots calculated during the process. 


### Overwriting default configuration values
p2p provides default configuration values for edge weights and node impedence (see spatial_access/configs.py).
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

lnoel@uchicago.edu or spatial@uchicago.edu

### Acknowledgments

Developed by Logan Noel at the University of Chicago's Center for Spatial Data Science (CSDS) with support from the Public Health National Center for Innovations (PHNCI), the University of Chicago, and CSDS. 



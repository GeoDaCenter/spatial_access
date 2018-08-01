**The repository is organized as follows:**

Under the **demo** folder, the notebooks run through Chicago's health example:  
* [reqs.ipynb](./reqs.ipynb)  : This notebook shows the installation and files requirements in order to run the demos.  
* [matrix.ipynb](./matrix.ipynb)  : This notebook shows how to run the travel time distance matrices.  It uses the [p2p](./scripts/p2p.py) script.
* [access_score.ipynb](./access_score.ipynb)  : This notebook shows how to run the access score and the specific parameters that might be tweaked depending on the user's interest.  It uses the [ScoreModel](./scripts/ScoreModel.py) and [CommunityAnalytics](./scripts/CommunityAnalytics.py) scripts.
* [coverage_score.ipynb](./coverage_score.ipynb)  :This notebook shows how to run the coverage score and the specific parameters that might be tweaked depending on the user's interest.  It uses the [ScoreModel](./scripts/ScoreModel.py) and [CommunityAnalytics](./scripts/CommunityAnalytics.py) scripts.
* [travel_time_metrics.ipynb](./travel_time_metrics.ipynb)  :This notebook shows how to run the travel time distance matrices. It uses the [ScoreModel](./scripts/ScoreModel.py) and [CommunityAnalytics](./scripts/CommunityAnalytics.py) scripts.  
* [calibration.ipynb](./calibration.ipynb)  : **? Have it as a notebook/within the demos/in this notebook or not at all?** Comparison (validation and calibration) with GoogleMaps.

The **data** folder contains the files needed for the estimation of the metrics under **ORIG** (for origins) and **DEST** (for destinations). The **matrices** folder contains the estimated symmetric and asymmetric matrices. The **access_score**, **coverage_score**, and **travel_time_metrics** folders contain the results of the analyses. Finally, **figures** contain the results of maps and plots calculated during the process. 

Further editing of the Python scripts is accessible under the folder **scripts**. 

The rest of this notebook describes the reasoning of the Python modules p2p, ScoreModel, and CommunityAnalytics which compose the calculation of the algorithm of travel time **matrices** and the estimation of the **metrics**. Please note that this report stipulates the **_parameters_** specified within the estimations so the users can reproduce the calculations.

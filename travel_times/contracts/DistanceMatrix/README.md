#Querying the Distance Matrix


**query_auto.py** The script will collect the driving distance between super blocks and destinations with MapZen's API. 
**query_pedestrian.py** The script will collect the walking distance from MapZen's API. 

Both scripts query MapZen's sources_to_targets API with 50 destination per queey.

The python version for the scripts is python 3.5.

* Command to run the model: `python query_auto.py`. When running the script, you'll need to provide the MapZen's API key like [key1.txt](key1.txt) and [key2.txt](key2.txt). Then you will need to input the number of blocks per destinations you want to query. The script will automaticly query all the distance and store the matrix in the outputfile.


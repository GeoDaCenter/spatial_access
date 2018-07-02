# contracts
Contracts Research Project


**data_process_script** folder contains the code to get and process the data:   

* spider.py: spider to get all the IRS 990 form in XML file.
* filter.py: parse the XML and extract the forms in Chicago, New York and Seattle
* merge.py: python script to merge the LEHD data into block shapefiles

The raw data is quite big(~30G), so I just added the pured to dropbox.   
[data on drop box](https://www.dropbox.com/sh/tcfb926armeo61r/AACaBDjIPrGzS3hrY7Z3pTrQa?dl=0)

----
* The DistanceMatrix folder contains the code to get distance matrix from mapzen's api as well as the keys. Sorry that the code is poorly commented, but the main function of the code is to get travel time and distance as well as creating log files to record the last query. So when the program is terminated, just run it again and it will begin with the last query.   
    MAPZENAPI: ```https://mapzen.com/documentation/mobility/matrix/api-reference/```

* The Model folder contains the code and result for the protype model.


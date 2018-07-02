#Access Score Model


**ScoreModel.py** The script thet generate the access score. User can define their own distance decay function and pass that function to the transportation model to apply it. 
**TransModel.py** The script will load the for walk and driving models.

The distance file are stored on dropbox, to run the script, you just need to download the distance file and put them into a folder named data in the current path.
[data on drop box](https://www.dropbox.com/sh/tcfb926armeo61r/AACaBDjIPrGzS3hrY7Z3pTrQa?dl=0)

The python version for the scripts is python 3.5 and they use the *pyshape* package. 

* Command to install the pyshp package `pip install pyshp` or `pip3 install pyshp`
* Command to run the model: `python ScoreModel.py`. The script will generate a shape file in the result folder contains the access score per block for each transportation model and a weighted combination access score.


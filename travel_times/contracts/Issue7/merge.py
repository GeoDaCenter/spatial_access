import pandas as pd
import numpy as np
import string
import difflib
from fuzzywuzzy import fuzz

def remove_punctuation(instr):
    for p in string.punctuation:
        instr = instr.replace(p, "")
    return instr



alldst = pd.read_csv("all_destinations_7632.csv", low_memory=False)
matcheddst = pd.read_csv("matched_destinations_4296.csv", dtype = {'match_rate': np.float64, 'good_match': np.int32}, low_memory=False)
alldata = pd.read_csv("nycdb_124391.csv", low_memory=False)
del matcheddst["name"]
del matcheddst["ein"]
del matcheddst["processed_current_entity_name"]
merged = alldst.merge(matcheddst, on = "ID.org", how = "left")
merged = merged.sort_values(by = "good_match")

data = []
trans = []
for index, row in alldata.iterrows():
    name = row["Current Entity Name"]
    name = remove_punctuation(name)
    date = row["date"]
    docid = row["DOS ID"]
    data.append({"name": name.upper(), "date": date, "dosid": docid, "curname": row["Current Entity Name"]})

def max_simial(name):
    sim = 0
    maxid = -1
    for i in range(0, len(data)):
        if(abs(len(name) - len(data[i]['name'])) / len(name) > 0.1) :
            continue
        ratio = fuzz.ratio(name, data[i]['name']) / 100.0
        if ratio > sim:
            maxid = i
            sim = ratio
    print("------------------------------------------------")
    print(name)
    print(data[maxid]["name"])
    print("Similarity:", sim)
    print("------------------------------------------------")
    return sim,maxid


for index, row in merged.iterrows():
    print("processing:", index)
    if row['good_match'] != 1:
        name = row["name"]
        (sim,maxid) = max_simial(name)
        d = data[maxid]
        merged.loc[index, "match_rate"] = sim
        merged.loc[index, "processed_name"] = d["name"]
        merged.loc[index, "date"] = d["date"]
        merged.loc[index, "DOS ID"] = d["dosid"]
        merged.loc[index, "Current Entity Name"] = d["curname"]


merged.to_csv("merged.csv")



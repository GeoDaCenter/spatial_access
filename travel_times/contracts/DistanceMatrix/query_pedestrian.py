import numpy as np
import json
import random
import requests
import time
import urllib.request

keys = []
keyfile = input("key file:")
keyfile = open(keyfile, "r")
for line in keyfile:
    keys.append(line.strip("\n"))
    
dist = {}
key_idx = 0
prefix = "matrix.mapzen.com/sources_to_targets?json="

costingType = "pedestrian"
filename = input("file:")
j_range = int(input("blocks to compute(*50):"))
res = open(filename, "r")

for l in res.readlines():
    dest = l.strip("\n").split(",")[0]
    dist[dest] = 1
res.close()

res = open(filename, "a")
    
def calDis(b, d):
    return (b["x"] - d["x"]) ** 2 + (b["y"] - d["y"]) ** 2

def get_key():
    global key_idx
    if key_idx % len(keys) == 0:
        time.sleep(0.5)
    key_idx += 1
    return keys[key_idx % len(keys)]

block = []
f1 = open("block.csv", "r")
lines = f1.readlines()
lines = lines[1:]
for line in lines:
    elements = line.strip("\n").split(",")
    data = {"id": elements[1], "x": np.float64(elements[2]), "y": np.float64(elements[3])}
    block.append(data)

dest = []
f1 = open("destnations.csv", "r")
lines = f1.readlines()
lines = lines[1:]
for line in lines:
    elements = line.strip("\n").split(",")
    data = {"id": elements[1], "x": np.float64(elements[2]), "y": np.float64(elements[3])}
    dest.append(data)

last_key = ""
cur_key = ""
for dest_idx, d in enumerate(dest):
    if d["id"] in dist:
        continue 
    print("processing:" + str(dest_idx))
    sorted_block = sorted(block, key = lambda b: calDis(b,d))
    dx, dy = d["x"], d["y"]
    location_dic = {"sources": [{"lat": dx, "lon": dy}]}
    dist[d["id"]] = []
    for j in range(j_range):
        location_dic["targets"] = []
        for i in range(j * 50, j * 50 + 50):
            dx, dy = sorted_block[i]["x"], sorted_block[i]["y"]
            location_dic["targets"].append({"lat": dx, "lon": dy})
        location_dic["costing"] =  costingType
        data = ""
        while data == "":
            try:
                cur_key = get_key()
                jsonstr = json.dumps(location_dic)
                apiurl = prefix + jsonstr + "&api_key=" + cur_key
                data = requests.get("https://" + apiurl).text
            except Exception as er:
                print(er)
                cur_key = get_key()
            if(len(keys) == 0):
                print("NO keys!!")
                break
        last_key = cur_key
        return_dic = json.loads(data)
        if "sources_to_targets" in return_dic:
            dists = return_dic["sources_to_targets"][0]
            for i in range(len(dists)):
                dist[d["id"]].append([sorted_block[i + j * 50]["id"],str(dists[i]["distance"]), str(dists[i]["time"])])

    res = open(filename, "a")
    for data in dist[d["id"]]:
        res.write(d["id"] + "," + data[0] + "," + data[1] + "," + data[2] + "\n")
    res.close()



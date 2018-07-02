import random
import numpy as np
import math
import shapefile
import pandas as pd
import copy

class KMeans:
    blocks = []
    superblocks = []
    k = 0
    def __init__(self, k):
        self.k = k
        
    def readData(self):
        self.blocks = []
        f1 = open("block.csv", "r")
        lines = f1.readlines()
        lines = lines[1:]
        for line in lines:
            elements = line.strip("\n").split(",")
            data = {"BlockID": elements[1], "x": np.float64(elements[2]), "y": np.float64(elements[3])}
            self.blocks.append(data)
        print(len(self.blocks), "blocks loaded")

    def calDist(self, a, b):
        return (a["x"] - b["x"])**2 + (a["y"] - b["y"])**2 
    
    def findNearest(self, cur):
        dist = 100.0
        for superid, block in enumerate(self.superblocks):
            tmp = self.calDist(block, cur)
            if(tmp < dist):
                dist = tmp
                cur["super"] = superid

    def updateSuper(self):
        x_sum = [0.0] * self.k
        y_sum = [0.0] * self.k
        count = [0.0] * self.k
        for block in self.blocks:
            x_sum[block["super"]] += block["x"]
            y_sum[block["super"]] += block["y"]
            count[block["super"]] += 1
        move_sum = 0.0 
        for i in range(self.k):
            x_sum[i] /= count[i]
            y_sum[i] /= count[i]
            move_sum += math.sqrt((self.superblocks[i]["x"] - x_sum[i]) ** 2 + (self.superblocks[i]["y"] - y_sum[i]) ** 2)
            self.superblocks[i]["x"] = x_sum[i]
            self.superblocks[i]["y"] = y_sum[i]
            self.superblocks[i]["count"] = count[i]
        print(move_sum)

    def iterate(self, m):
        sample = random.sample(range(len(self.blocks)), self.k)
        for idx, s in enumerate(sample):
            self.superblocks.append(copy.deepcopy(self.blocks[s]))
            self.superblocks[idx]["BlockID"] = idx
        for i in range(m):
            for block in self.blocks:
                self.findNearest(block)
            self.updateSuper()
            
    def generateShapeFile(self):
        w = shapefile.Writer(shapefile.POINT)
        w.field("BLOCKS", "N", 10)
        for block in self.superblocks:
            w.point(block["y"], block["x"])
            w.record(int(block["count"]))
        w.save("superblocks")

    def outputResult(self):
        df = pd.DataFrame.from_records(self.blocks)
        df.rename(columns={'x':'Latitude', 'y': 'Longitude', 'super': 'SuperBlockID'}, inplace=True)
        df.to_csv("blocks_spuer.csv")

        df = pd.DataFrame.from_records(self.superblocks)
        df.rename(columns={'x':'Latitude', 'y': 'Longitude', 'count': 'BlocksCount'}, inplace=True)
        df = df[['BlockID', 'Latitude', 'Longitude', 'BlocksCount']]
        df.to_csv("superblocks.csv")

if __name__ == "__main__":
    km = KMeans(500)
    km.readData()
    km.iterate(50)
    km.generateShapeFile()
    km.outputResult()

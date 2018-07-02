import shapefile
import random
import numpy as np
import pandas as pd
import os

todo = ["ct", "il", "nj", "ny", "pa", "wa"]
attrs = ["CE01", "CE02"]

def genPath(state, year):
    return "LEHD Data/" + state.upper() + "/" + state + "_rac_S000_JT00_" + str(year) + ".csv"

def csvReader(state, begin_year, end_year):
    year_dic = {}
    for year in range(begin_year, end_year + 1):
        print(year)
        dic = {}
        df = pd.read_csv(genPath(state, year), dtype = {'h_geocode': str, 'CE01': np.int64, 'CE02': np.int64, 'CE03': np.int64})
        for index, row in df.iterrows():
            dic[row["h_geocode"]] = [int(row[i]) for i in attrs]
        year_dic[year] = dic
    return year_dic

def newShapeFile(input, state , dic, output, begin_year, end_year):
    
    r = shapefile.Reader(input)
    w = shapefile.Writer()
    #shapes = sf.shapes()
    mis = 0
    hit = 0
    w.fields = list(r.fields)
    for year in range(begin_year, end_year + 1):
        for attr in attrs:
            w.field(attr +"_" + str(year), "N", 10)
    for rec in r.records():
        blkid = str(rec[4])
        for year in range(begin_year, end_year + 1):
            try:
                values = dic[year][blkid]
                for value in values:
                    rec.append(value)
            except:
                for at in attrs:
                    rec.append(-1)
        w.records.append(rec)
    
    w._shapes.extend(r.shapes())
    if not os.path.exists(output):
        os.mkdir(output)
    w.save(output + "/block")
    print(hit, " blocks have LEHD data")
    print(mis, " blocks dont have LEHD data")

if __name__ == "__main__":
    for state in todo:
        newShapeFile("raw/" + state, state, csvReader(state, 2002, 2014), "merged/" + state, 2002, 2014)


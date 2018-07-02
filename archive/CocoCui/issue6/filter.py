import urllib.request
import random
import json
import pandas as pd
import numpy as np
import os
import csv
import codecs
import time
import re
from fuzzywuzzy import fuzz
import string
zipstr = "11361, 11362, 11363, 11364, 11354, 11355, 11356, 11357, 11358, 11359, 11360, 11365, 11366, 11367, 11412, 11423, 11432, 11433, 11434, 11435, 11436, 11101, 11102, 11103, 11104, 11105, 11106, 11374, 11375, 11379, 11385, 11691, 11692, 11693, 11694, 11695, 11697, 11004, 11005, 11411, 11413, 11422, 11426, 11427, 11428, 11429, 11414, 11415, 11416, 11417, 11418, 11419, 11420, 11421, 11368, 11369, 11370, 11372, 11373, 11377, 11378"

def remove_punctuation(instr):
    for p in string.punctuation:
        instr = instr.replace(p, "")
    instr = instr.replace("INC", "")
    instr = instr.replace("THE", "")
    return instr

class Spider:
    indexs = []
    curdir = "./"
    year = 2013
    logfile = ""
    records = {}
    recordList = []
    proxylist = []
    pattern = '<table class="yp_multi_listing" cellpadding="5px" cellspacing=0 width="100%">[\s\S]*?</table>'
    pattern = re.compile(pattern)
    addr = '<div class="sml_txt">([\s\S]*?)</div>'
    addr = re.compile(addr)
    name_pattern = 'onclick="delayhref\(this\);return false;">([\s\S]*?)</a>'
    name_pattern = re.compile(name_pattern)
    res_dic = {}
    zipstr = "11361, 11362, 11363, 11364, 11354, 11355, 11356, 11357, 11358, 11359, 11360, 11365, 11366, 11367, 11412, 11423, 11432, 11433, 11434, 11435, 11436, 11101, 11102, 11103, 11104, 11105, 11106, 11374, 11375, 11379, 11385, 11691, 11692, 11693, 11694, 11695, 11697, 11004, 11005, 11411, 11413, 11422, 11426, 11427, 11428, 11429, 11414, 11415, 11416, 11417, 11418, 11419, 11420, 11421, 11368, 11369, 11370, 11372, 11373, 11377, 11378"
    zips = []
    cities = ["brooklyn", "new york", "staten island", "bronx", "queens"] 
    def __init__(self):
        self.logfile = open("process.log", "a")
        self.zips = self.zipstr.replace(" ", "").split(",")
        print(self.zips)

    def saveStatus(self, count):
        f = open ("status.txt", 'w')
        f.write(str(count))
        f.close()

    def inlist(self, addr):
        for city in self.cities:
            if city in addr:
                print(city)
                return True
        for zip in self.zips:
            if zip in addr:
                print(zip)
                return True
        return False

    def process(self):
        if os.path.exists("id_name.csv"):
            df = pd.read_csv("id_name.csv")
        for idx, row in df.iterrows():
            print(idx)
            name = row['name']
            city = row['city']
            state = row['state']
            id = row['ID.org']
            addrlist = self.find_name("raw/" + id + ".html", name)
            if len(addrlist) > 0:
                df.loc[idx, 'name'] = 'Done'
            self.res_dic[idx] = {"ID.org": id, "clean name": name}
            for i in range(10):
                if i < len(addrlist):
                    self.res_dic[idx]["match_" + str(i)] = addrlist[i]
                else:
                    self.res_dic[idx]["match_" + str(i)] = {}

        df = df[df.name != 'Done'].to_csv("todo.csv")
        df = pd.DataFrame.from_dict(self.res_dic, orient='index')
        cols = ["ID.org", "clean name"]
        for i in range(10):
            cols.append("match_" + str(i))
        df = df[cols]
        df.to_csv("addresses.csv", cols = cols)

    def find_name(self, filename, name, th = 0.5):
        html = open(filename, "r")
        html = html.read()
        addrlist = []
        addrs = self.pattern.findall(html)
        for i in addrs:
            try:
                dstname = self.name_pattern.findall(i)[0]
                address = self.addr.findall(i)[0]
                clean_address = address.replace("<br>", ";")
                city = address.split("<br>")[1]
                dstname = remove_punctuation(dstname.upper())
                ratio = fuzz.ratio(name, dstname) / 100.0
                dic = {"score": ratio, "name": dstname, "address":clean_address}
                if ratio > 0.3 and self.inlist(city.lower()):
                    addrlist.append(dic)
            except Exception as er:
                pass
        addrlist.sort(key = lambda obj: obj["score"], reverse = True)
        return addrlist

if __name__ == "__main__":
    spider = Spider()
    spider.process()

import urllib.request
import random
import json
import pandas as pd
import numpy as np
import os
import csv
import codecs
import requests
import time

user_agents = [
'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11',
'Opera/9.25 (Windows NT 5.1; U; en)',  
'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)',  
'Mozilla/5.0 (compatible; Konqueror/3.5; Linux) KHTML/3.5.5 (like Gecko) (Kubuntu)',  
'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.0.12) Gecko/20070731 Ubuntu/dapper-security Firefox/1.5.0.12',  
'Lynx/2.8.5rel.1 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/1.2.9',  
'Mozilla/5.0 (X11; Linux i686) AppleWebKit/535.7 (KHTML, like Gecko) Ubuntu/11.04 Chromium/16.0.912.77 Chrome/16.0.912.77 Safari/535.7',  
"Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:10.0) Gecko/20100101 Firefox/10.0 ",  
]   

class Spider:
    indexs = []
    curdir = "./"
    year = 2013
    logfile = ""
    records = {}
    recordList = []
    proxylist = []
    def __init__(self):
        self.logfile = open("process.log", "a")
    
    def getproxy(self):
        apiurl = "http://tvp.daxiangdaili.com/ip/?tid=558650581987371&num=100&area=美国"
        data = requests.get(apiurl).text
        for proxy in data.split("\r\n"):
            self.proxylist.append(proxy)

    def openurl(self, url):
        #res = urllib.request.urlopen(req, timeout = 3)
        data = ""
        while len(data) <= 1500:
            proxy = random.choice(self.proxylist)
            try:
                proxies = { "http": "http://" + proxy, "https": "https://" + proxy, } 
                res = requests.get(url, proxies = proxies, timeout = 2)
                data = res.text
                if "Please confirm that you are human by typing the numbers shown below into the box:" in data:
                    self.proxylist.remove(proxy)
                    continue
            except Exception as er:
                data = ""
                self.proxylist.remove(proxy)
                if len(self.proxylist) < 30:
                    print("charge proxies")
                    self.getproxy()
        return data

    def savedata(self, filename, data):
        f = open("raw/" + filename + ".html", 'wb')
        f.write(data)
        f.close()

    def loadIndex(self):
        filename = 'mergedcontracts.csv'
        with codecs.open(filename, "r",encoding='utf-8', errors='ignore') as csvfile:
            reader = csv.DictReader(csvfile)
            for rows in reader:
                id = rows['ID.org']
                record = {'ID.org': rows['ID.org'], 'year': rows['startyear'], 'name': rows['clean.name'], 'city': rows['city'], 'state': rows['state']}
                if id in self.records:
                    y = self.records[id]['year']
                    if(record['year'] > y):
                        self.records[id] = record
                else:
                    self.records[id] = record
            for id in self.records:
                self.recordList.append(self.records[id])
            newdf = pd.DataFrame(self.recordList)
            newdf.to_csv("id_name.csv")

    def saveStatus(self, count):
        f = open ("status.txt", 'w')
        f.write(str(count))
        f.close()

    def process(self):
        if os.path.exists("todo.csv"):
            df = pd.read_csv("todo.csv")
        else:
            self.loadIndex()
            df = pd.read_csv("id_name.csv")
        
        if os.path.exists("status.txt"):
            f = open("status.txt", 'r')
            startPoint = int(f.readline())
        else:
            startPoint = 0

        for idx, row in df.iterrows():
            if idx < startPoint:
                continue
            name = row['name']
            city = row['city']
            state = row['state']
            id = row['ID.org']
            try:
                url = "http://www.addresses.com/yellow-pages/name:" + name.replace(" ", "+") + "/state:NY/listings.html"
                #url = "http://www.yellowpages.com/search?from=AnyWho&tracks=true&search_terms=" + name.replace(" ", "+") + "&geo_location_terms=NY"
                #url = "http://www.whitepages.com/business/NY/state-search/" + name.replace(" ", "-")
                data = self.openurl(url)
                self.savedata(id, str.encode(data))
            except Exception as er:
                message = str(idx) + " : " + str(er)
                self.logfile.write(message + "\n")
            print("Porcess:", idx, "/", len(self.proxylist), "of proxies remained")
            time.sleep(2)
            if len(self.proxylist) < 30:
                print("charge proxies")
                self.getproxy()
            self.saveStatus(idx)

if __name__ == "__main__":
    spider = Spider()
    spider.getproxy()
    spider.process()

import urllib.request
import random
import json
import os

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
    def __init__(self, y):
        self.year = str(y)
        self.curdir = self.curdir + str(y) + "/";
        self.logfile = open(self.curdir + year + ".log", "a")
    
    def openurl(self, url):
        header = random.choice(user_agents)
        req = urllib.request.Request(url)
        req.addheaders = [('User-agent', header)]
        res = urllib.request.urlopen(req, timeout = 3)
        data = res.read()
        return data

    def saveXML(self, filename, data):
        f = open(self.curdir + filename + ".xml", 'wb')
        f.write(data)
        f.close()

    def loadIndex(self):
        filename = 'index_' + self.year + '.json'
        header = 'Filings' + self.year
        f = open(filename, encoding='utf-8')
        self.indexs = json.load(f)
        self.indexs = self.indexs[header]

    def saveStatus(self, count):
        f = open(self.year + "_status.txt", 'w')
        f.write(str(count))
        f.close()

    def process(self):
        statusfile = self.year + "_status.txt"
        startPoint = 0
        self.loadIndex()
        if os.path.exists(statusfile):
            f = open(statusfile, 'r')
            startPoint = int(f.readline())
        else:
            startPoint = 0
        for i in range(startPoint, len(self.indexs)):
            try:
                xml = self.openurl(self.indexs[i]["URL"])
                self.saveXML(self.indexs[i]["ObjectId"],xml)
            except Exception as er:
                message = str(i) + " : " + str(er)
                self.logfile.write(message + "\n")
            if i % 20 == 0:
                print("Porcess:", i, "/" ,len(self.indexs))
                self.saveStatus(i)

if __name__ == "__main__":
    year = input("year:")
    spider = Spider(year)
    spider.process()


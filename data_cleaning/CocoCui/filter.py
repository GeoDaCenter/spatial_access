import xml.dom.minidom
import os

xmls = []
xmlnames = []
citys = ["CHICAGO", "NEWYORK", "SEATTLE"]

def getXMLs(dir):
    global xmls
    files = os.listdir(dir)
    for name in files:
        if ".xml" in name:
            fullpath = os.path.join(dir, name)
            xmls.append(fullpath)
            xmlnames.append(name)

def getCity(xmlPath, error_file):
    dom = xml.dom.minidom.parse(xmlPath)
    filer = dom.getElementsByTagName('Filer')
    if len(filer) == 0:
        print(xmlName)
    else:
        city = filer[0].getElementsByTagName('City')
        if len(city) == 0:
            city = filer[0].getElementsByTagName('CityNm')
        if len(city) == 0:
            error_file.write(xmlPath + "\n")
            return (dom, "")
        else:
            return (dom, city[0].firstChild.data.upper().replace(" ", ""))

def output(city, dom, filename):
    if city in citys:
        output_path = os.path.join(citydir[city], filename)
        f = open(output_path, 'w')
        dom.writexml(f,encoding = 'utf-8')
        f.close()

if __name__ == "__main__":
    year = str(input("please input the year:"))
    output_root = year + "_extracted";
    citydir = {}
    if not os.path.exists(output_root):
        os.mkdir(output_root)
    error_file = os.path.join(output_root, "unparsed.log")
    error_file = open(error_file, 'a')
    for city in citys:
        citypath = os.path.join(output_root, city)
        if not os.path.exists(citypath):
            os.mkdir(citypath)
        citydir[city] = citypath
    
    getXMLs(year)
    for index,name in enumerate(xmls):
        if index % 100 == 0:
            print ("%.3f Complete" % (index * 100.0 / len(xmls)))
        dom, city = getCity(name, error_file)
        output(city, dom, xmlnames[index])


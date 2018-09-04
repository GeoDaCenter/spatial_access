import re
import STANDARDIZE_NAME as sname


def stdname(string):
    '''
    Calls the original standardize_name function, then performs some additional
    cleaning for service organizations according to the peculiarities of those
    datasets. Returns a dataframe.
    '''

    # Call the original standardize_name function to do preliminary cleaning
    string = sname.standardize_name(string)

    # Standardize local universities and other organizations that sometimes have
    # slightly different names across records of the same organization
    univs = ['UNIVERSITY OF CHICAGO','NORTHWESTERN UNIVERSITY',
             'DEPAUL UNIVERSITY','RUSH UNIVERSITY','UNIVERSITY OF ILLINOIS',
             'SOUTHERN ILLINOIS UNIVERSITY','ILLINOIS INSTITUTE OF TECHNOLOGY']
    others = ['SALVATION ARMY','EL VALOR','ERIE FAMILY HEALTH CENTER',
              'FRESENIUS MEDICAL CARE','FRIEND FAMILY HEALTH CENTER',
              'HUMAN RESOURCES DEVELOPMENT INSTITUTE']
    for item in univs + others:
        if string.startswith(item) or string.endswith(item):
            return item


    # Standardize entities that are part of the Archdiocese
    cath = ['CATHOLIC CHARITIES','CATHOLIC BISHOP OF CHICAGO',
            'ARCHDIOCESE OF CHICAGO','ARCHDIOSIS OF CHICAGO']
    for c in cath:
        if string.startswith(c) or string.endswith(c):
            return 'CATHOLIC CHARITIES OF ARCHDIOCESE OF CHICAGO'


    # Create a dictionary that maps other common names to the preferred name
    dicto = {'CHURCH OF JSUS CHRIST OF LD STS':'CHURCH OF JESUS CHRIST OF LATTER DAY SAINTS',
             'EASTER SEALS':'EASTER SEALS METROPOLITAN CHICAGO',
             '^UIC ':'UNIVERSITY OF ILLINOIS',
             '^UNIVERSITY ILLINOIS ':'UNIVERSITY OF ILLINOIS'
            }
    for key, value in dicto.items():
        if re.findall(key,string):
            return value

    return string

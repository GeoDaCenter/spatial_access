import numpy as np
import pandas as pd
import premap4 as pm4


IRS = '../../../rcc-uchicago/PCNO/Matching/CHICAGO_IRS990_2013-2016_reshaped.csv'
GEO = '../../../rcc-uchicago/PCNO/CSV/chicago/Geocoded Service Addresses/map4_for_geocoding_geocoded.csv'
MAP4 = '../../../rcc-uchicago/PCNO/CSV/chicago/Maps/map4.csv'


def read_geo():
    '''
    '''

    df = pd.read_csv(GEO,converters={'Zip':str})

    return df.drop(['Match Score','ID'],axis=1)


if __name__ == '__main__':

    irs = pm4.read_irs()
    geo = read_geo()

    merged = irs.merge(geo)
    merged.to_csv(MAP4,index=False)

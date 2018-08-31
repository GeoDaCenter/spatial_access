import numpy as np
import pandas as pd
import premap4 as pm4


GEO = '../../../rcc-uchicago/PCNO/CSV/chicago/Geocoded Service Addresses/map4_for_geocoding_geocoded.csv'
MAP4 = '../../../rcc-uchicago/PCNO/CSV/chicago/Maps/map4.csv'


def read_geo():
    '''
    Reads in the geocoded addresses for map 4 locations. Converts the Zip column
    to string. Drops the Match Score and ID columns. Returns a dataframe.
    '''

    # Read in the geocoded file and convert Zip to string
    df = pd.read_csv(GEO,converters={'Zip':str})

    # Drop two columns
    return df.drop(['Match Score','ID'],axis=1)


if __name__ == '__main__':

    # Read in the IRS records from the premap4.py script
    irs = pm4.mod_irs()

    # Read in the geocoded addresses
    geo = read_geo()

    # Merge the coordinates into the IRS records, then write to CSV
    merged = irs.merge(geo,how='left')
    merged.to_csv(MAP4,index=False)

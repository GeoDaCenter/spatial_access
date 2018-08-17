import re
import UTILS as u
import numpy as np
import pandas as pd


DOLLARS_DIVIDED = '../../../rcc-uchicago/PCNO/CSV/chicago/dollars_divided.csv'
HQ = '../../../rcc-uchicago/PCNO/CSV/chicago/Maps/map1.csv'
GEO = '../../../rcc-uchicago/PCNO/CSV/chicago/Geocoded Service Addresses/map2_geocoding_geocoded.csv'
MAP2_SATELLITES = '../../../rcc-uchicago/PCNO/CSV/chicago/Maps/map2_satellites.csv'
MAP2_HQ = '../../../rcc-uchicago/PCNO/CSV/chicago/Maps/map2_hq.csv'


def read_contracts():
    '''
    Reads in the contracts with HQ addresses; converts the zip codes to strings.
    Returns a dataframe.
    '''

    df = pd.read_csv(HQ,converters={'Zip':str})

    return df


def read_geo():
    '''
    Reads in the geocoded addresses for map 1. Drops the 'Match Score' column.
    Returns a dataframe.
    '''

    df = pd.read_csv(GEO)
    df = df.drop(['Match Score'],axis=1)

    return df


def read_dollars_divided():
    '''
    '''

    df = pd.read_csv(DOLLARS_DIVIDED,converters={'ZipCode_SVC':str})

    new_names = [re.sub('_SVC$','',x) for x in df.columns]
    cn = dict(zip(df.columns,new_names))

    df = df.rename(columns=cn,index=str)

    return df


def merger(dollars_divided,geo):
    '''
    '''

    df = u.merge_coalesce(dollars_divided,geo,'CSDS_Org_ID','_R','left')

    df = df.drop(['ClusterID','VendorName_LINK1','VendorName_LINK2','Name',
                  'CSDS_Vendor_ID_LINK2'],axis=1)

    return df


def separate_satellites(df):
    '''
    '''

    keep = ['CSDS_Vendor_ID','VendorName','CSDS_Org_ID','Address','City',
            'State','ZipCode','Longitude','Latitude','Dollars_Per_Location']

    satellites = merged[merged['HQ_Flag'] == 0]

    return satellites[keep].reset_index(drop=True)


def separate_hq(merged):
    '''
    '''

    keep = ['CSDS_Vendor_ID','VendorName','Agency_Summed_Amount',
            'Num_Svc_Locations','Address','City','State','ZipCode','Longitude',
            'Latitude','Dollars_Per_Location']

    hq = merged[merged['HQ_Flag'] == 1]

    return hq[keep].reset_index(drop=True)


if __name__ == '__main__':

    dollars_divided = read_dollars_divided()
    geo = read_geo()

    merged = merger(dollars_divided,geo)

    satellites = separate_satellites(merged)
    satellites.to_csv(MAP2_SATELLITES,index=False)

    hq = separate_hq(merged)
    hq.to_csv(MAP2_HQ,index=False)

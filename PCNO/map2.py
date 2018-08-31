import re
import UTILS as u
import numpy as np
import pandas as pd


DOLLARS_DIVIDED = '../../../rcc-uchicago/PCNO/CSV/chicago/dollars_divided.csv'
GEO1 = '../../../rcc-uchicago/PCNO/CSV/chicago/Geocoded Service Addresses/map2_geocoding_geocoded.csv'
GEO2 = '../../../rcc-uchicago/PCNO/CSV/chicago/Geocoded Service Addresses/map2_geocoding_version2_geocoded.csv'
GEO3 = '../../../rcc-uchicago/PCNO/CSV/chicago/Geocoded Service Addresses/map2_geocoding_version3_geocoded.csv'
MAP2_SATELLITES = '../../../rcc-uchicago/PCNO/CSV/chicago/Maps/map2_satellites.csv'
MAP2_HQ = '../../../rcc-uchicago/PCNO/CSV/chicago/Maps/map2_hq.csv'


def read_geo():
    '''
    Reads in the geocoded addresses for map 1. Drops the 'Match Score' column.
    Returns a dataframe.
    '''
    cv = {'Zip':str}
    df1 = pd.read_csv(GEO1,converters=cv)
    df2 = pd.read_csv(GEO2,converters=cv)
    df3 = pd.read_csv(GEO3,converters=cv)

    df1 = df1.rename(columns={'CSDS_Org_ID':'ID'},index=str)

    df = pd.concat([df1,df2,df3])
    df = df.drop(['Match Score','ID'],axis=1)
    df = df.rename(columns={'Zip':'ZipCode'},index=str)

    df = df.drop_duplicates(subset=['Address','City','State'],keep='first')

    return df


def read_dollars_divided():
    '''
    Reads the dollars_divided file, converting the Zip fields to string.
    Returns a dataframe.
    '''

    df = pd.read_csv(DOLLARS_DIVIDED,converters={'ZipCode':str,'ZipCode_SVC':str})

    cols = ['Address','City','State','ZipCode','Longitude','Latitude']
    dicto = dict([((x, x + '_HQ')) for x in cols])
    df = df.rename(columns=dicto,index=str)

    #'''
    new_names = [re.sub('_SVC$','',x) for x in df.columns]
    cn = dict(zip(df.columns,new_names))

    df = df.rename(columns=cn,index=str)

    return df


def merger(dollars_divided,geo):
    '''
    Merges the dollars_divided and geo dataframes, coalescing the values across
    matching columns. Drops unwanted columns. Returns a dataframe.
    '''

    keys = ['Address', 'City', 'State', 'ZipCode']
    sfx = '_R'
    how = 'left'

    df = u.merge_coalesce(dollars_divided,geo,keys,sfx,how)

    df = df.drop(['ClusterID','VendorName_LINK1','VendorName_LINK2','Name',
                  'CSDS_Vendor_ID_LINK2'],axis=1)

    subset = ['CSDS_Vendor_ID','Address','City','State','ZipCode']

    return df.drop_duplicates(subset=subset).reset_index(drop=True)


def separate_satellites(merged):
    '''
    Makes the dataframe for the map 2 satellite file: Separates satellite
    records, drops unwanted columns, and changes the order of the rest of the
    columns. Returns a dataframe.
    '''

    keep = ['CSDS_Vendor_ID','VendorName','CSDS_Org_ID','Address','City',
            'State','ZipCode','Longitude','Latitude','Dollars_Per_Location']

    satellites = merged[merged['HQ_Flag'] == 0]

    return satellites[keep].reset_index(drop=True)


def separate_hq(merged):
    '''
    Makes the dataframe for the map 2 HQ file: Separates HQ records, drops
    unwanted columns, and changes the order of the rest of the columns. Returns
    a dataframe.
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

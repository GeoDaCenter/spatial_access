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

    # Read in the geocoded files, converting Zip to string
    cv = {'Zip':str}
    df1 = pd.read_csv(GEO1,converters=cv)
    df2 = pd.read_csv(GEO2,converters=cv)
    df3 = pd.read_csv(GEO3,converters=cv)

    # Rename a column to match the others
    df1 = df1.rename(columns={'CSDS_Org_ID':'ID'},index=str)

    # Concatenate the geocoded dataframes together, then drop two columns and
    # rename a third
    df = pd.concat([df1,df2,df3])
    df = df.drop(['Match Score','ID'],axis=1)
    df = df.rename(columns={'Zip':'ZipCode'},index=str)

    # Drop duplicates based on this subset of columns; zip is excluded because
    # some addresses have the wrong zip and we only want to keep one record of
    # each address
    df = df.drop_duplicates(subset=['Address','City','State'],keep='first')

    return df


def read_dollars_divided():
    '''
    Reads the dollars_divided file, converting the Zip fields to string.
    Returns a dataframe.
    '''

    # Reads in the dollars_divided file, converting Zip codes to strings
    df = pd.read_csv(DOLLARS_DIVIDED,converters={'ZipCode':str,'ZipCode_SVC':str})

    # Renames columns to add '_HQ' to these fields
    cols = ['Address','City','State','ZipCode','Longitude','Latitude']
    dicto = dict([((x, x + '_HQ')) for x in cols])
    df = df.rename(columns=dicto,index=str)

    # Renames columns to trim off '_SVC'
    new_names = [re.sub('_SVC$','',x) for x in df.columns]
    cn = dict(zip(df.columns,new_names))
    df = df.rename(columns=cn,index=str)

    return df


def merger(dollars_divided,geo):
    '''
    Merges the dollars_divided and geo dataframes, coalescing the values across
    matching columns. Drops unwanted columns. Returns a dataframe.
    '''

    # Define the arguments to merge_coalesce
    keys = ['Address', 'City', 'State', 'ZipCode']
    sfx = '_R'
    how = 'left'

    # Merge dollars_divided and geo together, filling in coordinates
    df = u.merge_coalesce(dollars_divided,geo,keys,sfx,how)

    # Drop these columns
    df = df.drop(['ClusterID','VendorName_LINK1','VendorName_LINK2','Name',
                  'CSDS_Vendor_ID_LINK2'],axis=1)

    # Drop duplicates based only on this subset
    subset = ['CSDS_Vendor_ID','Address','City','State','ZipCode']

    return df.drop_duplicates(subset=subset).reset_index(drop=True)


def separate_satellites(merged):
    '''
    Makes the dataframe for the map 2 satellite file: Separates satellite
    records, drops unwanted columns, and changes the order of the rest of the
    columns. Returns a dataframe.
    '''

    # Define the columns to keep and their order
    keep = ['CSDS_Vendor_ID','VendorName','CSDS_Org_ID','Address','City',
            'State','ZipCode','Longitude','Latitude','Dollars_Per_Location']

    # Keep only records with HQ_Flag == 0
    satellites = merged[merged['HQ_Flag'] == 0]

    return satellites[keep].reset_index(drop=True)


def separate_hq(merged):
    '''
    Makes the dataframe for the map 2 HQ file: Separates HQ records, drops
    unwanted columns, and changes the order of the rest of the columns. Returns
    a dataframe.
    '''

    # Define the columns to keep and their order
    keep = ['CSDS_Vendor_ID','VendorName','Agency_Summed_Amount',
            'Num_Svc_Locations','Address','City','State','ZipCode','Longitude',
            'Latitude','Dollars_Per_Location']

    # Keep only records with HQ_Flag == 1
    hq = merged[merged['HQ_Flag'] == 1]

    return hq[keep].reset_index(drop=True)


if __name__ == '__main__':

    # Read in the dollars_divided and geocoded files
    dollars_divided = read_dollars_divided()
    geo = read_geo()

    # Merge them together
    merged = merger(dollars_divided,geo)

    # Separate the satellite records and write to CSV
    satellites = separate_satellites(merged)
    satellites.to_csv(MAP2_SATELLITES,index=False)

    # Separate the HQ addresses and write to CSV
    hq = separate_hq(merged)
    hq.to_csv(MAP2_HQ,index=False)

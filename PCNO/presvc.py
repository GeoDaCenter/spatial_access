import UTILS as u
import numpy as np
import pandas as pd
import MATCH_NAMES as mn
import ADDRESS_CLEANER as ac
import IMPORT_ADDRESSES as ad
import SERVICE_ADDRESS_CLEANER as sac
from SERVICE_STANDARDIZE_NAME import stdname


GEO = '../../../rcc-uchicago/PCNO/CSV/chicago/Geocoded Service Addresses/map1_addresses_geocoded.csv'
AGENCIES = '../../../rcc-uchicago/PCNO/CSV/chicago/service_agencies.csv'
NAMES = '../../../rcc-uchicago/PCNO/CSV/chicago/service_agencies_names.csv'

def merger():
    '''
    Imports the four datasets and merges them together. Returns a single
    dataframe.
    '''

    strings = ['pb','westchi','dfss','mapscorps']
    dfs = []

    for string in strings:
        print('\nReading in {} dataset(s)'.format(string.upper()))
        df = import_svc_addr(string)
        dfs.append(df)

    merged = pd.concat(dfs)

    return merged.replace(np.NaN,'')


def import_svc_addr(dataset):
    '''
    Imports a single dataset as determined by the input string. Drops certain
    columns for each dataset. Drops duplicates and resets the index. Returns a
    single dataframe.
    '''

    if dataset == 'pb':
        df = ad.read_pb()
        df = df[df.State == 'IL']
        df = df.drop('CommunityArea',axis=1)

    elif dataset == 'westchi':
        df = ad.read_wchi()
        df = df.drop(['Phone','Ward','CommunityArea'],axis=1)

    elif dataset == 'dfss':
        df = ad.read_dfss()
        drop = ['SiteName','Phone','Ward','CommunityAreaName','CommunityArea']
        df = df.drop(drop,axis=1)

    elif dataset == 'mapscorps':
        df = ad.read_mc()
        keep = ['Name','Address1','Address2','City','State','ZipCode','CSDS_Org_ID']
        df = df[keep]

    return df.drop_duplicates().reset_index(drop=True)


def clean_df(df):
    '''
    Standardizes the organization name, then cleans the address fields. Keeps
    only records in IL. Returns a dataframe.
    '''

    print('\nStandardizing names and cleaning addresses')

    df['Name'] = df['Name'].apply(stdname)

    df = sac.full_cleaning(df)

    df = df[df['State'] == 'IL']

    return df.reset_index(drop=True)


def filler(df,targets,type,keys1,keys2):
    '''
    Attempts to fill in missing values in the targets list from elsewhere in the
    dataset. The column names in keys1 should be the values on which two records
    must match exactly in order to fill in a missing value. The column names in
    keys2 are the ones that must be considered (in addition to the columns in
    keys1) when dropping duplicates from the dataframe. The type is the function
    (not a string) that should be applied to the columns in the target list.
    Returns a dataframe.
    '''

    bigkeys = keys1 + keys2

    # Make a copy of df but only keep the target columns plus those in keys1
    values = df.loc[:,targets + keys1]

    # For every column in the list of targets, change the type as specified
    # If the type is not string, replace the emptry string with np.NaN first
    for col in targets:
        if type == str:
            values.loc[:,col] = values.loc[:,col].astype(type)
        else:
            values.loc[:,col] = values.loc[:,col].replace('',np.NaN).astype(type)

    # Drop null values in the target values, then sort the values by the targets
    values = values.dropna(subset=targets)
    values = values.sort_values(by=targets,ascending=False)

    # Drop duplicates (considering only the columns in keys1); keep the first
    # row and drop subsequent duplicates
    values = values.drop_duplicates(subset=keys1,keep='first')

    # Drop the columns in the list of targets, then drop duplicates (considering
    # only the columns in keys1 + keys2); finally, merge in values with a left
    # merge so that all rows in df are retained (this fills in all the target
    # vals present in values)
    df = df.drop(targets,axis=1).drop_duplicates(subset=bigkeys).merge(values,how='left')

    return df.reset_index(drop=True)


def read_geo():
    '''
    Reads in the geocoded addresses from Map 1 (HQ addresses). Drops the Match
    Score column. Renames the Latitude and Longitude columns. Cleans the Zip
    column. Returns a dataframe.
    '''

    df = pd.read_csv(GEO)
    df = df.drop('Match Score',axis=1)

    #df = df.rename(columns={'Latitude':'Lat','Longitude':'Lon'},index=str)
    df = df.rename(columns={'Zip':'ZipCode'},index=str)

    df['ZipCode'] = df['ZipCode'].apply(u.fix_zip)

    return df


def try_fill(df):
    '''
    Fills in missing zip codes and coordinates as best as possible. Copies in
    values from elsewhere in the dataset and from the geocoded HQ addresses.
    Returns a dataframe.
    '''

    print('\nFilling in missing zip codes and coordinates as best as possible')

    # Fill in missing zip codes as best as possible
    #df = fill_zips(df)
    targetsZ = ['ZipCode']
    keys1Z = ['Address','City','State']
    keys2Z = ['Name','Longitude','Latitude']
    df = filler(df,targetsZ,str,keys1Z,keys2Z)

    # Fill in missing longitude and latitude coordinates as best as possible
    #df = fill_coords(df)
    targetsL = ['Longitude','Latitude']
    keys1L = ['Address','City','State','ZipCode']
    keys2L = ['Name']
    df = filler(df,targetsL,float,keys1L,keys2L)

    # Read in the geocoded HQ addresses and fill in zip codes and coordinates as
    # best as possible
    geo = read_geo()
    subset = ['Address','City','State']
    df = u.merge_coalesce(df.reset_index(drop=True),geo,subset)

    return df


def id_geocoded(df):
    '''
    Need to figure out what parts of this function to cannibalize LATER ON.
    Once the service addresses are merged into the contracts, THEN they should
    get a unique CSDS_Address_ID. For now, ignore everything in this function.
    '''

    keep = ['Longitude','Latitude','Address','City','Zip','State']
    geo1 = pd.read_csv(GEO)[keep + ['AddressID']]

    df = df.rename(columns={'ZipCode':'Zip'},index=str)

    for col in keep[0:2]:
        df[col] = df[col].replace('',np.NaN).apply(float)

    geo2 = df[keep].dropna(subset=keep[0:2],how='any')
    geo2 = geo2.drop_duplicates()
    geo2 = geo2.assign(AddressID = ['Addr_' + str(x + 1 + len(geo1)) for x in range(len(geo2))])

    geo = pd.concat([geo1,geo2])
    geo = geo.drop_duplicates(subset=keep[2:],keep='first')

    geo = geo.rename(columns={'Zip':'ZipCode'},index=str)

    return geo.reset_index(drop=True)


def just_names(df):
    '''
    Reduces the dataframe to unique entries in the Name column. Returns a
    dataframe.
    '''

    names = df[['Name']].drop_duplicates().reset_index(drop=True)

    names = names.rename(columns={'Name':'VendorName'},index=str)

    names = names.assign(CSDS_Svc_ID=['SvcAg_' + str(x + 1) for x in range(len(names))])

    return names


def merge_ids(df,names):
    '''
    '''

    names = names.rename(columns={'VendorName':'Name'},index=str)

    df = df.merge(names,how='left')

    return df


if __name__ == '__main__':

    #'''
    merged = merger()
    cleaned = clean_df(merged)
    filled = try_fill(cleaned)

    names = just_names(filled)
    names.to_csv(NAMES,index=False)

    identified = merge_ids(filled,names)
    identified.to_csv(AGENCIES,index=False)

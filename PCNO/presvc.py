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
    Imports the four datasets (PURPLEBINDER, WESTCHI, DFSSS, and MAPSCORPS) and
    merges them together. Returns a single dataframe.
    '''

    # A list of the dataset names
    strings = ['pb','westchi','dfss','mapscorps']

    # Initialize an empty list to hold the dataframes
    dfs = []

    # For every dataset in the list of dataset names:
    for string in strings:
        # Print progress report
        print('\nReading in {} dataset(s)'.format(string.upper()))
        # Read in the dataset
        df = import_svc_addr(string)
        # Append the newly read dataframe to the list
        dfs.append(df)

    # Concatenate the dataframes
    merged = pd.concat(dfs)

    # Replace np.NaN with the empty string
    return merged.replace(np.NaN,'')


def import_svc_addr(dataset):
    '''
    Imports a single dataset as determined by the input string. Drops certain
    columns for each dataset. Drops duplicates and resets the index. Returns a
    single dataframe.
    '''

    # Read in the PURPLEBINDER dataset
    if dataset == 'pb':
        df = ad.read_pb()
        # Keep only records in Illinois
        df = df[df.State == 'IL']
        # Drop the CommunityArea column
        df = df.drop('CommunityArea',axis=1)

    # Read in the WESTCHI dataset
    elif dataset == 'westchi':
        df = ad.read_wchi()
        # Drop these columns
        df = df.drop(['Phone','Ward','CommunityArea'],axis=1)

    # Read in the DFSS dataset
    elif dataset == 'dfss':
        df = ad.read_dfss()
        # Drop these columns
        drop = ['SiteName','Phone','Ward','CommunityAreaName','CommunityArea']
        df = df.drop(drop,axis=1)

    # Read in the MAPSCORPS dataset
    elif dataset == 'mapscorps':
        df = ad.read_mc()
        # Keep only these columns in this order
        keep = ['Name','Address1','Address2','City','State','ZipCode','CSDS_Org_ID']
        df = df[keep]

    # Drop duplicates and reset the index
    return df.drop_duplicates().reset_index(drop=True)


def clean_df(df):
    '''
    Standardizes the organization name, then cleans the address fields. Keeps
    only records in IL. Returns a dataframe.
    '''

    # Print progress report
    print('\nStandardizing names and cleaning addresses')

    # Standardize names
    df['Name'] = df['Name'].apply(stdname)

    # Clean service addresses
    df = sac.full_cleaning(df)

    # Keep only records with the address in Illinois
    df = df[df['State'] == 'IL']

    # Reset the index
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

    # Concatenate the lists of keys
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

    # Read in the geocoded addresses and drop a column
    df = pd.read_csv(GEO)
    df = df.drop('Match Score',axis=1)

    # Rename a column
    df = df.rename(columns={'Zip':'ZipCode'},index=str)

    # Fix the values in the ZipCode column
    df['ZipCode'] = df['ZipCode'].apply(u.fix_zip)

    return df


def try_fill(df):
    '''
    Fills in missing zip codes and coordinates as best as possible. Copies in
    values from elsewhere in the dataset and from the geocoded HQ addresses.
    Returns a dataframe.
    '''

    # Print progress report
    print('\nFilling in missing zip codes and coordinates as best as possible')

    # Fill in missing zip codes as best as possible
    targetsZ = ['ZipCode']
    keys1Z = ['Address','City','State']
    keys2Z = ['Name','Longitude','Latitude']
    df = filler(df,targetsZ,str,keys1Z,keys2Z)

    # Fill in missing longitude and latitude coordinates as best as possible
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


def just_names(df):
    '''
    Reduces the dataframe to unique entries in the Name column. Returns a
    dataframe.
    '''

    # Take only the Name column, drop duplicates, and reset the index
    names = df[['Name']].drop_duplicates().reset_index(drop=True)

    # Rename the column
    names = names.rename(columns={'Name':'VendorName'},index=str)

    # Add a service agency ID column
    names = names.assign(CSDS_Svc_ID=['SvcAg_' + str(x + 1) for x in range(len(names))])

    return names


def merge_ids(df,names):
    '''
    Merges the CSDS_Svc_ID column into the names dataframe. Returns a dataframe.
    '''

    names = names.rename(columns={'VendorName':'Name'},index=str)

    df = df.merge(names,how='left')

    return df


if __name__ == '__main__':

    merged = merger()
    cleaned = clean_df(merged)
    filled = try_fill(cleaned)

    names = just_names(filled)
    names.to_csv(NAMES,index=False)

    identified = merge_ids(filled,names)
    identified.to_csv(AGENCIES,index=False)

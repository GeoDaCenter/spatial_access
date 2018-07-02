import numpy as np
import pandas as pd
import ADDRESS_CLEANER as ac
import IMPORT_ADDRESSES as ad
import SERVICE_ADDRESS_CLEANER as sac
from SERVICE_STANDARDIZE_NAME import stdname


GEO = '../../../PCNO/CSV/chicago/Geocoded Service Addresses/map1_addresses_geocoded.csv'


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

    df['Name'] = df['Name'].apply(stdname)

    df = sac.full_cleaning(df)

    df = df[df['State'] == 'IL']

    return df.reset_index(drop=True)


def id_geocoded(df):
    '''

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


def fill_zips(df):
    '''
    Fills ins blank zip codes if the same address has a known zip code in a
    different record. In the case that the same address has 2+ different zip
    codes across records, retains the highest-numbered zip. Returns a dataframe.
    '''

    zipc = 'ZipCode'
    subset = ['Address','City','State']

    # Make a copy of df but only keep the columns 'ZipCode' plus those in subset
    zips = df.loc[:,(subset + [zipc])]

    # Replace empty zips with np.NaN
    zips[zipc] = zips[zipc].replace('',np.NaN)

    # Drop null values in the zip column; sort with higher-numbered zips first
    zips = zips.dropna(subset=[zipc])
    zips = zips.sort_values(by=zipc,ascending=False)

    # Considering only the columns in subset, drop subsequent duplicates
    zips = zips.drop_duplicates(subset=subset,keep='first')

    # Drop the ZipCode column, then drop duplicates (considering only the col)
    # Merge zips into df using a left join, which fills in zips for records
    # based on matching on the columns in subset

    print(df.columns)
    df = df.drop(['ZipCode'],axis=1).drop_duplicates(subset=subset + ['Name',\
           'Longitude','Latitude']).merge(zips,how='left')

    return df.reset_index(drop=True)


def fill_coords(df):
    '''
    Fills in longitude and latitude coordinates for addresses that have them. In
    the case of a tie, takes the record with the highest value for longitude.
    Returns a dataframe.
    '''

    subset = ['Address','City','ZipCode','State','Longitude','Latitude']

    coords = df.loc[:,subset]

    for col in subset[-2:]:
        df[col] = df[col].replace('',np.NaN).apply(float)

    coords = coords.dropna(subset=subset[-2:])
    coords = coords.sort_values(by=subset[-2:],ascending=False)

    coords = coords.drop_duplicates(subset=subset[:-2],keep='first')

    df = df.drop(subset[-2:],axis=1).drop_duplicates(subset=subset[:-2] + ['Name']).merge(coords,how='left')

    return df.reset_index(drop=True)


def thinner(df):
    '''
    '''

    # Fill in missing zip codes as best as possible
    df = fill_zips(df)

    # Fill in missing longitude and latitude coordinates as best as possible
    df = fill_coords(df)

    return df


if __name__ == '__main__':

    #'''
    merged = merger()
    cleaned = clean_df(merged)
    #cleaned.to_csv('SVC_AGENCIES.csv',index=False)


    thin = thinner(cleaned)
    geo = id_geocoded(thin)
    #'''

    print()


    '''
    -Copy Long,Lat in for identical addresses
    -Boil down to single line per identical record

    -Deduplicate based on name and address
    -Assign an address ID to each unique address
    -If there's a geocoded address, copy the coordinates to matching addresses
    -Geocode the rest of the addresses
    -Merge the coordinates back in

    -Then:  Record Linkage to HQ addresses
    '''

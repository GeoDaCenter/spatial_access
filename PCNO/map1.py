import numpy as np
import pandas as pd


HQ = '../../../rcc-uchicago/PCNO/CSV/chicago/contracts_w_hq_addresses.csv'
GEO = '../../../rcc-uchicago/PCNO/CSV/chicago/Geocoded Service Addresses/map1_addresses_geocoded.csv'
MAP1 = '../../../rcc-uchicago/PCNO/CSV/chicago/Maps/map1.csv'


def read_geo():
    '''
    Reads in the geocoded addresses for map 1. Drops the 'Match Score' column.
    Returns a dataframe.
    '''

    # Read in the geocoded file; convert Zip to string
    df = pd.read_csv(GEO,converters={'Zip':str})

    # Drop these columns
    df = df.drop(['Match Score','AddressID'],axis=1)

    return df


def read_contracts():
    '''
    Reads in the contracts with headquarter addresses. Returns a dataframe.
    '''

    # Read in the contracts with HQ addresses; convert Zip to string
    df = pd.read_csv(HQ,converters={'Zip':str})

    # Keep only records where the state is IL
    df = df[df['State'] == 'IL']

    return df


def sum_amounts(df):
    '''
    Takes in a dataframe. Adds a column with the sum of the amounts by vendor
    ID. Returns a dataframe.
    '''

    # Create a trimmed version of the dataframe with only these columns
    df_trimmed = df[['CSDS_Vendor_ID','CSDS_Contract_ID','Amount']]
    df_trimmed = df_trimmed.drop_duplicates()

    # Add up the amounts by vendor ID
    summer = df_trimmed.groupby('CSDS_Vendor_ID')['Amount'].sum()
    summer.name = 'Summed_Amount'
    summer = summer.to_frame().reset_index()

    # Merge the summed amounts in
    df = df.merge(summer,on='CSDS_Vendor_ID',how='right')

    # Keep these columns in this order
    df = df[['CSDS_Vendor_ID','Summed_Amount','VendorName','VendorID','Address',
             'City','State','Zip']]

    return df.drop_duplicates().reset_index(drop=True)


def merge():
    '''
    Reads in the geocoded headquarter addresses and the contracts. Gets the sum
    of amounts by vendor ID. Merges the dataframes together and returns a
    dataframe.
    '''

    # Read in the geocoded addresses
    geo = read_geo()

    # Read in the contracts, then get their summed amounts by vendor ID
    contracts = read_contracts()
    summed = sum_amounts(contracts)

    # Merge the dataframe with the summed amounts and the geocoding together
    df = summed.merge(geo,how='inner')

    # Keep these columns in this order
    df = df[['Summed_Amount','CSDS_Vendor_ID','Address','City','State','Zip',
             'Longitude','Latitude','VendorName']]

    return df.drop_duplicates().reset_index(drop=True)


if __name__ == '__main__':

    merged = merge()
    merged.to_csv(MAP1,index=False)

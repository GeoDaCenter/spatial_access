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

    df = pd.read_csv(GEO)
    df = df.drop(['Match Score','AddressID'],axis=1)

    return df


def read_contracts():
    '''
    Reads in the contracts with headquarter addresses. Returns a dataframe.
    '''

    df = pd.read_csv(HQ)

    return df


def sum_amounts(df):
    '''
    Takes in a dataframe. Adds a column with the sum of the amounts by vendor
    ID. Returns a dataframe.
    '''

    summer = df.groupby('CSDS_Vendor_ID')['Amount'].sum()
    summer = summer.to_frame().reset_index()

    df = df.merge(summer,how='right')

    return df


def merge():
    '''
    Reads in the geocoded headquarter addresses and the contracts. Gets the sum
    of amounts by vendor ID. Merges the dataframes together and returns a
    dataframe.
    '''

    geo = read_geo()

    contracts = read_contracts()
    summed = sum_amounts(contracts)

    df = summed.merge(geo)

    return df[['Amount','CSDS_Vendor_ID','Address','City','State','Zip',
               'Longitude','Latitude','VendorName']]


if __name__ == '__main__':

    merged = merge()
    merged.to_csv(MAP1,index=False)

import numpy as np
import pandas as pd


HQ = '../../../rcc-uchicago/PCNO/CSV/chicago/contracts_w_hq_addresses.csv'
GEO = '../../../rcc-uchicago/PCNO/CSV/chicago/Geocoded Service Addresses/map1_addresses_geocoded.csv'
CATEGORIES = '../../../rcc-uchicago/PCNO/Rule-based classification/chi_cook_il_classified.csv'
MAP1B = '../../../rcc-uchicago/PCNO/CSV/chicago/Maps/map1b.csv'


def read_geo():
    '''
    Reads in the geocoded addresses for map 1. Drops the 'Match Score' column.
    Returns a dataframe.
    '''

    df = pd.read_csv(GEO,converters={'Zip':str})
    df = df.drop(['Match Score','AddressID'],axis=1)

    return df


def read_contracts():
    '''
    Reads in the contracts with headquarter addresses. Returns a dataframe.
    '''

    df = pd.read_csv(HQ,converters={'Zip':str})
    df = df[df['State'] == 'IL']

    return df


def read_categories():
    '''
    Reads in the service-code classifications for the contracts. Returns a
    dataframe.
    '''

    df = pd.read_csv(CATEGORIES)
    df = df[['Classification','Contract Number']]
    df = df.rename(columns={'Contract Number':'ContractNumber'},index=str)

    return df


def merge():
    '''
    Reads in the geocoded headquarter addresses, the contracts, and the service
    classifications. Merges the dataframes together. Returns a dataframe.
    '''

    geo = read_geo()

    contracts = read_contracts()

    cats = read_categories()

    df = contracts.merge(geo)
    df = df.merge(cats)

    df = df.drop('AddressID',axis=1)

    return df.drop_duplicates().reset_index(drop=True)


if __name__ == '__main__':

    merged = merge()
    merged.to_csv(MAP1B,index=False)

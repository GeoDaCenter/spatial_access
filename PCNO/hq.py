import re
import numpy as np
import pandas as pd


PREHQ = '../../../PCNO/CSV/chicago/prehq_contracts.csv'
HQ = '../../../PCNO/CSV/chicago/contracts_w_hq_addresses.csv'
DEDUPED = '../../../PCNO/Geo/deduped_contract_results.csv'
ADDR_OUT = '../../../PCNO/CSV/chicago/map1_addresses_for_geocoding.csv'


def read_deduplicated():
    '''
    Reads in the contracts with deduplicated vendor names. Drops the Address2
    and index columns. Renames columns. Fixes zip codes by converting floats to
    strings and dropping +4s. Replaces 'INVALID' values with the empty string.
    Returns a dataframe.
    '''

    df = pd.read_csv(DEDUPED)
    df = df.drop(['Address2','Unnamed: 0'],axis=1)
    df = df.rename(columns={'Address1':'Address','ZipCode':'Zip'},index=str)

    # Fix ZipCodes
    df['Zip'] = df['Zip'].apply(lambda x: re.sub(r'\.0$','',str(x)))
    df['Zip'] = df['Zip'].apply(lambda x: re.sub(r'-[0-9]{4}$','',x))

    df = df.replace('INVALID','')

    return df


def best_address(df):
    '''
    Takes the most common address for each deduplicated vendor name. If there is
    a tie for most common address, takes the first address. Returns a dataframe
    with vendor ID and the best address.
    '''

    # Shortcut
    vdr = 'CSDS_Vendor_ID'

    # Get the number of times each address appears for each vendor ID
    counts = df.groupby(vdr)['Address'].value_counts()#nunique()
    counts.name = 'AddressFrequency'
    counts = counts.to_frame().reset_index()
    counts = counts.sort_values(by=['AddressFrequency'],ascending=False)

    # Get the max number of times an address appears for each vendor ID
    max_count = counts.groupby([vdr,'Address']).max()
    max_count = max_count.rename(columns={'AddressFrequency':'MostCommonAddressAppears#'},index=str)
    max_count = max_count.reset_index()

    # Merge the dataframes so that we keep only the most common values
    merger = counts.merge(max_count,how='inner')
    merger = merger.reset_index()

    # This takes the first address for each vendor, so if there's a tie between
    # 2+ addresses for most common, this breaks the tie
    merger = merger.groupby(vdr).first()
    merger = merger.reset_index()

    # Merge the addresses back in on a left join to drop the vendors with no
    # address information at all
    df = df.merge(merger,how='inner')

    # Keep only these fields and drop duplicates
    df = df[['CSDS_Vendor_ID','Address','City','State','Zip']].drop_duplicates()

    # Drop records with no address, then reset index
    df = df.dropna(subset=['Address'])
    df = df.reset_index(drop=True)

    # Make a dataframe with just these fields; drop duplicates; assign an ID
    addresses_only = df[['Address','City','State','Zip']].drop_duplicates()
    addresses_only = addresses_only.assign(AddressID=['Addr_' + str(x + 1) for x in range(len(addresses_only))])

    # Merge the address IDs in
    df = df.merge(addresses_only,how='left')

    return df


def apply_hq_address(results,best_addr):
    '''
    Takes in the results and best_address dataframes and merges them on vendor
    ID. Drops records without an address. Returns a dataframe.
    '''

    # Shortcut
    cols = ['Address','City','State','Zip']

    # Drop the columns in cols, then drop duplicates; copy to a new dataframe
    df = results.drop(cols,axis=1).drop_duplicates()

    # Merge in the best addresses (inner so that it only keeps records for which
    # there is a headquarter address)
    merged = df.merge(best_addr,how='inner')

    return merged


def just_addresses(best_addr):
    '''
    Takes in a dataframe of headquarter addresses with vendor IDs and reduces it
    to just addresses. Returns a dataframe.
    '''

    df = best_addr.drop('CSDS_Vendor_ID',axis=1).drop_duplicates()

    return df

if __name__ == '__main__':

    results = read_deduplicated()

    best_addr = best_address(results)

    merged = apply_hq_address(results,best_addr)
    merged.to_csv(HQ,index=False)

    addresses = just_addresses(best_addr)
    addresses.to_csv(ADDR_OUT,index=False)

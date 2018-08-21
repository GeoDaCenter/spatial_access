import numpy as np
import pandas as pd
import ADDRESS_CLEANER as ac


IRS = '../../../rcc-uchicago/PCNO/Matching/CHICAGO_IRS990_2013-2016_reshaped.csv'
GEO = '../../../rcc-uchicago/PCNO/CSV/chicago/map4_for_geocoding.csv'


def read_irs():
    '''
    Reads in the IRS records. Converts the ZipCode field to string and drops
    unwanted columns. Adds a unique ID for each organization. Cleans addresses,
    then renames columns and drops one last field. Returns a dataframe.
    '''

    # Define tthe columns to keep
    keep = ['EIN','OrganizationName','Address1','Address2','City','State','ZipCode']

    df = pd.read_csv(IRS,converters={'ZipCode':str})
    # Do this at the end instead of at the beginning

    # Keep the desired columns
    df = df[keep].drop_duplicates().reset_index(drop=True)

    # Add a unique ID
    df['CSDS_Org_ID'] = ['IRS' + str(x + 1) for x in range(len(df))]

    # Rename columns
    df = df.rename(columns={'OrganizationName':'VendorName'},index=str)

    # Send df through the round2 address cleaner
    df = ac.round2(df)

    # Now send the address column through the round-1 adress cleaner
    df['Address1'] = df['Address1'].apply(ac.address_cleaner)

    # Rename some addresses and drop a column
    df = df.rename(columns={'Address1':'Address','ZipCode':'Zip'},index=str).drop('Address2',axis=1)

    return df


def just_addresses(df):
    '''
    Reduces the IRS records to just addresses (which will be geocoded). Returns
    a dataframe.
    '''

    addresses = df[['Address','City','State','Zip','CSDS_Org_ID']]
    addresses = addresses.drop_duplicates(subset=['Address','City','State','Zip'])
    addresses = addresses[addresses['Address'] != '']
    addresses = addresses.rename(columns={'CSDS_Org_ID':'ID'},index=str)

    return addresses.reset_index(drop=True)


if __name__ == '__main__':

    irs = read_irs()

    addresses = just_addresses(irs)
    addresses.to_csv(GEO,index=False)

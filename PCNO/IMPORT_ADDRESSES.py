import numpy as np
import pandas as pd
import DFSS as dfss
import WESTCHI as wc
import MAPSCORPS as mc
import PURPLEBINDER as pb
import ADDRESS_CLEANER as ac
from STANDARDIZE_NAME import standardize_name as stdname


COOK_ADDR = '../../../rcc-uchicago/PCNO/CSV/chicago/CookCtyAddresses-for_geocoding.csv'
IL_ADDR = '../../../rcc-uchicago/PCNO/CSV/chicago/il_vendors_by_hand.csv'
IRS = '../../../rcc-uchicago/PCNO/Matching/CHICAGO_IRS990_2013-2016_reshaped.csv'
PB = '../../../rcc-uchicago/PCNO/Matching/originals/pb_programs.json'
WCHI = '../../../rcc-uchicago/PCNO/Matching/originals/WestChicagoResources_Apr2017f1.csv'
DFSS = '../../../rcc-uchicago/PCNO/Matching/originals/Family_and_Support_Services_Delegate_Agencies.csv'
MC = '../../../rcc-uchicago/PCNO/Matching/originals/TalenE_UC_AllChi.xlsx'
MC_2009_2015 = '2009-2015 data'
MC_2016 = '2016 data'


def read_il_addr():
    '''
    Reads in the hand-collected Illinois State addresses (only the ones for
    which there was not a match in the IRS data). Returns a dataframe.
    '''

    # Not sending to the address cleaner because these were hand-cleaned
    # SEND TO THE ADDRESS CLEANER ANYWAY
    il_addr = pd.read_csv(IL_ADDR,converters={'Address1':ac.address_cleaner})

    # Keep only these columns
    il_addr = il_addr[['VendorName','Address1','Address2','City','State','ZipCode']]

    return il_addr


def read_cook_addr():
    '''
    Reads in the hand-collected Cook County addresses, renames columns, and
    inserts an address2 column. Cleans the addresses. Returns a dataframe.
    '''

    cook_addr = pd.read_csv(COOK_ADDR,converters={'Address':ac.address_cleaner})

    cook_addr = cook_addr.rename(columns={'Address':'Address1','Zip':'ZipCode'})
    cook_addr['Address2'] = ''

    cook_addr = ac.round2(cook_addr)

    return cook_addr


def read_irs():
    '''
    Reads in the previously parsed and reshaped IRS data, then reassigns the
    internal organization ID. Drops columns. Returns a dataframe.
    '''

    keep = ['OrganizationName','Address1','Address2','City','State','ZipCode']

    df = pd.read_csv(IRS)
    # Do this at the end instead of at the beginning
    #converters={'Address1':ac.address_cleaner,'Address2':ac.address_cleaner}

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

    return df


def read_pb():
    '''
    Imports the PurpleBinder dataset. Drops rows with no location info at all.
    Assigns an ID. Returns a dataframe.
    '''

    df = pb.import_pb(PB)

    # If there is no location info at all for a record, drop it
    drop_cols = ['Address1','Address2','City','State','ZipCode','Latitude','Longitude']
    df = df.dropna(subset=drop_cols,how='all').drop_duplicates().reset_index(drop=True)

    # Create a sequential CSDS org ID for each record
    df = df.assign(CSDS_Org_ID=['PB' + str(x + 1) for x in range(len(df))])

    return df


def read_wchi():
    '''
    Imports the West Chicago resources dataset. Assigns an ID. Returns a
    dataframe.
    '''

    df = wc.import_wchi(WCHI)
    df = df.assign(CSDS_Org_ID=['WCHI' + str(x + 1) for x in range(len(df))])

    return df


def read_dfss():
    '''
    Reads in the DFSS dataset. Assigns an ID. Returns a dataframe.
    '''

    df = dfss.import_dfss(DFSS)
    df = df.assign(CSDS_Org_ID=['DFSS' + str(x + 1) for x in range(len(df))])

    return df


def read_mc():
    '''
    Reads in the MapsCorps datasets. Assigns an ID. Returns a single dataframe.
    '''

    df1 = mc.import_mc(MC,MC_2009_2015)
    df2 = mc.import_mc(MC,MC_2016)

    df = pd.concat([df1,df2])

    df = df.assign(CSDS_Org_ID=['MC' + str(x + 1) for x in range(len(df))])

    return df

import UTILS as u
import numpy as np
import pandas as pd


DEDUPED = '../../../rcc-uchicago/PCNO/CSV/chicago/2018-07-03_link_agencies_output.csv'
HQ = '../../../rcc-uchicago/PCNO/CSV/chicago/contracts_w_hq_addresses.csv'
SVC = '../../../rcc-uchicago/PCNO/CSV/chicago/service_agencies.csv'

THRESH = 0.34


def linker():
    '''
    '''

    link = read_deduplicated()
    link1 = link.rename(columns={'VendorName':'VendorName_LINK1'},index=str)
    link2 = u.rename_cols(link,['VendorName','CSDS_Vendor_ID'],'_LINK2')

    df = link1.merge(link2,how='left')
    df = df[df['CSDS_Vendor_ID'] != df['CSDS_Vendor_ID_LINK2']].reset_index(drop=True)

    return df


def merger():
    '''
    '''

    link = linker()
    hq = read_hq()
    svc = read_svc()

    merged = hq.merge(link,how='left').merge(svc,how='left')

    return merged


def read_hq():
    '''
    '''

    df = pd.read_csv(HQ,converters={'Zip':str})

    return df


def read_svc():
    '''
    '''

    df = pd.read_csv(SVC,converters={'ZipCode':str})
    df = u.rename_cols(df,[x for x in df.columns if x != 'CSDS_Svc_ID'],'_SVC')
    df = df.rename(columns={'CSDS_Svc_ID':'CSDS_Vendor_ID_LINK2'},index=str)

    return df


def read_deduplicated():
    '''
    '''

    df = pd.read_csv(DEDUPED,converters={'ClusterID':int})

    df = df[df['LinkScore'] >= THRESH]

    df = df.drop(['LinkScore','SourceFile'],axis=1)

    return df


def agg_funds(hq):
    '''
    '''

    agg = hq.groupby('CSDS_Vendor_ID')['Amount'].sum().reset_index()

    return agg


def count_svc_addr(df):
    '''
    '''

    counts = df.groupby('ClusterID')['CSDS_Vendor_ID_LINK2'].value_counts()
    counts.name = 'WhatThisCounts'
    return counts


    return df


if __name__ == '__main__':

    merged = merger()






    '''
    $/agency @ service addresses



    CONTRACTAGENCIES [VendorName] LINK [Name] SERVICEAGENCIES



    *******
    Problem:  Single locations are defined by multiple unique address strings, all the cleaning notwithstanding
    *******
    Options:
    -Geocode everything, then do float comparisons on the coordinates (or drop some that are within some tolerance of others)
    -Split up addresses with re and try to compare them
    -Split up addresses with the Usaddress library and try to compare them
    -Deduplicate with Logan's module (concatenate all to a single field first)
    -Deduplicate with the Dedupe library (I'll need to write a script that requires the CSDS_Agency_ID to match)
    '''

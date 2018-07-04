import UTILS as u
import numpy as np
import pandas as pd


DEDUPED = '../../../rcc-uchicago/PCNO/CSV/chicago/2018-07-03_link_agencies_output.csv'
HQ = '../../../rcc-uchicago/PCNO/CSV/chicago/contracts_w_hq_addresses.csv'
SVC = '../../../rcc-uchicago/PCNO/CSV/chicago/service_agencies.csv'

THRESH = 0.34


def merger():
    '''
    '''

    deduped = read_deduplicated()
    hq = read_hq()
    svc = read_svc()

    merged = hq.merge(deduped,how='left')

    #svc = svc.rename(columns={},index=str)

    #merged = merged.merge(svc,how='left')

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

    return df


def read_deduplicated():
    '''
    '''

    df = pd.read_csv(DEDUPED,converters={'ClusterID':str})

    df = df[df['LinkScore'] >= THRESH]

    df = df.drop(['LinkScore','SourceFile'],axis=1)

    df = u.rename_cols(df,['ClusterID','VendorName'],suffix='_LINK')

    return df


def merge_addresses(hq):
    '''
    '''

    amounts = agg_funds(hq)
    min_hq = minimize_hq(hq)

    df = min_hq.merge(amounts,how='left')

    return df


def minimize_hq(hq):
    '''
    '''

    df = hq[['VendorName','CSDS_Vendor_ID','Address','City','State','Zip',
             'AddressID']].drop_duplicates().reset_index(drop=True)

    return df


def agg_funds(hq):
    '''
    '''

    agg = hq.groupby('CSDS_Vendor_ID')['Amount'].sum().reset_index()

    return agg


if __name__ == '__main__':

    merged = merger()






    '''
    $/agency @ service addresses
    '''

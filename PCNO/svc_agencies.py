import re
import UTILS as u
import numpy as np
import pandas as pd
import COMPARE_ADDRESSES as ca


LINK = '../../../rcc-uchicago/PCNO/CSV/chicago/2018-07-03_link_agencies_output.csv'
HQ = '../../../rcc-uchicago/PCNO/CSV/chicago/contracts_w_hq_addresses.csv'
SVC = '../../../rcc-uchicago/PCNO/CSV/chicago/service_agencies.csv'
GEO = '../../../rcc-uchicago/PCNO/CSV/chicago/map2_geocoding.csv'
DOLLARS_DIVIDED = '../../../rcc-uchicago/PCNO/CSV/chicago/dollars_divided.csv'

THRESH = 0.34


def read_linker():
    '''
    Reads in the linked agencies file, retains matches >= the THRESH level, then
    drops two columns. Returns a dataframe.
    '''

    df = pd.read_csv(LINK,converters={'ClusterID':str})

    df = df[df['LinkScore'] >= THRESH]

    df = df.drop(['LinkScore','SourceFile'],axis=1)

    return df


def linker():
    '''
    Reads in the linker file (to link HQ agencies to service agencies). Merges a
    copy of itself on cluster ID, then eliminates records that match on vendor
    ID (to produce only matches that have different vendor IDs). Returns a
    dataframe.
    '''

    link = read_linker()
    link1 = link.rename(columns={'VendorName':'VendorName_LINK1'},index=str)
    link2 = u.rename_cols(link,['VendorName','CSDS_Vendor_ID'],'_LINK2')

    df = link1.merge(link2,how='left')
    df = df[df['CSDS_Vendor_ID'] != df['CSDS_Vendor_ID_LINK2']].reset_index(drop=True)

    return df

'''
def merger():

    link = linker()
    hq = read_hq()
    svc = read_svc()

    merged = hq.merge(link,how='left').merge(svc,how='left')

    return merged
'''


def dollars_per_location():
    '''
    Reads in the service agencies and the HQ agencies, then links them (using
    the linker dataframe). Calculates the number of dollars per location.
    Returns a dataframe.
    '''

    link = linker()
    svc = read_svc()
    hq = read_hq()[['CSDS_Vendor_ID','VendorName','Agency_Summed_Amount']].drop_duplicates()

    merged = hq.merge(link,how='left').merge(svc,how='left')

    merged = merged.assign(Dollars_Per_Location=merged['Agency_Summed_Amount']\
                           / (1 + merged['Num_Svc_Locations']))

    return merged.reset_index(drop=True)


def read_hq():
    '''
    Reads in the contracts with HQ addresses; converts the zip codes to strings.
    Adds up the contract amounts per agency. Returns a dataframe.
    '''

    df = pd.read_csv(HQ,converters={'Zip':str})
    agg_amounts = agg_funds(df)
    merged = df.merge(agg_amounts)

    return merged


def read_svc():
    '''
    Reads in the service agency addresses. Calls the COMPARE_ADDRESSES module to
    merge duplicate addresses per agency. Counts the number of service addresses
    per organization. Returns a dataframe.
    '''

    print('\nReading in service agencies')

    df = pd.read_csv(SVC,converters={'ZipCode':str})
    df = u.rename_cols(df,[x for x in df.columns if x != 'CSDS_Svc_ID'],'_SVC')
    df = df.rename(columns={'CSDS_Svc_ID':'CSDS_Vendor_ID_LINK2'},index=str)

    key = 'CSDS_Vendor_ID_LINK2'
    target = 'Address_SVC'
    fixed_addresses = ca.fix_duplicate_addresses(df,key,target)
    fixed_addresses = fixed_addresses.drop_duplicates(subset=[key,target])

    counts = count_svc_addr(fixed_addresses)
    merged = fixed_addresses.merge(counts)

    return merged.reset_index(drop=True)


def agg_funds(hq):
    '''
    Adds up the contract amounts per HQ agency. Returns a dataframe.
    '''

    agg = hq.groupby('CSDS_Vendor_ID')['Amount'].sum().reset_index()
    agg = agg.rename(columns={'Amount':'Agency_Summed_Amount'},index=str)

    return agg


def count_svc_addr(df):
    '''
    Counts the number of service addresses per agency. Returns a dataframe.
    '''

    df = df.assign(Constant=1)
    counts = df.groupby('CSDS_Vendor_ID_LINK2')['Constant'].count()
    counts.name = 'Num_Svc_Locations'

    return counts.to_frame().reset_index()


def separate_satellites(df):
    '''
    '''

    keep = ['CSDS_Vendor_ID','VendorName','CSDS_Org_ID_SVC','City_SVC',
            'State_SVC','ZipCode_SVC','Longitude_SVC','Latitude_SVC',
            'Address_SVC','Dollars_Per_Location']

    satellites = df.dropna(subset=['Num_Svc_Locations'])
    satellites = satellites[keep]

    new_names = [re.sub('_SVC$','',x) for x in keep]
    cn = dict(zip(keep,new_names))

    satellites = satellites.rename(columns=cn,index=str)

    return satellites.reset_index(drop=True)


def needs_geocoding(df):
    '''
    Keeps only the records that have not been geocoded. Returns a dataframe.
    '''

    id = 'CSDS_Org_ID'
    lat = 'Latitude'
    lon = 'Longitude'
    address_fields = ['Address','City','State','ZipCode']

    needs_geo = df[[id,lat,lon] + [x for x in address_fields]].drop_duplicates()
    needs_geo = needs_geo[pd.isnull(needs_geo[lat])]
    needs_geo = needs_geo.drop([lat,lon],axis=1)

    needs_geo = needs_geo.rename(columns={'ZipCode':'Zip'},index=str)

    return needs_geo.reset_index(drop=True)


if __name__ == '__main__':

    dollars_div = dollars_per_location()
    dollars_div.to_csv(DOLLARS_DIVIDED,index=False)

    satellites = separate_satellites(dollars_div)

    needs_geo = needs_geocoding(satellites)
    needs_geo.to_csv(GEO,index=False)





    '''
    $/agency @ service addresses

    CONTRACTAGENCIES [VendorName] LINK [Name] SERVICEAGENCIES

    -Count the number of service addresses per agency; add as a column
    -Add agg_dollars as a column
    -Divide agg_dollars by num_locations
    -Pull out the ones that need to be geocoded, then geocode them, then merge
        them back in
    -Make two dataframes:
        -HQs
        -Satellites


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

import numpy as np
import pandas as pd


MAP1B = '../../../rcc-uchicago/PCNO/CSV/chicago/maps/map1b.csv'
DOLLARS_DIVIDED = '../../../rcc-uchicago/PCNO/CSV/chicago/dollars_divided.csv'
MAP2B_SATELLITES = '../../../rcc-uchicago/PCNO/CSV/chicago/Maps/map2b_satellites.csv'
MAP2B_HQ = '../../../rcc-uchicago/PCNO/CSV/chicago/Maps/map2b_hq.csv'


def read_contracts():
    '''
    '''

    df = pd.read_csv(MAP1B,converters={'Zip':str})

    return df


def read_dollars_divided():
    '''
    '''

    df = pd.read_csv(DOLLARS_DIVIDED,converters={'Zip':str})

    return df


def merger():
    '''
    '''


    contracts = read_contracts()
    dollars_divided = read_dollars_divided()

    merged = dollars_divided.merge(contracts,how='left')

    merged['Dollars_Per_Contract_Per_Location'] = merged['Amount'] / merged['Num_Svc_Locations']


    return merged


def separate_hq(merged):
    '''
    '''

    keep = ['CSDS_Contract_ID','ContractNumber','Description',
            'Agency/Department','VendorName','VendorID','Amount','StartDate',
            'EndDate','Category/ProcurementType','Link/ContractPDF',
            'CSDS_Vendor_ID','Address','City','State','Zip','Jurisdic',
            'Longitude','Latitude','Classification','Num_Svc_Locations',
            'Dollars_Per_Contract_Per_Location']

    hq = merged[merged['HQ_Flag'] == 1]

    return hq[keep].reset_index(drop=True)


def separate_satellites(merged):
    '''
    '''

    keep = ['CSDS_Contract_ID','ContractNumber','Description',
            'Agency/Department','VendorName','VendorID','Amount','StartDate',
            'EndDate','Category/ProcurementType','Link/ContractPDF',
            'CSDS_Vendor_ID','Address','City','State','Zip','Jurisdic',
            'Longitude','Latitude','Classification',
            'Dollars_Per_Contract_Per_Location']

    satellites = merged[merged['HQ_Flag'] == 0].drop(['Address','City','State','Zip'],axis=1)

    cols = {'Address_SVC':'Address','City_SVC':'City','State_SVC':'State',
            'ZipCode_SVC':'Zip'}
    satellites = satellites.rename(columns=cols,index=str)

    return satellites[keep].reset_index(drop=True)


if __name__ == '__main__':


    merged = merger()

    hq = separate_hq(merged)
    hq.to_csv(MAP2B_HQ,index=False)

    satellites = separate_satellites(merged)
    satellites.to_csv(MAP2B_SATELLITES,index=False)

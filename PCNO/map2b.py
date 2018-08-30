import map2 as m2
import numpy as np
import pandas as pd


MAP1B = '../../../rcc-uchicago/PCNO/CSV/chicago/maps/map1b.csv'
DOLLARS_DIVIDED = '../../../rcc-uchicago/PCNO/CSV/chicago/dollars_divided.csv'
MAP2B_SATELLITES = '../../../rcc-uchicago/PCNO/CSV/chicago/Maps/map2b_satellites.csv'
MAP2B_HQ = '../../../rcc-uchicago/PCNO/CSV/chicago/Maps/map2b_hq.csv'

MAP2_SATELLITES = '../../../rcc-uchicago/PCNO/CSV/chicago/Maps/map2_satellites.csv'
MAP2_HQ = '../../../rcc-uchicago/PCNO/CSV/chicago/Maps/map2_hq.csv'

def read_map2():
    '''
    '''

    keep = ['CSDS_Vendor_ID','VendorName','Agency_Summed_Amount','Address',
            'City','State','ZipCode','HQ_Flag','Num_Svc_Locations',
            'Dollars_Per_Location']

    dollars_divided = m2.read_dollars_divided()
    dollars_divided = dollars_divided[keep]

    cv = {'ZipCode':str}
    hq = pd.read_csv(MAP2_HQ,converters=cv)
    hq['HQ_Flag'] = 1
    sat = pd.read_csv(MAP2_SATELLITES,converters=cv)
    sat['HQ_Flag'] = 0

    merged = pd.concat([hq,sat])

    merged = merged.drop(['Agency_Summed_Amount','CSDS_Org_ID',#'City','State',
                          #'ZipCode','Address',#'Longitude','Latitude'
                          'Num_Svc_Locations','Dollars_Per_Location'],axis=1)

    merged = merged.merge(dollars_divided,how='left')

    return merged



def read_contracts():
    '''
    Reads in the contracts from map 1b, converting the Zip field to string.
    Returns a dataframe.
    '''

    df = pd.read_csv(MAP1B,converters={'Zip':str})
    df = df.drop(['Longitude','Latitude','Address','City','State','Zip'],axis=1)

    return df


def read_dollars_divided():
    '''
    Reads the dollars_divided file, converting the Zip field to a string.
    Returns a dataframe.
    '''

    df = pd.read_csv(DOLLARS_DIVIDED,converters={'ZipCode':str,'ZipCode_SVC':str})

    return df


def merger():
    '''
    Reads in the contracts and dollars_divided files and merges them. Calculates
    the dollars per contract per location by dividing the amount by the number
    of service locations. Returns a dataframe.
    '''

    contracts = read_contracts()

    #dollars_divided = read_dollars_divided()
    dollars_divided = read_map2()

    merged = contracts.merge(dollars_divided,how='left')

    merged['Dollars_Per_Contract_Per_Location'] = merged['Amount'] / merged['Num_Svc_Locations']


    return merged


def separate_hq(merged):
    '''
    Makes the dataframe for the map 2b HQ file: Separates HQ records, drops
    unwanted columns, and changes the order of the rest of the columns. Returns
    a dataframe.
    '''

    keep = ['CSDS_Contract_ID','ContractNumber','Description',
            'Agency/Department','VendorName','VendorID','Amount','StartDate',
            'EndDate','Category/ProcurementType','Link/ContractPDF',
            'CSDS_Vendor_ID','Address','City','State','ZipCode','Jurisdic',
            'Longitude','Latitude','Classification','Num_Svc_Locations',
            'Dollars_Per_Contract_Per_Location']

    hq = merged[merged['HQ_Flag'] == 1]

    return hq[keep].reset_index(drop=True)


def separate_satellites(merged):
    '''
    Makes the dataframe for the map 2b satellite file: Separates satellite
    records, drops unwanted columns, renames some columns, and changes the order
    of the rest of the columns. Returns a dataframe.
    '''

    keep = ['CSDS_Contract_ID','ContractNumber','Description',
            'Agency/Department','VendorName','VendorID','Amount','StartDate',
            'EndDate','Category/ProcurementType','Link/ContractPDF',
            'CSDS_Vendor_ID','Address','City','State','Zip','Jurisdic',
            'Longitude','Latitude','Classification',
            'Dollars_Per_Contract_Per_Location']

    satellites = merged[merged['HQ_Flag'] == 0]#.drop(['Address','City','State','Zip'],axis=1)

    cols = {'Address_SVC':'Address','City_SVC':'City','State_SVC':'State',
            'ZipCode_SVC':'Zip'}
    satellites = satellites.rename(columns=cols,index=str)

    return satellites#[keep].reset_index(drop=True)


if __name__ == '__main__':


    merged = merger()

    hq = separate_hq(merged)
    hq.to_csv(MAP2B_HQ,index=False)

    satellites = separate_satellites(merged)
    satellites.to_csv(MAP2B_SATELLITES,index=False)

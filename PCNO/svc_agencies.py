import re
import UTILS as u
import numpy as np
import pandas as pd
import COMPARE_ADDRESSES as ca


LINK = '../../../rcc-uchicago/PCNO/CSV/chicago/2018-07-03_link_agencies_output.csv'
MAP1B = '../../../rcc-uchicago/PCNO/CSV/chicago/maps/map1b.csv'
SVC = '../../../rcc-uchicago/PCNO/CSV/chicago/service_agencies.csv'
GEO = '../../../rcc-uchicago/PCNO/CSV/chicago/map2_geocoding.csv'
GEO2 = '../../../rcc-uchicago/PCNO/CSV/chicago/map2_geocoding_version2.csv'
DOLLARS_DIVIDED = '../../../rcc-uchicago/PCNO/CSV/chicago/dollars_divided.csv'

THRESH = 0.34


def read_linker():
    '''
    Reads in the linked agencies file, retains matches >= the THRESH level, then
    drops two columns. Returns a dataframe.
    '''

    # Read in the link file, converting ClusterID to string
    df = pd.read_csv(LINK,converters={'ClusterID':str})

    # Keep only records with LinkScore >= THRESH
    df = df[df['LinkScore'] >= THRESH]

    # Drop these columns
    df = df.drop(['LinkScore','SourceFile'],axis=1)

    return df


def linker():
    '''
    Reads in the linker file (to link HQ agencies to service agencies). Merges a
    copy of itself on cluster ID, then eliminates records that match on vendor
    ID (to produce only matches that have different vendor IDs). Returns a
    dataframe.
    '''

    # Read in the link dataframe
    link = read_linker()

    # Make two new dataframes by copying the link dataframe and renaming columns
    link1 = link.rename(columns={'VendorName':'VendorName_LINK1'},index=str)
    link2 = u.rename_cols(link,['VendorName','CSDS_Vendor_ID'],'_LINK2')

    # Merge the two link dataframes together
    df = link1.merge(link2,how='left')

    # Drop self-matches and reset the index
    df = df[df['CSDS_Vendor_ID'] != df['CSDS_Vendor_ID_LINK2']].reset_index(drop=True)

    return df


def insert_marginal_hq(df):
    '''
    For each headquarters address, makes a row with that same address in the
    fields for the service address. This is so that headquarters addresses will
    be included as locations to which funds must be allocated. Returns a
    dataframe.
    '''

    # Initalize an empty list to hold dictionaries
    list_of_dictos = []

    # Iterate through the rows in the dataframe; For every row:
    for row in df.itertuples(index=False):
        # If the service address is not np.NaN:
        if row.Address_SVC is not np.NaN:
            # And if the address != the service address:
            if row.Address != row.Address_SVC:
                # Make a dictionary of the row and append it to list_of_dictos
                dicto = row._asdict()
                list_of_dictos.append(dicto)

    # For every dictionary (which each represents a row)
    for dicto in list_of_dictos:
        # Set the column on the left to have the value on the right
        dicto['Address_SVC'] = dicto['Address']
        dicto['City_SVC'] = dicto['City']
        dicto['State_SVC'] = dicto['State']
        dicto['ZipCode_SVC'] = dicto['ZipCode']
        dicto['CSDS_Org_ID_SVC'] = np.NaN

    # Make a dataframe from the list of newly modified dictionaries
    appender = pd.DataFrame(list_of_dictos)

    # Append new df to original df; drop duplicates for good measure
    df_aug = pd.concat([df,appender])
    df_aug = df_aug.drop_duplicates()

    return df_aug


def merger():
    '''
    '''

    # Read in the linker dataframe
    link = linker()

    # Read in the headquarters data and keep only these columns; drop duplicates
    hq = read_hq()[['CSDS_Vendor_ID','VendorName','Agency_Summed_Amount','Address',
                    'City','State','ZipCode','Longitude','Latitude']].drop_duplicates()

    # Read in the service addresses
    svc = read_svc()

    # Merge:  HQ -- LINK -- SVC
    merged = hq.merge(link,how='left').merge(svc,how='left')

    # Pull HQ addresses into SVC fields so that HQ addresses will be counted as
    # locations to which to allocate funds
    df_aug = insert_marginal_hq(merged)

    # Merge these dataframes together; drop duplicates based on these fields
    mega_df = pd.concat([merged,df_aug])
    mega_df = mega_df.drop_duplicates(subset=['CSDS_Vendor_ID','Address_SVC']).reset_index(drop=True)

    return mega_df



def dollars_per_location(merged):
    '''
    Reads in the service agencies and the HQ agencies, then links them (using
    the linker dataframe). Calculates the number of dollars per location.
    Returns a dataframe.
    '''

    # Declare a list of columns
    cols = ['Address','City','State','ZipCode']

    # Fill in blanks in col + '_SVC' from values in col
    for col in cols:
        merged[col + '_SVC'] = merged[col + '_SVC'].combine_first(merged[col])

    # If the address, city, and state match, fill in latitude & longitude
    coords = ['Longitude','Latitude']
    for col in coords:
        merged[col + '_SVC'] = merged.apply(lambda x: x[col] if
                                        (x['Address'] == x['Address_SVC']) and
                                        (x['City'] == x['City_SVC']) and
                                        (x['State'] == x['State_SVC'])
                                        else np.NaN, axis=1)

    # Need to account for HQ addresses with different zips

    # Sort values by these fields
    merged2 = merged.sort_values(['CSDS_Vendor_ID','Address_SVC','City_SVC',
                                  'State_SVC','ZipCode_SVC'],ascending=True)

    # Frop duplicates based on this subset of fields, keeping the first record
    merged2 = merged2.drop_duplicates(subset=['CSDS_Vendor_ID','Address','City',
                                              'State','Address_SVC','City_SVC',
                                              'State_SVC'],keep='first')

    # Make a flag column and set it to 1 if the HQ and SVC fields match, else 0
    merged2['HQ_Flag'] = merged2.apply(lambda x: 1 if
                                    (x['Address'] == x['Address_SVC']) and
                                    (x['City'] == x['City_SVC']) and
                                    (x['State'] == x['State_SVC']) else 0,
                                    axis=1)

    # Count how many locations there are per organization; merge the counts in
    counts = count_svc_addr(merged2)
    numbered = merged2.merge(counts,how='left')

    # Calculate the number of dollars divided by the number of locations
    dollars_div = numbered.assign(Dollars_Per_Location=numbered['Agency_Summed_Amount']\
                           / numbered['Num_Svc_Locations'])

    # Drop duplicates and reset the index for good measure
    return dollars_div.drop_duplicates().reset_index(drop=True)


def read_hq():
    '''
    Reads in the contracts with HQ addresses; converts the zip codes to strings.
    Adds up the contract amounts per agency. Returns a dataframe.
    '''

    # Read in the map 1b records, convering zip code to string
    df = pd.read_csv(MAP1B,converters={'Zip':str})

    # Rename this column
    df = df.rename(columns={'Zip':'ZipCode'},index=str)

    # Aggregate the total funds per agency, then merge those values in
    agg_amounts = agg_funds(df)
    merged = df.merge(agg_amounts)

    return merged


def read_svc():
    '''
    Reads in the service agency addresses. Calls the COMPARE_ADDRESSES module to
    merge duplicate addresses per agency. Counts the number of service addresses
    per organization. Returns a dataframe.
    '''

    # Print progress report
    print('\nReading in service agencies')

    # Read in the service agencies, converting zip code to string
    df = pd.read_csv(SVC,converters={'ZipCode':str})

    # Append '_SVC' to all columns except CSDS_Svc_ID
    df = u.rename_cols(df,[x for x in df.columns if x != 'CSDS_Svc_ID'],'_SVC')

    # Rename a column to prepare for linking
    df = df.rename(columns={'CSDS_Svc_ID':'CSDS_Vendor_ID_LINK2'},index=str)

    # Use the COMPARE_ADDRESSES module to clean up multiple strings for a single
    # address record
    key = 'CSDS_Vendor_ID_LINK2'
    target = 'Address_SVC'
    fixed_addresses = ca.fix_duplicate_addresses(df,key,target)

    # Drop duplicates based on the key and target fields
    fixed_addresses = fixed_addresses.drop_duplicates(subset=[key,target])

    return fixed_addresses


def agg_funds(hq):
    '''
    Adds up the contract amounts per HQ agency. Returns a dataframe.
    '''

    # Group by vendor ID and sum the amount
    agg = hq.groupby('CSDS_Vendor_ID')['Amount'].sum().reset_index()

    # Rename the column to reflect the true values
    agg = agg.rename(columns={'Amount':'Agency_Summed_Amount'},index=str)

    return agg


def count_svc_addr(df):
    '''
    Counts the number of service addresses per agency. Returns a dataframe.
    '''

    # Assign a constant to count
    df = df.assign(Constant=1)

    # Group by vendor ID and count the constants
    counts = df.groupby('CSDS_Vendor_ID')['Constant'].count()

    # Rename the series
    counts.name = 'Num_Svc_Locations'

    # Convert to a dataframe and reset the index
    return counts.to_frame().reset_index()


def separate_satellites(df):
    '''
    The problem right now is that this is keeping HQs that have satellites and
    only excluding HQs with no satellites.

    Going to leave this alone and deal with it in the map2 script.
    '''

    # Define columns to keep and their order
    keep = ['CSDS_Vendor_ID','VendorName','CSDS_Org_ID_SVC','City_SVC',
            'State_SVC','ZipCode_SVC','Longitude_SVC','Latitude_SVC',
            'Address_SVC','Dollars_Per_Location']

    # Any rows with np.NaN in this field are not satellites, so drop them
    satellites = df.dropna(subset=['Num_Svc_Locations'])

    # Keep only records with Num_Svc_Locations > 1
    # (This renders the previous line redundant; consider addressing)
    satellites = satellites[satellites['Num_Svc_Locations'] > 1]

    # Keep designated columns and rearrange
    satellites = satellites[keep]

    # Append column names with '_SVC'
    new_names = [re.sub('_SVC$','',x) for x in keep]
    cn = dict(zip(keep,new_names))
    satellites = satellites.rename(columns=cn,index=str)

    # Reset the index for good measure
    return satellites.reset_index(drop=True)


def needs_geocoding(df):
    '''
    Keeps only the records that have not been geocoded. Returns a dataframe.
    '''

    # Shortcuts
    id = 'CSDS_Org_ID'
    lat = 'Latitude'
    lon = 'Longitude'

    # Define a list of fields
    address_fields = ['Address','City','State','ZipCode']

    # Keep only these fields; drop duplicates
    needs_geo = df[[id,lat,lon] + [x for x in address_fields]].drop_duplicates()

    # Keep only records with np.NaN in the Latitude column
    needs_geo = needs_geo[pd.isnull(needs_geo[lat])]

    # Drop the Latitude and Longitude columns
    needs_geo = needs_geo.drop([lat,lon],axis=1)

    # Drop rows with np.NaN in the CSDS_Org_ID column
    needs_geo = needs_geo.dropna(subset=['CSDS_Org_ID'])

    # Rename columns
    needs_geo = needs_geo.rename(columns={'ZipCode':'Zip','CSDS_Org_ID':'ID'},index=str)

    # Reset the index for good measure
    return needs_geo.reset_index(drop=True)


if __name__ == '__main__':

    merged = merger()

    dollars_div = dollars_per_location(merged)
    dollars_div.to_csv(DOLLARS_DIVIDED,index=False)

    # This is the correct amount:  3810692646.1199999

    satellites = separate_satellites(dollars_div)

    needs_geo = needs_geocoding(satellites)
    needs_geo.to_csv(GEO2,index=False)

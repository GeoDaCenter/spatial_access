import numpy as np
import pandas as pd
from datetime import datetime as dt


DOLLARS_DIVIDED = '../../../rcc-uchicago/PCNO/CSV/chicago/dollars_divided.csv'
GEO1 = '../../../rcc-uchicago/PCNO/CSV/chicago/Maps/map2_hq.csv'
GEO2 = '../../../rcc-uchicago/PCNO/CSV/chicago/Maps/map2_satellites.csv'
MAP2B_SATELLITES = '../../../rcc-uchicago/PCNO/CSV/chicago/Maps/map2b_satellites.csv'
MAP2B_HQ = '../../../rcc-uchicago/PCNO/CSV/chicago/Maps/map2b_hq.csv'


def read_geo():
    '''
    '''

    geo1 = pd.read_csv(GEO1,converters={'ZipCode':str})
    geo2 = pd.read_csv(GEO2,converters={'ZipCode':str})

    geo = pd.concat([geo1,geo2])
    geo = geo.rename(columns={'ZipCode':'Zip'},index=str)

    return geo.drop('Dollars_Per_Location',axis=1)


def read_contracts():
    '''
    '''

    contracts1 = pd.read_csv(MAP2B_HQ,converters={'ZipCode':str})
    contracts1['HQ_Flag'] = 1

    contracts2 = pd.read_csv(MAP2B_SATELLITES,converters={'ZipCode':str})
    contracts2['HQ_Flag'] = 0

    contracts = pd.concat([contracts1,contracts2])

    return contracts


def merger():
    '''
    '''

    geo = read_geo()
    contracts = read_contracts()

    merged = contracts.merge(geo,how='left')

    return merged


def datefixer(datestring):
    '''
    Fixes dates that come in 'yyyy-mm-dd' format and changes them to datetime.
    If there is no date, returns datetime for 01/01/1900.
    '''

    if not datestring:
        return dt.strptime('1/1/1900','%m/%d/%Y')
    else:
        try:
            return dt.strptime(datestring,'%m/%d/%y')#'%Y-%m-%d')
        except:
            return dt.strptime(datestring,'%Y-%m-%d')


def assign_fy(df):
    '''
    '''

    s = 'EarliestStartDate'
    e = 'LatestEndDate'

    df = df.assign(FYStart=df[s].apply(fy))
    df = df.assign(FYEnd=df[e].apply(fy))

    df = df.assign(FYs=df.apply(lambda x: x.FYEnd - x.FYStart + 1, axis=1))

    return df


def fy(datetime):
    '''
    Takes in a datetime object and returns the fiscal year in which that date
    falls.
    '''

    # Per the City Clerk's web site, the fiscal year follows the calendar year
    # http://www.chicityclerk.com/legislation-records/journals-and-reports/city-budgets
    fystart = '-01-01' # -mm-dd

    year = datetime.strftime('%Y')

    thresh = datefixer(year + fystart)

    if datetime >= (thresh):
        return int(year) + 1
    else:
        return int(year)


def fix_dates(df):
    '''
    Runs the 'StartDate' and 'EndDate' columns through datefixer. Returns a
    dataframe.
    '''

    s = 'StartDate'
    e = 'EndDate'

    # Run through a datefixer for calculations and to make sure dates are okay
    df[s] = df[s].apply(datefixer)
    df[e] = df[e].apply(datefixer)

    return df


def id_problem_dates(df,mode):
    '''
    Identifies records with problem date ranges. Returns a dataframe.
    '''

    p = 'ContractDateProblem'

    if mode == 'standard':
        s = 'StartDate'
        e = 'EndDate'
    else:
        s = 'EarliestStartDate'
        e = 'LatestEndDate'

    df = df.assign(ContractDateProblem = np.NaN)

    df[p] = df.apply(lambda x: 1 if x[s] > x[e] else 0, axis=1)

    return df


def calc_len(df,mode):
    '''
    Calculates the length of each contract in days. Returns a dataframe.
    '''

    p = 'ContractDateProblem'
    c = 'ContractLength'

    if mode == 'standard':
        s = 'StartDate'
        e = 'EndDate'
    else:
        s = 'EarliestStartDate'
        e = 'LatestEndDate'

    df = df.assign(ContractLength = np.NaN)

    # If there is not a contract date problem, calculate the length in days.
    # The constant (1) is added to include both the day on which the contract
    # begins and the day on which it ends.
    df[c] = df.apply(lambda x: np.NaN if x[p] else (x[e] - x[s]).days + 1, axis=1)

    return df


def find_best_dates(df):
    '''
    Takes in a dataframe of contracts and for each unique contract number, finds
    the most common start & end dates and assigns those. Returns a dataframe.
    '''

    merged = most_common_date(df,'StartDate')
    merged = most_common_date(merged,'EndDate')

    return merged


def most_common_date(df,field):
    '''
    Takes in a dataframe of contracts and a fieldname and, for each contract,
    finds the most common date in the given field, then assigns that value in a
    new field. Returns a dataframe.
    '''

    # Define a constant
    cn = 'ContractNumber'

    # Determine how to sort the dataframe
    if field == 'StartDate':
        sort = True
        date_name = 'EarliestStartDate'
    else:
        sort = False
        date_name = 'LatestEndDate'

    # Get the number of times each date appears for each contract, then sort by
    # contract and the date field
    dates = df.groupby([cn])[field].value_counts()
    dates.name = 'Count'
    dates = dates.to_frame().reset_index()
    dates = dates.sort_values(by=[cn,field],ascending=sort)
    #return dates

    # Get the max number of times a date appears for each contract
    max_count = dates.groupby([cn,field]).max()

    # Merge the dataframes so that we keep only the most common values
    merger = dates.merge(max_count,how='left')  # SHOULD THIS BE INNER?

    # Take only the first record for each contract number:
    # When field == Start Date, this will be the earliest date; when
    # field == End Date, this will be the latest date
    merger = merger.groupby(cn).first()

    # Reset the index and drop the count column, then rename the new column
    merger = merger.reset_index()[[cn,field]]
    merger = merger.rename(columns={field:date_name},index=str)

    # Merge the new date column back into the original df and return it
    df = df.merge(merger)

    return df


def prep(merged):
    '''
    Prepares the dataset for the fiscal year calculations. Returns a dataframe.
    '''

    # Convert datestrings to datetime objects for calculations
    dated = fix_dates(merged)

    # Across all the records for a given contract, find the most common start
    # and end dates and assign those to all the records for that contract. If
    # there is a tie for the most common date, assign the most extreme (earliest
    # for start dates and latest for end dates).
    best_dates = find_best_dates(dated)

    # Identify records that have an end date before the start date
    prob_dates = id_problem_dates(best_dates,'expanded')
    return prob_dates

    # Measure the length of each contract in days
    #length_measured = calc_len(prob_dates,'expanded')

    # Convert to one record per amount per contract ID (instead of one record
    # per address per contract ID)
    unique_amts = unique_amounts(prob_dates)#length_measured)

    # Sum the amounts for all the records associated with a given contract
    #summer = sum_amounts(unique_amts)

    return unique_amts#summer


def unique_amounts(df):
    '''
    Takes in a dataframe of contract records and drops duplicate records (which
    have different addresses). Returns a dataframe.
    '''



    '''
    df = df.drop(['Address','City','State','Zip','Latitude','Longitude',
                  'AddressID','Num_Svc_Locations'],
                 axis=1)

    return df.drop_duplicates().reset_index(drop=True)
    '''

    #df = df.drop_duplicates(subset=['ContractNumber','Amount'])
    agg = df.groupby('ContractNumber')['Amount'].sum()
    agg.name = 'TotalAmount'
    agg = agg.to_frame().reset_index()

    merged = df.merge(agg,how='inner')

    merged = merged[['ContractNumber','Description','Agency/Department',
                     'VendorName','VendorID','Category/ProcurementType',
                     'Link/ContractPDF','CSDS_Vendor_ID','Address','City',
                     'State','Zip','Agency_Summed_Amount',
                     'CSDS_Org_ID','Num_Svc_Locations','EarliestStartDate',
                     'LatestEndDate','ContractDateProblem','TotalAmount']]

    return merged.drop_duplicates(subset=['ContractNumber']).reset_index(drop=True)


def sum_amounts(df):
    '''
    Adds up the different amounts for each contract. Returns a dataframe.
    '''

    trimmed = df[['Amount','CSDS_Contract_ID','ContractNumber',
                  'EarliestStartDate','LatestEndDate','ContractDateProblem']]#,#'ContractLength']]
    trimmed = trimmed.drop_duplicates()

    summer = trimmed.groupby(['ContractNumber']).Amount.sum()
    summer.name = 'TotalAmount'
    summer = summer.to_frame().reset_index()

    #BOOKMARK

    df = df.drop('Amount',axis=1)
    df = df.merge(summer)
    #df = df[['Contract Number','EarliestStartDate','LatestEndDate',
     #        'ContractDateProblem','ContractLength','TotalAmount',
      #       'CSDS_Agency_ID']]

    return df.drop_duplicates().reset_index(drop=True)


def separate_addresses(df):
    '''
    Removes the contract info and reduces the dataframe to just the agency and
    address info. Returns a dataframe.
    '''

    df = df[['CSDS_Vendor_ID','Address','City','State','Zip',#'AddressID',
             'Latitude','Longitude','Num_Svc_Locations']]

    #df = df.dropna(subset=['AddressID'])

    return df.drop_duplicates().reset_index(drop=True)


def merge_addr(amts,addr):
    '''
    Merges the amounts and addresses dataframes. Returns a dataframe with one
    row per address per contract.
    '''

    #unique = addr

    #add_ct = addr.groupby('CSDS_Vendor_ID').count()#['AddressID']
    addr = addr.drop_duplicates()
    add_ct = addr['CSDS_Vendor_ID'].value_counts()

    add_ct.name = 'AddressCount'
    add_ct = add_ct.to_frame().reset_index()
    add_ct = add_ct.rename(columns={'index':'CSDS_Vendor_ID'},index=str)

    add_merge = addr.merge(add_ct)
    amts_merge = add_merge.merge(amts)
    amts_div = amts_merge.assign(AnnualDollarsPerAddressPerContract=amts_merge.apply(
               lambda x: x.AnnualAmount / x.AddressCount, axis=1))

    amts_div = amts_div.drop([#'CSDS_Contract_ID','EndDate','StartDate',
                              'Link/ContractPDF','Description',
                              'VendorID'],axis=1).drop_duplicates().reset_index(drop=True)

    return amts_div


def calc_ann_amt(df):
    '''
    Calculates dollars per fiscal year. Returns a dataframe.
    '''

    col = 'Dollars_Per_Contract_Per_Location'

    #df = df.assign(AnnualAmount=df.apply(lambda x: x.TotalAmount / x.FYs if
    df = df.assign(AnnualAmount=df.apply(lambda x: x[col] / x.FYs if
                   x.ContractDateProblem == 0 else np.NaN,axis=1))

    return df


def make_span(df):
    '''
    Makes a dataframe with a row for each fiscal year that each contract spans.
    Returns a dataframe.
    '''

    df_trimmed = df[df['ContractDateProblem'] == 0]
    df_trimmed = df[['ContractNumber','FYStart','FYEnd']]
    df_trimmed = df_trimmed.drop_duplicates().reset_index(drop=True)

    df_trimmed['Range'] = df_trimmed.apply(lambda x: [y for y in range(x['FYStart'],x['FYEnd'] + 1)],axis=1)

    df_trimmed = df_trimmed.set_index('ContractNumber')

    spanner = df_trimmed['Range'].apply(pd.Series).stack().reset_index(level=0)
    spanner = spanner.rename(columns={0:'FY'},index=str).reset_index(drop=True)
    spanner['Range'] = spanner['FY'].apply(int)

    return spanner


def make_map3b(spanner,ann_amts):
    '''
    '''

    keep = ['CSDS_Contract_ID','ContractNumber','Description',
            'Agency/Department','VendorName','VendorID','Amount',
            'EarliestStartDate','LatestEndDate','Category/ProcurementType',
            'Link/ContractPDF','CSDS_Vendor_ID','Address','City','State','Zip',
            'Jurisdic','Longitude','Latitude','Classification',
            'Num_Svc_Locations','Dollars_Per_Contract_Per_Location','FYStart',
            'FYEnd','FY','AnnualAmount']

    merged = spanner.merge(ann_amts)

    hq = merged[merged['HQ_Flag'] == 1].reset_index(drop=True)
    satellites = merged[merged['HQ_Flag'] == 0].reset_index(drop=True)

    return hq[keep],satellites[keep]


def make_map3(hqb,satb):
    '''
    '''

    keep = ['CSDS_Vendor_ID','FY']#,'VendorName']

    keep2 = ['Address','City','State','Longitude','Latitude']#,'Zip']

    z = ['Zip'] #There are different zips for some addresses, which is keeping
    # the groupby from working properly, but I'm not sure why

    anam = 'AnnualAmount'

    hq_sum = hqb.groupby(keep)[anam].sum().to_frame().reset_index()
    hqb_trimmed = hqb[keep + keep2 + z].drop_duplicates().reset_index(drop=True)

    hq = hqb_trimmed.merge(hq_sum,how='left')

    sat_sum = satb.groupby(keep + keep2)[anam].sum().to_frame().reset_index()
    satb_trimmed = satb[keep + keep2 + z].drop_duplicates().reset_index(drop=True)

    sat = satb_trimmed.merge(sat_sum,how='left')

    return hq.reset_index(drop=True),sat.reset_index(drop=True)


if __name__ == '__main__':

    # Total funds should be short $710,000 because of records w/ date problems.
    # New total should be $3809982646.12
    #                  $3,809,982,646.12

    target = 3809982646.12
    print('Target:                 {0:,.2f}'.format(target))

    # contracts.Amount.sum() should be: 3810692646.12
    contracts = merger()

    # Convert to one record (with a single amount) per contract
    dated = prep(contracts)

    # Assign the fiscal years in which each contract begins and ends
    fy_assigned = assign_fy(dated)

    # Calculate the annual amount for each contract (totalAmt / numFY)
    ann_amts = calc_ann_amt(fy_assigned)

    spanner = make_span(ann_amts)

    map3b_hq,map3b_satellites = make_map3b(spanner,ann_amts)

    #-----------------------------------------------------------------FINE ABOVE

    hq,satellites = make_map3(map3b_hq,map3b_satellites)
    print(hq.AnnualAmount.sum() + satellites.AnnualAmount.sum() - target)
    print(hq.AnnualAmount.sum() - map3b_hq.AnnualAmount.sum())
    print(satellites.AnnualAmount.sum() - map3b_satellites.AnnualAmount.sum())


    '''
    Map 3:  Amount per fiscal year per location

    Map 3b: amount per fiscal year per location per contract

    So Map 3 is Map 3b aggregated up

    Start with 3b and then aggregate up to 3?


    So 3b should have one row for each applicable FY per contract per location,
    one file for HQs and one for satellites.

    3 should have one row for each applicable FY (with the FY sum for all
    contracts in effect that FY) per location, one file for HQs and one for
    satellites.
    '''

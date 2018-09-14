import numpy as np
import pandas as pd
from datetime import datetime as dt


MAP2B_HQ = '../../../rcc-uchicago/PCNO/CSV/chicago/Maps/map2b_hq.csv'
MAP2B_SATELLITES = '../../../rcc-uchicago/PCNO/CSV/chicago/Maps/map2b_satellites.csv'
MAP3_HQ = '../../../rcc-uchicago/PCNO/CSV/chicago/Maps/map3_hq.csv'
MAP3_SATELLITES = '../../../rcc-uchicago/PCNO/CSV/chicago/Maps/map3_satellites.csv'
MAP3B_HQ = '../../../rcc-uchicago/PCNO/CSV/chicago/Maps/map3b_hq.csv'
MAP3B_SATELLITES = '../../../rcc-uchicago/PCNO/CSV/chicago/Maps/map3b_satellites.csv'


def read_contracts():
    '''
    Reads the map 2b HQ and satellite files and adds a flag for the type of
    location. Returns a dataframe.
    '''

    # Read in contracts and convert ZipCode to string
    cv = {'ZipCode':str}
    contracts1 = pd.read_csv(MAP2B_HQ,converters=cv)
    contracts2 = pd.read_csv(MAP2B_SATELLITES,converters=cv)

    # Assign flags depending on whether the dataframe came from HQ or satellites
    contracts1['HQ_Flag'] = 1
    contracts2['HQ_Flag'] = 0

    # Concatenate the dataframes
    contracts = pd.concat([contracts1,contracts2])

    return contracts


def datefixer(datestring):
    '''
    Fixes dates that come in 'yyyy-mm-dd' or 'm/d/yy' format and changes them to
    datetime. If the string is empty, returns datetime for 01/01/1900.
    '''

    if not datestring:
        return dt.strptime('1/1/1900','%m/%d/%Y')
    else:
        try:
            return dt.strptime(datestring,'%Y-%m-%d')
        except:
            return dt.strptime(datestring,'%m/%d/%y')


def assign_fy(df):
    '''
    Determines the fiscal years in which the earliest start date and latest end
    date are located. Calculates the number of fiscal years spanned by the given
    contract. Returns a dataframe.
    '''

    # Define some fieldnames
    s = 'EarliestStartDate'
    e = 'LatestEndDate'

    # Assign the FYStart and FYEnd variables by getting the FY of the dates in
    # the 'EarliestStartDate' and 'LatestEndDate' fields
    df = df.assign(FYStart=df[s].apply(fy))
    df = df.assign(FYEnd=df[e].apply(fy))

    # Count the numbber of FYs spanned by the range
    df = df.assign(FYs=df.apply(lambda x: x.FYEnd - x.FYStart + 1, axis=1))

    return df


def fy(datetime_object):
    '''
    Takes in a datetime object and returns the fiscal year in which that date
    falls.
    '''

    # Per the City Clerk's web site, the fiscal year follows the calendar year:
    # http://www.chicityclerk.com/legislation-records/journals-and-reports/city-budgets

    # Therefore, the fiscal year of any date matches its year. However, the same
    # will not be true in all jurisdictions. This script allows the script to be
    # modified for other FY start dates.

    # Set a string that defines when the fiscal year ends (December 31)
    fyend = '-12-31' # -mm-dd

    # Extract the year from datetime_object
    year = datetime_object.strftime('%Y')

    # Concatenate the strings, then pass to datefixer to get a datetime object
    thresh = dt.strptime(year + fyend,'%Y-%m-%d')

    # If the date is after the threshold, it's in the next fiscal year
    if datetime_object > (thresh):
        return int(year) + 1
    else:
        return int(year)


def fix_dates(df):
    '''
    Runs the 'StartDate' and 'EndDate' columns through datefixer. Returns a
    dataframe.
    '''

    # Define the column names
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

    # If running in standard mode, then start = StartDate and end = EndDate
    if mode == 'standard':
        s = 'StartDate'
        e = 'EndDate'
    # If not running in standard mode, then use these fields instead
    else:
        s = 'EarliestStartDate'
        e = 'LatestEndDate'

    # Assign an empty variable
    df = df.assign(ContractDateProblem = np.NaN)

    # If s is greater than e, then there's a problem with the dates
    df['ContractDateProblem'] = df.apply(lambda x: 1 if x[s] > x[e] else 0, axis=1)

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

    # Define a fieldname
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


def calc_ann_amt(df):
    '''
    Calculates dollars per fiscal year. Returns a dataframe.
    '''

    col = 'Dollars_Per_Contract_Per_Location'

    # For records that do not have a contract date problem, assign to
    # AnnualAmount the value in col divided by the number of FYs spanned by the
    # contract; otherwise, assign np.NaN
    df = df.assign(AnnualAmount=df.apply(lambda x: x[col] / x.FYs if
                                 x.ContractDateProblem == 0 else np.NaN,axis=1))

    return df


def make_span(df):
    '''
    Makes a dataframe with a row for each fiscal year that each contract spans.
    Returns a dataframe.
    '''

    # Make a trimmed version of the dataset with only the records that have no
    # date problems and with only the contract number and starting and ending
    # fiscal years.
    df_trimmed = df[df['ContractDateProblem'] == 0]
    df_trimmed = df[['ContractNumber','FYStart','FYEnd']]
    df_trimmed = df_trimmed.drop_duplicates().reset_index(drop=True)

    # Create a new column that contains a list of all the fiscal years spanned
    # by each contract
    df_trimmed['Range'] = df_trimmed.apply(lambda x:
                         [y for y in range(x['FYStart'],x['FYEnd'] + 1)],axis=1)

    # Reshape the dataframe so that there is one row per FY per contract
    df_trimmed = df_trimmed.set_index('ContractNumber')
    spanner = df_trimmed['Range'].apply(pd.Series).stack().reset_index(level=0)
    spanner = spanner.rename(columns={0:'FY'},index=str).reset_index(drop=True)
    spanner['FY'] = spanner['FY'].apply(int)

    # Keep only these columns
    return spanner[['ContractNumber','FY']]


def make_map3b(spanner,ann_amts):
    '''
    Fills in the annual amount for each contract; splits the data into HQ and
    satellite dataframes. Drops unneeded columns and reorders the rest. Returns
    two dataframes.
    '''

    # Defines the order for the columns to keep
    keep = ['CSDS_Contract_ID','ContractNumber','Description',
            'Agency/Department','VendorName','VendorID','Amount',
            'EarliestStartDate','LatestEndDate','Category/ProcurementType',
            'Link/ContractPDF','CSDS_Vendor_ID','Address','City','State','ZipCode',
            'Jurisdic','Longitude','Latitude','Classification','Num_Svc_Locations',
            'Num_Total_Locations','Dollars_Per_Contract_Per_Location','FYStart',
            'FYEnd','FY','AnnualAmount']

    # Merges the annual amounts into the dataframe of fiscal years per contract
    merged = spanner.merge(ann_amts)

    # Keep only the records without a contract date problem
    merged = merged[merged['ContractDateProblem'] == 0]

    # Splits the data into HQ and satellite dataframes
    hq = merged[merged['HQ_Flag'] == 1].reset_index(drop=True)
    satellites = merged[merged['HQ_Flag'] == 0].reset_index(drop=True)

    # Drops unneeded columns and reorders the rest
    return hq[keep],satellites[keep]


def make_map3(hqb,satb):
    '''
    Aggregates the map 3b dataframes up to the location level. Returns two
    dataframes.
    '''

    # Defines the order for the first subset of columns to keep
    keep = ['CSDS_Vendor_ID','FY','VendorName']

    # Defines the order of the second subset of the columns to keep
    keep2 = ['Address','City','State','Longitude','Latitude']

    # Defines the last subset of the columns to keep
    z = ['ZipCode']

    # Shortcut
    anam = 'AnnualAmount'

    # Groups the map 3b HQ dataframe by the columns in keep, then sums the anam
    # column and converts the resulting series to a dataframe. Resets the index
    # to get the columns in keep back.
    hq_sum = hqb.groupby(keep)[anam].sum().to_frame().reset_index()

    # Keeps only the selected columns from the map 3b HQ dataframe, then drops
    # duplicates
    hqb_trimmed = hqb[keep + keep2 + z].drop_duplicates().reset_index(drop=True)

    # Merges the two modified dataframes such that the result has one line per
    # fiscal year per agency (with HQ address)
    hq = hqb_trimmed.merge(hq_sum,how='left')

    # Groups the map 3b satellite dataframe by the columns in keep + keep2, then
    # sums the anam column and converts the resulting series to a dataframe.
    # Resets the index to get back the columns in keep + keep2.
    sat_sum = satb.groupby(keep + keep2)[anam].sum().to_frame().reset_index()

    # Keeps only the selected columns from the map 3b satellites dataframe, then
    # drops duplicates
    satb_trimmed = satb[keep + keep2 + z].drop_duplicates().reset_index(drop=True)

    # Merges the two modified dataframes such that the result has one line per
    # fiscal year per location (with satelltie address)
    sat = satb_trimmed.merge(sat_sum,how='left')

    return hq.reset_index(drop=True),sat.reset_index(drop=True)


if __name__ == '__main__':

    # Total funds should be short $710,000 because of records w/ date problems.
    # New total should be $3809982646.12
    target = 3809982646.12
    print('Target:                                {0:,.2f}'.format(target))

    # contracts.Dollars_Per_Contract_Per_Location.sum() should be: 3810692646.12
    contracts = read_contracts()

    # Convert to one record (with a single amount) per contract
    dated = prep(contracts)

    # Assign the fiscal years in which each contract begins and ends
    fy_assigned = assign_fy(dated)

    # Calculate the annual amount for each contract (totalAmt / numFY)
    ann_amts = calc_ann_amt(fy_assigned)

    # Make the span of applicable FYs for each organization
    spanner = make_span(ann_amts)

    # Create the dataframes for map 3b
    map3b_hq,map3b_satellites = make_map3b(spanner,ann_amts)

    # Create the dataframes for map 3
    map3_hq,map3_satellites = make_map3(map3b_hq,map3b_satellites)

    # Validate that the amounts are correct
    print('Map 3 HQ + satellites annual amounts:  {0:,.2f}'.format(\
               map3_hq.AnnualAmount.sum() + map3_satellites.AnnualAmount.sum()))
    print('Difference between target and\n\tmap 3 HQ + satellites:\t\t\t   {0:,.2f}'.format(\
          map3_hq.AnnualAmount.sum() + map3_satellites.AnnualAmount.sum() - target))


    print('\nMap 3b HQ + satellites annual amounts: {0:,.2f}'.format(\
               map3b_hq.AnnualAmount.sum() + map3b_satellites.AnnualAmount.sum()))
    print('Difference between target and\n\tmap 3b HQ + satellites:\t\t\t   {0:,.2f}'.format(\
          map3b_hq.AnnualAmount.sum() + map3b_satellites.AnnualAmount.sum() - target))

    # Write to CSV
    map3_hq.to_csv(MAP3_HQ,index=False)
    map3_satellites.to_csv(MAP3_SATELLITES,index=False)

    map3b_hq.to_csv(MAP3B_HQ,index=False)
    map3b_satellites.to_csv(MAP3B_SATELLITES,index=False)

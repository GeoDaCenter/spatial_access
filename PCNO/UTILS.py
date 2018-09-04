import re
import numpy as np
import pandas as pd


def upper(df):
    '''
    Converts all strings (except for URLS in the Link/ContractPDF column) in a
    dataframe to uppercase. Returns a dataframe.
    '''

    # Print progress report
    print('Converting text columns to uppercase')

    # For every column:
    for col in df.columns:
        # If the column is type Object (holds strings) and isn't the Link column
        if df[col].dtype == 'O' and col != 'Link/ContractPDF':
            # Convert all the values to uppercase
            df[col] = df[col].str.upper()

    return df


def fix_zip(zipcode):
    '''
    Cleans zip codes that come in as a string, int, or float. Returns a string.
    '''

    # Convert string and strip off trailing '.0'
    zip_string = re.sub(r'\.0$','',str(zipcode))

    # Trim off +4 if there is one
    zip_string = re.sub(r'-[0-9]{4}$','',zip_string)

    return zip_string


def merge_coalesce(df1,df2,keys,suffix='_R',how='left'):
    '''
    Merges two dataframes with overlapping columns that do not match. Copies the
    values from the second dataframe into the first dataframe. The suffix should
    be a string that does not currently end any of the column names for either
    dataframe. The how argument defines what kind of join to make.

    Returns a dataframe.
    '''

    # Make a list of the columns in df2 that ARE NOT in df1
    cols = [x for x in df2.columns if x not in keys]

    # Rename those columns in df2 to have the suffix
    df2 = rename_cols(df2,cols,suffix)

    # Make the merge; replace the empty string with np.NaN
    df = pd.merge(df1,df2,how=how)
    df = df.replace('',np.NaN)

    # Coalesce values on the repeated columns
    # The repeated columns are the ones where col is in df1.columns and
    # (col + SUFFIX) is in df2.columns
    coal = [x for x in df1.columns if x + suffix in df2.columns]

    # Fill in empty spce in col with values from col + suffix
    for col in coal:
        df[col] = df[col].combine_first(df[col + suffix])

    # Drop the extra columns, those that end with the suffix
    drop = [x for x in df2.columns if x.endswith(suffix)]
    df = df.drop(drop,axis=1)

    # Replace np.NaN with the empty string
    return df.replace(np.NaN,'')


def rename_cols(df,cols,suffix='_R'):
    '''
    Adds a specified suffix to the names of specified columns. Returns a
    dataframe.
    '''

    # Define the list of new column names
    new = [x + suffix for x in cols]

    # Zip old and new names into a dictionary
    cn = dict(zip(cols,new))

    # Rename the columns
    df = df.rename(columns=cn,index=str)

    return df

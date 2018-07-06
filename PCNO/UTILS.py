import re
import numpy as np
import pandas as pd


def upper(df):
    '''
    Converts all strings (except for URLS in the Link/ContractPDF column) in a
    dataframe to uppercase. Returns a dataframe.
    '''

    print('Converting text columns to uppercase')

    for col in df.columns:
        if df[col].dtype == 'O' and col != 'Link/ContractPDF':
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
    values from the second dataframe into the first dataframe. Returns a
    dataframe.
    '''

    cols = [x for x in df2.columns if x not in keys]
    df2 = rename_cols(df2,cols,suffix)

    df = pd.merge(df1,df2,how=how)
    df = df.replace('',np.NaN)

    # Coalesce values on the repeated columns
    # The repeated columns are the ones where col is in df1.columns and
    # (col + SUFFIX) is in df2.columns
    coal = [x for x in df1.columns if x + suffix in df2.columns]

    for col in coal:
        df[col] = df[col].combine_first(df[col + suffix])

    # Drop the extra columns
    drop = [x for x in df2.columns if x.endswith(suffix)]
    df = df.drop(drop,axis=1)

    # Replace np.NaN with the empty string
    return df.replace(np.NaN,'')


def rename_cols(df,cols,suffix='_R'):
    '''
    Adds a specified suffix to the names of specified columns. Returns a
    dataframe.
    '''

    new = [x + suffix for x in cols]
    cn = dict(zip(cols,new))

    df = df.rename(columns=cn,index=str)

    return df

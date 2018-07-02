import re
import UTILS as u
import numpy as np
import pandas as pd
from string import punctuation, digits


STRIP_CHARS = punctuation + digits + ' '


def import_wchi(fname):
    '''
    Reads in the West Chi dataset. Splits the address field into its component
    parts. Converts strings to uppercase. Returns a dataframe.
    '''

    df = read_wc(fname)
    split = split_addr(df)
    df_upper = u.upper(split)

    return df_upper


def read_wc(fname):
    '''
    Reads in the West Chi dataset. Renames columns and drops others. Returns a
    dataframe.
    '''

    uc = ['name','address','postal_code','ComArea','WardArea','phone']
    cv = dict([(item,str) for item in uc[2:]])
    cols = {'name':'Name','address':'Address','postal_code':'ZipCode',
            'ComArea':'CommunityArea','WardArea':'Ward','phone':'Phone'}

    df = pd.read_csv(fname, usecols = uc, converters = cv)
    df = df.rename(columns = cols)

    return df


def split_addr(df):
    '''
    Splits the address into its component parts. Returns a dataframe.
    '''

    # Remove the country name and instances of commas following the state name;
    # expand the Address column into component parts, splitting on ', '
    new_cols = df['Address'].str.replace(' IL,',' IL').str.replace(', USA','')\
                            .str.split(pat=', ',n=0,expand=True)

    # Concatenate the original df and the new columns made from the Address col
    df = pd.concat([df,new_cols], axis=1)

    # Rename the new columns
    df = df.rename(columns = {0:'Address_both',1:'City',2:'State'},index=str)

    # Strip off forbidden characters from the State field
    df['State'] = df['State'].apply(lambda x: x.strip(STRIP_CHARS))

    # Expand the Address_both column into two parts
    new_cols = df['Address_both'].str.split(pat='; ',n=0,expand=True)

    # Concatenate the new columns to the dataframe, then rename them and drop
    # the other two address columns
    df = pd.concat([df,new_cols], axis=1)
    df = df.rename(columns = {0:'Address1',1:'Address2'},index=str)
    df = df.drop(['Address','Address_both'], axis = 1)

    # replace any empty fields with the empty string
    df = df.replace(np.NaN,'')

    df = df.drop_duplicates().reset_index(drop=True)

    return df

import re
import UTILS as u
import numpy as np
import pandas as pd
from string import punctuation, digits

# Define a constant of characters to strip off
STRIP_CHARS = punctuation + digits + ' '


def import_wchi(fname):
    '''
    Reads in the West Chi dataset. Splits the address field into its component
    parts. Converts strings to uppercase. Returns a dataframe.
    '''

    # Read in the WESTCHI file
    df = read_wc(fname)

    # Split addresses into their compnent parts
    split = split_addr(df)

    # Convert strings to uppercase
    df_upper = u.upper(split)

    return df_upper


def read_wc(fname):
    '''
    Reads in the West Chi dataset. Renames columns and drops others. Returns a
    dataframe.
    '''

    # Define columns to use
    uc = ['name','address','postal_code','ComArea','WardArea','phone']

    # Make a dictionary of converters (all to string)
    cv = dict([(item,str) for item in uc[2:]])

    # Read in file, using usecols and converters
    df = pd.read_csv(fname, usecols = uc, converters = cv)

    # Rename columns
    cols = {'name':'Name','address':'Address','postal_code':'ZipCode',
            'ComArea':'CommunityArea','WardArea':'Ward','phone':'Phone'}
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

    # Expand the Address_both column into two parts, splitting on '; '
    new_cols = df['Address_both'].str.split(pat='; ',n=0,expand=True)

    # Concatenate the new columns to the dataframe, then rename them and drop
    # the other two address columns
    df = pd.concat([df,new_cols], axis=1)
    df = df.rename(columns = {0:'Address1',1:'Address2'},index=str)
    df = df.drop(['Address','Address_both'], axis = 1)

    # replace any empty fields with the empty string
    df = df.replace(np.NaN,'')

    # Drop drop_duplicates and reset the index for good measure
    df = df.drop_duplicates().reset_index(drop=True)

    return df

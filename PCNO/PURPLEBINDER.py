import re
import UTILS as u
import numpy as np
import pandas as pd
from string import punctuation

# Drop the hyphen but add a space
PUNCTUATION = punctuation.replace('-',' ')


def import_pb(fname):
    '''
    Reads in the PurpleBinder dataset. Splits each record into multiple based on
    the number of locations contained in the locations field. Splits the
    location column into its component parts (Address1, Address2, City, State, &
    ZipCode) and then converts all the strings to uppercase.
    Returns a dataframe.
    '''

    # Read in the json file
    df = read_pb(fname)

    # Split the locations into multiple rows (one row per location)
    splitR = split_rows(df)

    # Split the location column into its component parts
    splitC = split_cols(splitR)

    # Convert string columns to uppercase
    df_upper = u.upper(splitC)

    return df_upper


def read_pb(fname):
    '''
    Reads in the PurpleBinder data from the JSON file specified in fname.
    Coalesces the organization_name and name fields. Replaces None values with
    the empty string. Transforms the locations field from a dictionary to a
    tuple of tuples of tuples. Converts the categories, datasets, and tags
    fields from lists to tuples. Drops duplicate records. Returns a dataframe.
    '''

    # Shortcuts
    org = 'organization_name'
    loc = 'locations'
    nm = 'name'

    # Read in json file
    df = pd.read_json(fname)

    # Pull in the 'name' field if org is blank
    df[org] = df.apply(lambda x: x[nm] if x[org] == '' else x[org],axis=1)

    # Replace None values
    df = df.apply(lambda x: '' if x is None else x,axis=1)

    # Convert dictionary to tuple of tuples of tuples; we'll break up the tuple
    # into strings later
    df[loc] = df[loc].apply(lambda x: tuple(tuple(y.items()) for y in x))

    # Convert lists to tuples, otherwise we can't drop duplicates
    convert = ['categories','datasets','tags']
    for col in convert:
        df[col] = df[col].apply(tuple)

    return df.drop_duplicates().reset_index(drop=True)


def splitters():
    '''
    Creates two constants, split_list and split_string. The former is a list of
    strings that are field labels and must be cleaned out of the location string
    and the latter is the strings concatenated and joined with pipes.
    '''

    a2 = r'address2'
    a1 = r'address'
    c = r'city'
    s = r'STATE'
    z = r'zipcode'
    la = r'YLatitude'
    lo = r'XLongitude'
    ca = r'community_area_id'

    split_list = [a2,a1,c,s,z,la,lo,ca]
    split_string = '|'.join(split_list)

    return split_list,split_string


def split_cols(df):
    '''
    Splits the Location column into multiple columns of address components.
    Returns a dataframe.
    '''

    # Shortcut
    loc = 'Location'

    # Hard-coded string replacement because otherwise cities like 'Palatine' and
    # 'Hoffman Estates' break (and a string with 'mailing address'; replacing
    # 'lng' to be consistent with the 'lat' replacement).
    df[loc] = df[loc].str.replace('\(lat, ','\(YLatitude, ')
    df[loc] = df[loc].str.replace('\(lng, ','\(XLongitude, ')
    df[loc] = df[loc].str.replace('\(state, ','\(STATE, ')
    df[loc] = df[loc].str.replace('\(mailing address','\(MailingAddr, ')

    # Get these constants
    split_list, split_string = splitters()

    # Make a dataframe called new_cols that uses re to split up the location
    # column with the split_string
    new_cols = df[loc].apply(lambda x: pd.Series([y for y in re.split(split_string,x)]))

    # Clean up the values a little
    new_cols = clean(new_cols,split_list)

    # Concatenate df and new_cols; drop the loc column
    merged = pd.concat([df, new_cols],axis=1)
    merged = merged.drop([loc],axis=1)

    return merged


def split_rows(pb):
    '''
    Splits the 'locations' field up into multiple rows, returning a dataframe
    with one row per location per organization name. Returns a dataframe.
    '''

    # Shortcuts
    lsplit = 'split_locations'
    loc = 'Location'
    locs = 'locations'
    vname = 'Name'
    oname = 'organization_name'

    # Create a new column, lsplit, from the locs column:
    # Convert tuple of tuples of tuples to string, joining with semicolons
    # Delete single quotes
    # Strip off extra semicolons
    pb[lsplit] = pb[locs].apply(lambda x: ''.join([str(chunk) + ';' for chunk in x]).replace("'",''))
    pb[lsplit] = pb[lsplit].str.strip(';')

    # Create a new dataframe from the lsplit column, grouping by oname
    splitter = pd.DataFrame(pb[lsplit].str.split(';').tolist(),index=pb[oname]).stack()

    # Reset the index, then keep the 0 and oname columns
    splitter = splitter.reset_index()[[0,oname]]

    # Rename the columns
    splitter.columns = [loc,vname]

    # Drop any duplicates and then reset the index
    splitter = splitter.drop_duplicates().reset_index(drop=True)

    return splitter


def clean(df,string_list):
    '''
    Cleans up the values after the addresses have been split into their
    component parts.
    '''

    # For every column in the dataframe:
    for col in df:
        # Strip off punctuation and spaces
        df[col] = df[col].str.strip(PUNCTUATION)
        # Clean up instances of the name of the column or of 'None'
        for string in string_list + ['None']:
            df[col] = df[col].str.replace(string,'')

    # Replace instances of the empty string with null, then drop records that
    # have null in all fields
    df = df.replace('',np.NaN)
    df = df.dropna(axis='columns',how='all')

    # Make a list of the new column names
    name_list = ['Address1','Address2','City','State','ZipCode','Latitude',
                 'Longitude','CommunityArea']

    # Make a dictionary that maps old name to new name, then rename the columns
    cn = dict(zip(list(df.columns),name_list))
    df = df.rename(columns=cn,index=str)

    return df.reset_index(drop=True)

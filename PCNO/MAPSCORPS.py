#import re
import UTILS as u
import numpy as np
import pandas as pd
from string import ascii_letters


def import_mc(fname,sheetname):
    '''
    Reads in one MapsCorps dataset. Replaces str(np.NaN) with the empty string.
    Converts string values to uppercase. Drops duplicates. Returns a dataframe.
    '''

    # Extracts the year from the sheetname
    year = get_year(sheetname)

    # Uses a different function to read in the file based on the year
    if year == 2009:
        df = read_2009(fname,sheetname)
    elif year == 2016:
        df = read_2016(fname,sheetname)

    # Replaces the string 'nan' (str(np.NaN)) with the empty string and converts
    # strings to uppercase
    df = df.replace('nan','')
    df_upper = u.upper(df)

    return df_upper.drop_duplicates().reset_index(drop=True)


def get_year(sheetname):
    '''
    Extracts the start year from the sheetname. Returns an integer.
    '''

    year = sheetname.strip(ascii_letters)
    year = int(year[0:4])

    return year


def read_2009(fname,sheetname):
    '''
    Reads the 2009 worksheet. Keeps only the records from the designated
    categories (per Dr. Marwell). Renames columns. Concatenates addresses. Adds
    the city (Chicago) and state (IL) for all entries. Returns a dataframe.
    '''

    # Reads in a specific sheet from the file, taking every field in as a string
    df = pd.read_excel(fname,sheetname,dtype=str)

    # Gets the categories for the 2009 file
    keep_cats = keep(2009)

    # Define some fieldnames
    pt = 'OrgTypeMain'
    pst = 'OrgTypeLabel'

    # Keep only records with categories in the keep_cats list
    df = df[df[pst].isin(keep_cats)].drop_duplicates().reset_index(drop=True)

    # Rename some fields
    cn = {'OrgName':'Name','CommArea':'CommunityArea','Unit':'Address2',
          'PostalCode':'ZipCode',pst:'SubType',pt:'Type'}
    df = df.rename(columns=cn,index=str)

    # Concatenate the address fields
    df['Address1'] = df.apply(lambda x: x['Addnum'] + ' ' + x['Street'],axis=1)

    # Set city and state fields because there aren't any in the dataset
    df['City'] = 'CHICAGO'
    df['State'] = 'IL'

    return df


def read_2016(fname,sheetname):
    '''
    Reads the 2016 worksheet. Keeps only the records from the designated
    categories (per Dr. Marwell). Renames columns. Concatenates addresses. Adds
    the state (IL) for all entries. Returns a dataframe.
    '''

    # Reads in a specific sheet from the file, taking every field in as a string
    original_df = pd.read_excel(fname,sheetname,dtype=str)

    # Define some fieldnames
    pt = 'PlaceType'
    pst = 'PlaceSubType'

    # Get the subtype from the keep function for the 2016 datset
    keep_sub = keep(2016)

    # Define these based on Dr. Marwell's instructions
    keep_type = ['Childcare and Schools',
                 'Health Services',
                 'Social Services & Political Advocacy']

    # Keep only records that meet Dr. Marwell's criteria
    df2 = original_df[original_df[pst].isin(keep_sub)]
    df3 = original_df[(original_df[pt].isin(keep_type)) & (original_df[pst] == 'Other')]

    # Concatenate the two dataframes
    df = pd.concat([df2,df3])

    # Rename columns
    cn = {'Unit':'Address2','Zip Code':'ZipCode','GeoArea':'CommunityArea',
          'PhoneNumber':'Phone',pt:'Type',pst:'SubType'}
    df = df.rename(columns=cn,index=str)

    # Replace 'nan' with '' in the Fraction field
    df['Fraction'] = df['Fraction'].replace('nan','')

    # Concatenate the address fields
    df['Address1'] = df.apply(lambda x: x['BuildingNumber'] + ' ' + x['Fraction'] + ' ' + x['Street'],axis=1)

    # Set the state to IL because it isn't in the original dataset
    df['State'] = 'IL'

    return df


def keep(year):
    '''
    Defines a list of categories to keep for the 2009-2015 or 2016 MapsCorps
    data. Returns a list of strings.
    '''

    # Categories to keep by year, according to Dr. Marwell

    if year == 2009:
        keep = ['Arts & Entertainment - Museum',
                'Arts & Entertainment - Other specify',
                'Arts & Entertainment - Perform',
                'Arts & Entertainment - Social Club',
                'Arts & Entertainment - Theater',
                'Health Service - Counseling ',
                'Health Service - Hospital',
                'Health Service - Mental Hospital ',
                'Health Service - Mobile health',
                'Health Service - Other specify',
                'Health Service - Out-patient',
                'Health Service - Rehab',
                'Health Service - Therapy',
                'Non-Res Religious - Church',
                'Non-Res Religious - Mosque',
                'Non-Res Religious - Other religious, specify',
                'Non-Res Religious - Other worship',
                'Non-Res Religious - Synagogue',
                'Other - Community Event',
                'Other - Community garden',
                'Other - Research group',
                'School & Childcare -Kid Center',
                'School & Childcare -Other educational specify',
                'School & Childcare -Private K-12',
                'School & Childcare -Private Univ',
                'School & Childcare -Seminary',
                'Service & Programmed Residential - Group home',
                'Service & Programmed Residential - Other specify',
                'Service & Programmed Residential - Religious',
                'Service & Programmed Residential - Senior',
                'Service & Programmed Residential - Shelter',
                'Soc Serv & Polit Advoc - Administrative ',
                'Soc Serv & Polit Advoc - Advocacy ',
                'Soc Serv & Polit Advoc - Child welfare',
                'Soc Serv & Polit Advoc - Disabled',
                'Soc Serv & Polit Advoc - Employment',
                'Soc Serv & Polit Advoc - Food Charity',
                'Soc Serv & Polit Advoc - Mobile Service',
                'Soc Serv & Polit Advoc - Other soc. service specify',
                'Soc Serv & Polit Advoc - Other specify',
                'Soc Serv & Polit Advoc - Senior ',
                'Soc Serv & Polit Advoc - Soc. Service Cntr.']

    elif year == 2016:
        keep = ['Administrative',
                'Advocacy',
                'Child welfare',
                'Church',
                'Community event',
                'Community garden',
                'Counselor',
                'Disabled',
                'Employment',
                'ER',
                'Food Charity',
                'Group home',
                'Hospital',
                'Kid Center',
                'Live theater',
                'Mobile health service',
                'Mosque',
                'Museum',
                'Other religious except residential',
                'Other social service',
                'Out-patient',
                'Performers & arts instructors',
                'Private University',
                'Private school K-12',
                'Public University',
                'Rehab inpatient',
                'Research body',
                'Seminary',
                'Senior',
                'Senior housing',
                'Shelter',
                'Social club',
                'Social service',
                'Synagogue',
                'Therapy outpatient']

    return keep

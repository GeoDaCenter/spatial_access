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

    year = get_year(sheetname)

    if year == 2009:
        df = read_2009(fname,sheetname)
    elif year == 2016:
        df = read_2016(fname,sheetname)

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

    df = pd.read_excel(fname,sheetname,dtype=str)

    keep_cats = keep(2009)

    pt = 'OrgTypeMain'
    pst = 'OrgTypeLabel'

    df = df[df[pst].isin(keep_cats)].drop_duplicates().reset_index(drop=True)

    cn = {'OrgName':'Name','CommArea':'CommunityArea','Unit':'Address2',
          'PostalCode':'ZipCode',pst:'SubType',pt:'Type'}

    df = df.rename(columns=cn,index=str)

    df['Address1'] = df.apply(lambda x: x['Addnum'] + ' ' + x['Street'],axis=1)

    df['City'] = 'CHICAGO'
    df['State'] = 'IL'

    return df


def read_2016(fname,sheetname):
    '''
    Reads the 2016 worksheet. Keeps only the records from the designated
    categories (per Dr. Marwell). Renames columns. Concatenates addresses. Adds
    the state (IL) for all entries. Returns a dataframe.
    '''
    original_df = pd.read_excel(fname,sheetname,dtype=str)

    pt = 'PlaceType'
    pst = 'PlaceSubType'

    keep_sub = keep(2016)
    keep_type = ['Childcare and Schools',
                 'Health Services',
                 'Social Services & Political Advocacy']

    df2 = original_df[original_df[pst].isin(keep_sub)]
    df3 = original_df[(original_df[pt].isin(keep_type)) & (original_df[pst] == 'Other')]

    df = pd.concat([df2,df3])

    cn = {'Unit':'Address2','Zip Code':'ZipCode','GeoArea':'CommunityArea',
          'PhoneNumber':'Phone',pt:'Type',pst:'SubType'}

    df = df.rename(columns=cn,index=str)

    df['Fraction'] = df['Fraction'].replace('nan','')

    df['Address1'] = df.apply(lambda x: x['BuildingNumber'] + ' ' + x['Fraction'] + ' ' + x['Street'],axis=1)

    df['State'] = 'IL'

    return df


def keep(year):
    '''
    Defines a list of categories to keep for the 2009-2015 or 2016 MapsCorps
    data. Returns a list of strings.
    '''

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

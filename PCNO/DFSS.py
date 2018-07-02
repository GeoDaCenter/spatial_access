import UTILS as u
import numpy as np
import pandas as pd


def import_dfss(fname):
    '''
    Reads in the DFSS dataset, converting strings to uppercase. Assigns an ID.
    Returns a dataframe.
    '''

    df = read_dfss(fname)

    df_upper = u.upper(df)

    return df_upper


def read_dfss(fname):
    '''
    Reads in the DFSS dataset. Renames columns. Returns a dataframe.
    '''

    uc = ['Agency','Site Name','Address','Address Line 2','City','State','ZIP',
          'Phone Number','Ward','Community Area','Community Area Number',
          'Latitude','Longitude']

    cv = dict([(x,str) for x in uc[0:-2]])

    df = pd.read_csv(fname,encoding='ISO-8859-1',usecols=uc,converters=cv)

    cn  = {'Agency':'Name','Site Name':'SiteName',
           'Address':'Address1','Address Line 2':'Address2','ZIP':'ZipCode',
           'Phone Number':'Phone','Community Area':'CommunityAreaName',
           'Community Area Number':'CommunityArea',}

    df = df.rename(columns=cn,index=str)

    df = df.drop_duplicates().reset_index(drop=True)

    return df

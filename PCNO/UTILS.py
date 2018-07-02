import numpy as np
import pandas as pd


def upper(df):
    '''
    Converts all strings (except for URLS in the Link/ContractPDF column) in a
    dataframe to uppercase. Returns a dataframe.
    '''

    print('\nConverting text columns to uppercase')

    for col in df.columns:
        if df[col].dtype == 'O' and col != 'Link/ContractPDF':
            df[col] = df[col].str.upper()

    return df

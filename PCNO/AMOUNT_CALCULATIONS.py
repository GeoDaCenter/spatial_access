import numpy as np
import pandas as pd


def clean_dollars(dollars):
    '''
    Takes in a dollar string, cleans it, and returns a float amount.
    '''

    if dollars.strip().upper() == 'INVALID':
        return np.NaN

    else:
        # Trim off leading '($' and replace with '-' (to signify negatives)
        dollars = dollars.replace('($','-')

        # Trim off trailing '$' and ')'
        dollars = dollars.strip('$)')

        # Remove commas
        dollars = dollars.replace(',','')

        return float(dollars)


def drop_low(df,thresh=.01):
    '''
    Takes in a dataframe of contracts. Drops contracts with an invalid dollar
    amount and those with an amount below a certain threshold (per JK). Returns
    a dataframe.
    '''

    a = 'Amount'

    # Drop NAs from the Amount column
    df = df.dropna(subset=[a])

    # Convert to float
    df[a] = df[a].apply(float)

    # Drop records with amounts below the threshold
    df = df[df[a] >= thresh]

    return df

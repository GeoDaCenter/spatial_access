#A script specifically to clean the contracts data

#Logan Noel (CSDS 2018)

import pandas as pd
import numpy as np


def clean_data(input_filename='MERGED_contracts_addresses.csv', output_filename='data/cleaned_contracts_data.csv'):
    df = pd.read_csv(input_filename)
    df['CSDS_Agency_ID'] = df['CSDS_Agency_ID'].str.upper()
    df['CSDS_AgencyAddress_ID'] = df['CSDS_AgencyAddress_ID'].str.upper()
    df['CSDS_Site_ID'] = df['CSDS_Agency_ID'] + df['CSDS_AgencyAddress_ID']
    df['Amount'] = df['Amount'].replace('[\$,]','',regex=True)
    df = df[['CSDS_Site_ID', 'Amount', 'Classification', 'X', 'Y']]
    df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce')
    df.dropna(axis=0, inplace=True, how='any')
    df.set_index('CSDS_Site_ID', inplace=True)

    rv = {}
    already_added = set()

    AMT_COL = df.columns.get_loc('Amount') + 1
    CLASS_COL = df.columns.get_loc('Classification') + 1
    X_COL = df.columns.get_loc('X') + 1
    Y_COL = df.columns.get_loc('Y') + 1
    ID_COL = 0
    finished = 0
    total = 0
    for data in df.itertuples():
        total += 1
        idx = data[ID_COL]
        amount = data[AMT_COL]
        cat = data[CLASS_COL]
        x = data[X_COL]
        y = data[Y_COL]
        if y < 41.594667900000005 or y > 42.072776599999997:
            continue
        elif x > -87.574800499999995 or x < -87.887844600000008:
            continue
        elif amount < 0:
            continue
        finished += 1
        if idx in already_added:
            rv[idx][0] += amount
        else:
            already_added.add(idx)
            rv[idx] = [amount, cat, x, y]

    res = pd.DataFrame.from_dict(rv, orient='index')

    res.to_csv(output_filename)
    print('excluded {} out of {}'.format(total - finished, total))
    return res


if __name__ == '__main__':
    clean_data()
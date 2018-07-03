import re
import UTILS as u
import numpy as np
import pandas as pd
import MATCH_NAMES as mn
import MERGE_CONTRACTS as mc
import IMPORT_ADDRESSES as ad
import AMOUNT_CALCULATIONS as ac
import ADDRESS_CLEANER as addclean
from STANDARDIZE_NAME import standardize_name as stdname

# Minimum Jaro-Winkler similarity required to deem two strings a match
JWSIM_THRESH = .9

# Minimum dollar amount required to keep a contract record
MIN_DOLLARS = .01

# File shortcuts
HQ = '../../../rcc-uchicago/PCNO/CSV/chicago/contracts_w_hq_addresses.csv'
OUT = '../../../rcc-uchicago/PCNO/CSV/chicago/prehq_contracts.csv'


def read_contracts():
    '''
    Reads in the contrats dataset via the MERGE_CONTRACTS module. Returns a
    dataframe.
    '''

    dfs = []

    for fname_tuple in mc.FNAMES:
        df = mc.process_dataset(fname_tuple)
        if fname_tuple[-1] == 'CHI':
            df = addclean.round2(df)
            df['Address1'] = df['Address1'].apply(addclean.address_cleaner)
        dfs.append(df)

    merged = pd.concat(dfs)

    merged = u.upper(merged)

    return merged   # 6591 records


def clean_amounts(df):
    '''
    Cleans dollar amounts with the clean_dollars function, then drops contracts
    with amounts below the MIN_DOLLARS threshold. Returns a dataframe.
    '''

    print('Cleaning amounts')

    # Shortcut
    a = 'Amount'

    df[a] = df[a].apply(ac.clean_dollars)

    df = ac.drop_low(df,MIN_DOLLARS)

    return df


def import_addresses(dataset):
    '''
    Reads in one of three address datasets (specified with a string). Returns a
    dataframe.
    '''

    print('Reading in {} addresses'.format(dataset.upper()))

    if dataset == 'cook':
        df = ad.read_cook_addr()
        df = df.rename(columns={'ID':'VendorName'},index=str)

    elif dataset == 'irs':
        df = ad.read_irs()
        df = df.rename(columns={'OrganizationName':'VendorName'},index=str)
        df['VendorName'] = df['VendorName'].apply(stdname)

    elif dataset == 'il':
        df = ad.read_il_addr()
        df['VendorName'] = df['VendorName'].apply(stdname)

    df = u.upper(df)

    return df


def jwsim_contracts_irs(contracts,irs,suffix):
    '''
    Takes the contracts and IRS dataframes and returns a dataframe of records
    with matching names (>= JWSIM_THRESH).
    '''

    # Rename the columns in IRS:
    irs = u.rename_cols(irs,irs.columns,suffix)

    # Restrict the contracts df to just those from IL
    contracts = contracts[contracts.CSDS_Contract_ID.str.startswith('IL')]

    # Take the cartesian product between the two; replace np.NaN with ''
    prod = mn.cart_prod(contracts,irs)
    prod = prod.replace(np.NaN,'')

    print('Calculating Jaro-Winkler similarity on vendor names')

    # Compute the Jaro-Winkler similarity on the VendorName cols
    col1 = 'VendorName'
    arg = ((prod,col1,col1 + suffix))
    jwsim = mn.parallelize(mn.jwsim,arg)

    return jwsim[jwsim.JWSimilarity >= JWSIM_THRESH]


def coalesce_matches(contracts,jwsim,suffix):
    '''
    Pulls in the addresses from IRS records previously deemed to match the IL
    agencies. Returns a dataframe.
    '''

    jwsim = trim_jwsim(jwsim,suffix)

    keys = ['CSDS_Contract_ID']

    df = u.merge_coalesce(contracts,jwsim,keys,suffix)

    return df


def trim_jwsim(jwsim,suffix):
    '''
    Trims off the original columns that were duplicated in the matching process
    as well as filtering out multiple matches per contract. Returns a dataframe.
    '''

    # Take the top match per contract
    jwsim = jwsim.sort_values('JWSimilarity',ascending=False)
    jwsim = jwsim.drop_duplicates(subset='CSDS_Contract_ID',keep='first')

    # Rename two columns that must be retained in the next step
    cn = {'VendorName_IRS':'IRSOrgName','CSDS_Org_ID_IRS':'CSDS_Org_ID'}
    jswim = jwsim.rename(columns=cn,index=str)

    # Keep only these cols
    keep = ['CSDS_Contract_ID'] + [x for x in jwsim.columns if 'IRS' in x]
    jwsim = jwsim[keep]

    # Make a dictionary of old to new names (stripping the suffix)
    old = [x for x in jwsim.columns if x.endswith(suffix)]
    new = [re.sub(suffix + '$','',x) for x in old]
    names = dict(zip(old,new))

    # Rename the columns as specified in the dictionary
    jwsim = jwsim.rename(columns=names,index=str)

    return jwsim


def preprocess_contracts():
    '''
    Reads in the contract records. Preprocesses them to clean the amounts and
    keep only those over the minimum amount specified in the MIN_DOLLARS
    constant.  Imports hand-collected addresses for Cook and IL contracts and
    merges in addresses from IRS990 forms to fill in as many blanks as possible.
    Returns a dataframe.
    '''

    contracts = read_contracts()
    contracts = clean_amounts(contracts)
    cook = import_addresses('cook')

    print('Coalescing COOK matches')
    merged = u.merge_coalesce(contracts,cook,'VendorName')
    merged['VendorName'] = merged['VendorName'].apply(stdname)

    irs = import_addresses('irs')

    sfx = '_IRS'
    jwsim = jwsim_contracts_irs(merged,irs,sfx)
    print('Coalescing IRS matches')
    coalesced = coalesce_matches(merged,jwsim,sfx)

    il = import_addresses('il')
    print('Coalescing IL matches')
    df = u.merge_coalesce(coalesced,il,'VendorName')

    return df


if __name__ == '__main__':

    df = preprocess_contracts()

    df.to_csv(OUT,index=False)

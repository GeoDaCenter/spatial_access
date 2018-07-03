import numpy as np
import pandas as pd
from itertools import repeat
from jellyfish import jaro_winkler as jw
from multiprocessing import cpu_count, Pool


def match_names(df1,df2,col1,col2,std=True,auto=False):
    '''
    NEEDS DOCUMENTATION

    Takes in two dataframes and a column name from each, standardizes the values
    in the two columns, and returns a dataframe of the Cartesian product of the
    dataframes with the Jaro-Winkler similarity of the values in the columns.
    '''

    if std:
        df1[col1] = df1[col1].apply(stdname)
        df2[col2] = df2[col2].apply(stdname)

    prod = cart_prod(df1,df2,((col1,col2)))

    arg = ((prod,col1,col2))
    jws = parallelize(jwsim,arg)

    return jws


def cart_prod(df1,df2,auto=False):
    '''
    NEEDS DOCUMENTATION

    Takes the Cartesian product of two different dataframes (for which column
    names do not overlap). Returns a dataframe.
    '''

    k = 'key'

    # In each df, create a key column with all the same values
    df1 = df1.assign(key=0)
    df2 = df2.assign(key=0)

    print('Taking a Cartesian product')

    if not auto:
        # Take the Cartesian product of the two dataframes
        prod = pd.merge(df1,df2,on=k)
        # Drop the added column
        prod = prod.drop(k,axis=1)

    else:
        df1 = df1.assign(ix1=[x for x in range(len(df1))])
        df2 = df2.assign(ix2=[x for x in range(len(df2))])
        prod = pd.merge(df1,df2,on=k)
        prod = prod.drop(k,axis=1)
        prod = prod[prod['ix1'] < prod['ix2']]
        prod = prod.drop(['ix1','ix2'],axis=1)

    return prod


def disambiguate_names(df,key,ids):
    '''
    NEEDS DOCUMENTATION

    For an auto-cartesian product
    key is the column to be matched
    ids is the (list of) column(s) that identify each record
    '''

    if type(ids) != list:
        ids = [ids]

    df1 = df[[key] + ids].copy()

    df2 = u.rename_cols(df1.copy(),[key] + ids,'_R')

    jws = mn.match_names(df1,df2,key,key + '_R',False)

    return jws


def jwsim(args):
    '''
    TAKES A SINGLE PARAMETER, A TUPLE of a dataframe and a tuple of colnames.
    Caclulates the Jaro-Winkler similarity between the two specified columns of
    the given dataframe. Returns a dataframe.
    '''

    df, cols = args
    col1, col2 = cols

    print('.')

    df['JWSimilarity'] = df.apply(lambda x: jw(x[col1],x[col2]),axis=1)

    return df


def parallelize(function,tuple):
    '''
    Adapted from http://blog.adeel.io/2016/11/06/parallelize-pandas-map-or-apply

    Parallelizes function, which is called on the parts of tuple (which are,
    respectively, the dataframe and the two columns on which the function will
    be called).
    '''

    df,col1,col2 = tuple

    print('\nCalculating Jaro-Winkler similarity on {} and {}'.format(col1,col2))

    cores = cpu_count()
    partitions = cores * 4
    data_split = np.array_split(df, partitions)
    pool = Pool(cores)
    data = pd.concat(pool.map(function, zip(data_split,repeat((col1,col2)))))
    pool.close()
    pool.join()
    return data

import numpy as np
import pandas as pd
from itertools import repeat
from jellyfish import jaro_winkler as jw
from multiprocessing import cpu_count, Pool


def cart_prod(df1,df2,auto=False):
    '''
    NEEDS DOCUMENTATION

    Takes the Cartesian product of two different dataframes (for which column
    names do not overlap); optionally, takes the Cartesian product of a
    dataframe with itself. Returns a dataframe.
    '''

    k = 'key'

    # In each df, create a key column with all the same values
    df1 = df1.assign(key=0)
    df2 = df2.assign(key=0)

    print('Taking a Cartesian product')

    if not auto:
        # Take the Cartesian product of the two dataframes (by matching k in one
        # dataframe to k in the other dataframe, where all values for k are
        # equal; thus, every row in df1 is matched with every row in df2)
        prod = pd.merge(df1,df2,on=k)
        # Drop the added column
        prod = prod.drop(k,axis=1)

    else:
        # Take the Cartesian product of the dataframe with itself (by matching
        # every row in the dataframe to itself)
        df1 = df1.assign(ix1=[x for x in range(len(df1))])
        df2 = df2.assign(ix2=[x for x in range(len(df2))])
        prod = pd.merge(df1,df2,on=k)
        # Drop the key column
        prod = prod.drop(k,axis=1)
        # Drop duplicate rows
        prod = prod[prod['ix1'] < prod['ix2']]
        # Drop the added columns
        prod = prod.drop(['ix1','ix2'],axis=1)

    return prod


def jwsim(args):
    '''
    TAKES A SINGLE PARAMETER, A TUPLE of a dataframe and a tuple of colnames.
    Caclulates the Jaro-Winkler similarity between the two specified columns of
    the given dataframe. Returns a dataframe.
    '''

    # Unpack the arguments
    df, cols = args
    col1, col2 = cols

    # Print this to show that the program is still running
    print('.')

    # Take the JW similarity for strings in col1 and col2 and store it in a new
    # column
    df['JWSimilarity'] = df.apply(lambda x: jw(x[col1],x[col2]),axis=1)

    return df


def parallelize(function,tuple):
    '''
    Adapted from http://blog.adeel.io/2016/11/06/parallelize-pandas-map-or-apply

    Parallelizes function, which is called on the parts of tuple (which are,
    respectively, the dataframe and the two columns on which the function will
    be called).
    '''

    # Unpack the arguments
    df,col1,col2 = tuple

    # Print progress statement
    print('\nCalculating Jaro-Winkler similarity on {} and {}'.format(col1,col2))

    # Determine how many cores the machine has
    cores = cpu_count()

    # Calculate how many partitions into which to segment the data
    partitions = cores * 4

    # Split the dataframe into however many partitions
    data_split = np.array_split(df, partitions)

    # Initialize a pool
    pool = Pool(cores)

    # Parallelize the function with the arguments, then concatenate the results
    data = pd.concat(pool.map(function, zip(data_split,repeat((col1,col2)))))
    pool.close()
    pool.join()

    return data

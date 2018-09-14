import re
import UTILS as u
import pandas as pd
import itertools as it
import usaddress as add


def fix_duplicate_addresses(df,key='ClusterID',target='Address_SVC'):
    '''
    Takes in a dataframe. Attempts to fix duplicate addresses (by default, in
    the 'Address_SVC' field) if they have the same key (bby default, the
    'ClusterID' field). Returns a dataframe.
    '''

    print('\nFixing duplicate addresses')

    # Sort the target field by length, longest to shortest
    sorter = df[target].str.len().sort_values(ascending=False).index
    df = df.reindex(sorter)

    # Make a mini version of the dataframe with two fields, the key & the target
    # (which has been renamed to indicate it's the original field)
    minimized_df = df[[key,target]].drop_duplicates().dropna()
    minimized_df[target + '_Original'] = minimized_df[target]

    # Make a list of the unique values in the key field
    unique_keys = list(minimized_df[key].unique())

    # Set a flag to FALSE
    new_df_exists = False


    # OVERVIEW: Call the iter_df() function on subsets of the dataframe (one
    # subset per key) to compare and fix the address strings assigned to that
    # key.

    # For each value in the list of unique keys:
        # Make a mini dataframe that is just the rows corresponding to that key
        # If the there is more than 1 row:
            # Call iter_df() on the mini df & assign the result to local_df2
            # If the new_df_exists flag is set to TRUE:
                # Create new_df by concatenating the existing new_df and local_df2
            # else: Assign the name new_df to local_df2 and set the new_df_exists to TRUE
    for uKey in unique_keys:
        local_df = minimized_df[minimized_df[key] == uKey]
        if len(local_df) > 1:
            local_df2 = iter_df(local_df.copy().drop_duplicates().reset_index(drop=True),target)
            if new_df_exists:
                new_df = pd.concat([new_df,local_df2])
            else:
                new_df = local_df2
                new_df_exists = True

    print('Coalescing fixed addresses')

    # Rename the columns in preparation of calling merge_coalesce()
    new_cols = {target:target + '_COAL',target + '_Original':target}
    new_df = new_df.rename(columns=new_cols,index=str)

    # Rename the columns in preparation of calling merge_coalesce()
    min_cols = {target + '_Original':target + '_COAL'}
    minimized_df = minimized_df.rename(columns=min_cols,index=str)

    # Coalesce with the dfs in this order so that we keep the new values
    merged = u.merge_coalesce(new_df,minimized_df,[key,target],how='right')

    # Merge the new address strings in, drop the original field, and rename the
    # new one
    df = df.merge(merged,how='left').drop(target,axis=1)
    df = df.rename(columns={target + '_COAL':target},index=str)

    return df


def iter_df(df,field):
    '''
    Goes through a dataframe and compares each address string to all other
    address strings. Updates all matches so that they have the exact same string
    (if A matches B and B matches C, updates B and C so that they match A).
    Returns a dataframe.
    '''

    # Resets the index so that the lower index is always listed first.
    df = df.reset_index(drop=True)

    # For every pair of indices:
        # Set string1 to the target value at the first index
        # Set string2 to the target value at the second index
        # Compare the strings
            # If one requires a fix, call update_df() and fix it
    for idx1, idx2 in it.combinations(range(len(df)),2):
        string1 = df.loc[idx1,field]
        string2 = df.loc[idx2,field]
        result, fix = pairwise_comparison(string1,string2)
        if result:
            if fix:
                df = update_df(df,field,idx1,idx2)
        else:
            pass

    return df


def update_df(df,field,idx1,idx2):
    '''
    Takes a dataframe, the name of a target field, and the two indices to be
    considered. Updates the value in the target field at the higher of the two
    indices to equal the value at the lower index. Returns a dataframe.
    '''

    # Find out which is higher and which is lower
    min_idx = min(idx1,idx2)
    max_idx = max(idx1,idx2)

    # Copy the target string from the value at the lower index
    target_string = df.loc[min_idx,field]

    # Set the value at the higher index to the target string
    df.loc[max_idx,field] = target_string

    return df


def pairwise_comparison(string1,string2):
    '''
    Parses two strings into usaddress dictionaries, then compares the
    dictionaries to assess whether the addresses are the same. Returns True if
    so and False if not. Also returns a list with the names of the fields (if
    any) that need to be fixed. (The results are used for flow control in the
    iter_df() function.)
    '''

    forbidden = {'251 EAST HURON 541 NORTH FAIRBANKS':'251 EAST HURON STREET'}

    for key,val in forbidden.items():
        if string1 == key:
            string1 = val
        if string2 == key:
            string2 = val


    # What about the city, state, and zip? Should those be concatenated and
    # considered, too? Possibly consider this in future work.


    # Parse the addresses into dictionaries
    s1_dicto = add.tag(string1)[0]
    s2_dicto = add.tag(string2)[0]

    # Set a flag to its default value
    same = True

    # This will hold the names of fields that need to be fixed
    fix = []

    # Allow '123 Central' and '123 Central Avenue' to match, but mark for fixing
    # This first statement is in case the street type is in the second string
    # but not in the first
    if 'StreetNamePostType' not in s1_dicto.keys() and 'StreetNamePostType' in \
        s2_dicto.keys():
        fix.append('StreetNamePostType')


    # Compare the address strings by part
    for key, value1 in s1_dicto.items():
        # If string1 has street type and string2 doesn't, mark for fixing; but
        # if string2 does and they don't match, mark for fixing
        if key == 'StreetNamePostType':
            if key in s2_dicto.keys():
                if value1 != s2_dicto[key]:
                    fix.append(key)
            else:
                fix.append(key)
            continue
        # The component is also present in string2, assign its value to value2
        if key in s2_dicto.keys():
            value2 = s2_dicto[key]
        # Otherwise, mark for fixing and start again with the next key
        else:
            fix.append(key)
            continue
        # AddressNumber must match exactly; if not, mark as False and exit loop
        if key == 'AddressNumber':
            if value1 == value2:
                continue
            else:
                same = False
                break
        # If non-AddressNumber values match, continue
        elif value1 == value2:
            continue
        # Otherwise, check if one is a substring of the other and if so, mark
        # for fixing
        elif is_substring(value1,value2):
            fix.append(key)
            continue
        # If they don't match, mark as False and exit loop
        else:
            same = False
            break

    # If either dictionary has a single key and the shorter one is not a
    # substring of the other, then mark as False
    if len(s1_dicto) == 1 and not is_substring(string1,string2):
        same = False
    elif len(s2_dicto) == 1 and not is_substring(string2,string1):
        same = False

    return same, fix


def ns(string):
    '''
    Removes all the spaces from a string. Returns a string.
    '''

    ns_string = string.replace(' ','')

    return ns_string


def is_substring(string1,string2):
    '''
    Evaluates whether either string is a substring of the other. If not, removes
    spaces from both strings and then checks. Returns a boolean.
    '''

    if not re.findall(string1,string2):
        if not re.findall(string2,string1):
            if not re.findall(ns(string1),ns(string2)):
                if not re.findall(ns(string2),ns(string1)):
                    return False

    return True

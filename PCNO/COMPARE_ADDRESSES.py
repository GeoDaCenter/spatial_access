import re
import pandas as pd
import itertools as it
import usaddress as add


def fix_duplicate_addresses(df,key='ClusterID',target='Address_SVC'):
    '''
    '''

    sorter = df[target].str.len().sort_values(ascending=False).index
    df = df.reindex(sorter)
    #df = df.sort_values(by=key)
    #df = df.assign(ID=df[key])

    #key = [key]

    minimized_df = df[[key,target]].drop_duplicates().dropna()#.loc[:,[key,target]]
    minimized_df[target + '_Original'] = minimized_df[target]
    #print(minimized_df)
    unique_keys = list(df[key].unique())

    new_df_exists = False

    for uKey in unique_keys:
        local_df = minimized_df[minimized_df[key] == uKey]
        if len(local_df) > 1:
            local_df2 = iter_df(local_df.copy().drop_duplicates().reset_index(drop=True),target)
            if new_df_exists:
                new_df = pd.concat([new_df,local_df2])
            else:
                new_df = local_df2
                new_df_exists = True
            if local_df2[key].max() == '134': # is next
                print(local_df)
                print(local_df2)
                print('---------------------------------------------------------------')

    # Need to merge changes back into the original df

    new_df = new_df.rename(columns={target:target + '_Fixed',target + '_Original':target},index=str)
    #minimized_df = minimized_df.rename(columns={target + '_Original':target},index=str)
    print('\nnew_df:')
    for col in new_df.columns:
        print(col)
    print('\nminimized_df:')
    for col in minimized_df.columns:
        print(col)
    merged = minimized_df.merge(new_df,on=[key,target],how='left')

    # Need to add an ID to the original so that I can merge the fixed values back in

    return merged.drop(target,axis=1)


def iter_df(df,field):
    '''
    '''

    df = df.reset_index(drop=True)

    matches, unmatches = [], []

    for idx1, idx2 in it.combinations(range(len(df)),2):
        string1 = df.loc[idx1,field]
        string2 = df.loc[idx2,field]
        result, fix = pairwise_comparison(string1,string2)
        if result:
            matches.append(tuple((idx1,idx2)))
            if fix:
                df = update_df(df,field,idx1,idx2)
        else:
            unmatches.append(tuple((idx1,idx2)))

    return df


def update_df(df,field,idx1,idx2):
    '''
    '''

    min_idx = min(idx1,idx2)
    max_idx = max(idx1,idx2)

    target_string = df.loc[min_idx,field]
    df.loc[max_idx,field] = target_string

    return df


def pairwise_comparison(string1,string2):
    '''
    Parses two strings into usaddress dictionaries, then compares the
    dictionaries to assess whether the addresses are the same. Returns True if
    so and False if not.
    '''

    #What about the city, state, and zip? Should those be concatenated and considered, too?

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


# DEPRECATED FUNCTION
def compare_addresses(df,address_field):
    '''
    Takes a dataframe and the name of an address field, then does pairwise
    comparisons on the strings in the field. Returns True if they are all the
    same and False if at least one is different.
    '''

    same = True

    for string1, string2 in it.combinations(df[field],2):
        same = pairwise_comparison(string1,string2)
        if not same:
            break

    return same

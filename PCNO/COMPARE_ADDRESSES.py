import re
import itertools as it
import usaddress as add





def pairwise_comparison(string1,string2):
    '''
    Parses two strings into usaddress dictionaries, then compares the
    dictionaries to assess whether the addresses are the same. Returns True if
    so and False if not.
    '''

    s1_dicto = add.tag(string1)[0]
    s2_dicto = add.tag(string2)[0]

    same = True

    for key, value1 in s1_dicto.items():
        value2 = s2_dicto[key]
        if value1 == value2:
            continue
        elif re.findall(value1,value2) or re.findall(value2,value1):
            continue
        else:
            same = False
            break

    return same


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

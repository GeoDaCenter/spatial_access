import re
from string import digits
import ADDRESS_CLEANER as ac


def address_cleaner(string):
    '''
    Cleans a string based on the peculiarities of the PurpleBinder, West Chi,
    DFSS, and MapsCorps datasets. Returns a string.
    '''

    string = string.strip()

    blocked = ['CALL FOR DETAILS','CONFIDENTIAL LOCATION','BASEMENT',
               'CONFIDENTIAL','UNDISCLOSED LOCATION','MULTIPLE LOCATIONS',
               'UNDISCLOSED LOCATION- NORTHSIDE','MULTIPLE LOCATIONS CHICAGO',
               'DV SHELTER']

    for item in blocked:
        if string == item:
            return ''

    if string.startswith('PHONE') or string.startswith('OFFICE PHONE') or \
        string == 'EDWARD HEALTH & FITNESS CENTER â€” SEVEN BRIDGES':
        return ''

    if string.endswith(' FLOOR') or string.endswith(' FL'):
        string = re.sub(r'[0-9]+(ST|ND|RD|TH) FLOOR$','',string)
        string = re.sub(r'[0-9]+(ST|ND|RD|TH) FL$','',string)

    elif string.endswith('ADH (MC 345)'):
        string = string[0:-len('ADH (MC 345)')]

    # Replace multiple spaces with a single space; replace'C/O'; replace forward
    # slashes
    string = re.sub(r'\s+',' ',string)
    string = re.sub(r'C/O',' ',string)
    string = re.sub(r'/',' ',string)

    # Replace abbreviated directions with full words
    string = re.sub(r'(\s|^)E\.?(?=\s|$)',' EAST',string)
    string = re.sub(r'(\s|^)W\.?(?=\s|$)',' WEST',string)
    string = re.sub(r'(\s|^)N\.?(?=\s|$)',' NORTH',string)
    string = re.sub(r'(\s|^)S\.?(?=\s|$)',' SOUTH',string)

    # Define a dictionary of characters on which to split (dictionary because of
    # the challenge with raw strings and backslashes)
    split_chars = {',':',',
                   '\(':'(',
                   '\)':')',
                   ' - ':' - ',
                   r'\\':'\\',
                   ':':':'}

   # For every key, value pair in the split_chars dictionary:
    for key, value in split_chars.items():
        # If key is found within string:
        if re.findall(key,string):
            # Call splitter on string with value
            string = splitter(string,value)

    # Hard-coding a weird prefix found on some strings
    string = re.sub(r'^C4\s(\s|[A-Z])+(?=([0-9]+\s))','',string)

    # Clean up encoding issues with O'Hare
    string = re.sub(r'O(.)*HARE (INTERNATIONAL )?AIRPORT$','O\'HARE INTERNATIONAL AIRPORT',string)

    # Hard-coded cleanup for strings that end in the word PHONE
    string = re.sub(r' PHONE$','',string)

    # Hard-coded clean-up for strings ending in an ampersand
    string = string.strip(' &')

    # This address is causing irremediable problems, so just take the first one
    if string == '4944 AND 4909 WEST HURON':
        #print(string)
        return '4944 WEST HURON'

    # If the address is supposed to end in a number (like a state/cty/US hwy),
    # return it. Else, clean it some more.
    if re.findall(r' ROUTE [0-9]+$',string):
        return string
    else:
        return ac.address_cleaner(string)


def splitter(string,char):
    '''
    Splits a string into pieces, keeping the parts that appear to contain a real
    address. Returns a string.
    '''

    # Split the string and declare an empty list where pieces will be appended
    split_list = string.split(char)
    keep = []

    # If the address in the second item is a substring of the address in the
    # first item, AND it's not a valid address, strip it out of the first item
    # and return what's left over
    if len(split_list) == 2:
        a,b = split_list
        if a.startswith(b):
            if not re.findall(r'[0-9]\s[A-Z0-9]+',b):
                return a.lstrip(b)

        # If there's a valid address in each string, return the address from the
        # first string
        elif re.findall(r'[0-9]\s[A-Z0-9]+',a) and re.findall(r'[0-9]\s[A-Z0-9]+',b):
            return a

    # If there's an address or an ampersand in the item, keep it
    for item in split_list:
        item = item.strip()
        if re.findall(r'[0-9]+\s[A-Z0-9]+',item) or re.findall(r'&',item):
            keep.append(item)

    # Join the pieces back together and condense multiple spaces
    string = ' '.join(keep)
    string = re.sub(r'\s+',' ',string)

    return string


def clean_zips(df):
    '''
    Cleans zip codes by trimming off +4s and deleting strings longer than five
    digits. Returns a dataframe.
    '''

    zipc = 'ZipCode'

    df[zipc] = df[zipc].apply(lambda x: x.split('-')[0])
    df[zipc] = df[zipc].apply(lambda x: x if len(x) == 5 else '')

    return df


def full_cleaning(df):
    '''
    Cleans each address field, then combines the two and cleans them together.
    Calls the zip code cleaner. Returns a dataframe.
    '''

    df['Address1'] = df['Address1'].apply(address_cleaner)
    df['Address2'] = df['Address2'].apply(address_cleaner)

    df['Address'] = df.apply(lambda x: x['Address1'] + ',' + x['Address2'],axis=1)
    df['Address'] = df['Address'].apply(address_cleaner)

    df = df.drop(['Address1','Address2'],axis=1)

    df = clean_zips(df)

    return df

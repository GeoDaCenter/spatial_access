import numpy as np
import pandas as pd
from datetime import datetime as dt


# FNAMES is a list of tuples. There is one tuple per original dataset. The tuple
# consists of the original filename, the output filename, and a label that will
# be used to identify the records in that dataset.
FNAMES = [tuple(('../../../PCNO/CSV/chicago/originals/Cook County contracts.csv','COOK')),
          tuple(('../../../PCNO/CSV/chicago/originals/City of Chicago contracts delegates blanks.csv','CHI')),
          tuple(('../../../PCNO/CSV/chicago/originals/IL State Contracts w Keep column.csv', 'IL'))]

# CLEANER contains non-printing characters that will be cleaned out of strings.
CLEANER = ['\n','\r','\t']

# FIELDS is the union of the field names in both the original datasets minus the
# Start Date, Link, and Contract PDF fields, which are processed differently.
FIELDS = ['Contract Number','Vendor Number','Vendor Name','Amount',
          'Description','System Release','Lead Department','Start Date',
          'End Date','Category','Purchase Order Description',
          'Purchase Order (Contract) Number','Revision Number',
          'Specification Number','Contract Type','Approval Date','Department',
          'Vendor ID','Address 1','Address 2','City','State','Zip',
          'Award Amount','Procurement Type']

# We want to keep only contracts with a start date on or since 01/01/2012.
BEGIN_DATE = dt.strptime('1/1/12','%m/%d/%y')


def date_fixer(date_string):
    '''
    Fixes dates that come in 'mm/dd/yy' format and changes them to datetime.
    If there is no date, returns datetime for 01/01/1900.
    '''

    if not date_string:
        return dt.strptime('1/1/1900','%m/%d/%Y')
    else:
        return dt.strptime(date_string,'%m/%d/%y')


def text_cleaner(string):
    '''
    Cleans strings of text by replacing forbidden characters with spaces,
    removing instances of the replacement character, stripping leading and
    trailing whitespace, and converting to uppercase.
    '''

    # If present in the string, replace each NPC from CLEANER with a space
    for npc in CLEANER:
        string = string.replace(npc, ' ')

    # Remove replacement character, which will break things later on; strip
    # leading and trailing spaces; convert to uppercase
    return string.replace('�','').strip().upper()


def link_cleaner(link):
    '''
    Cleans links by deleting forbidden characters.
    '''

    # If present in the string, delete each NPC from CLEANER
    for npc in CLEANER:
        link = link.replace(npc, '')

    # Remove replacement character, which will break things later on; strip
    # leading and trailing spaces
    return link.replace('�','').strip()


def process_dataset(fname_tuple):
    '''
    Reads in a CSV file, sending most fields through the text_cleaner() function
    and keeping only designated records. Sends the link fields through a link
    cleaner and the date fields through a datefixer.
    '''

    # Unpack the tuple into its parts
    fnamein, label = fname_tuple

    if label == 'IL':
        cn = ['FY','Agency Code','Agency','Contract Number','Award Description',
              'Type Description','Class Description','Vendor Name','Vendor 2',
              'Start Date','End Date','Current Contract Amount',
              'Planned Contract Amount','Current Expended Amount','Keep']

        cv = dict([(field, text_cleaner) for field in cn])
        cv['Start Date'] = date_fixer
        cv['End Date'] = date_fixer

        print('Reading IL')
        df = pd.read_csv(fnamein, names = cn, converters = cv, skiprows = 1)

    else:
        # Dictionary of converters (all text fields get sent to text_cleaner)
        cv = dict([(field, text_cleaner) for field in FIELDS])
        cv['Start Date'] = date_fixer
        cv['End Date'] = date_fixer
        cv['Approval Date'] = date_fixer
        cv['Link'] = link_cleaner
        cv['Contract PDF'] = link_cleaner

        print('Reading {}'.format(label))

        # Read in the file and use the converters dictionary
        df = pd.read_csv(fnamein, converters = cv)

    # Omit when the 'Keep' column is not equal to 'y' or 'Y'; drop duplicates
    df = df[df.Keep.str.strip().str.upper() == 'Y']
    df = df.drop_duplicates()

    # Keep only contracts with a start date on or since the begin date.
    df = df[df['Start Date'] >= BEGIN_DATE]

    # Create a sequential CSDS contract ID for each record
    df = df.assign(CSDS_Contract_ID=[label + str(x + 1) for x in range(len(df))])

    # Replace np.nan and empty strings with 'INVALID' (or else the ML breaks)
    df = df.replace(np.nan,'INVALID').replace('','INVALID')

    df = trimmer(df,label)

    return df


def trimmer(df,label):
    '''
    Trims and pads the dataframe so that it has the right columns. Returns a
    dataframe.
    '''

    keep = ['CSDS_Contract_ID','ContractNumber','Description','Agency/Department',
            'VendorName','VendorID','Amount','StartDate','EndDate',
            'Category/ProcurementType','Link/ContractPDF',
            'Address1','Address2','City','State','ZipCode']


    if label == 'COOK':
        cn = {'Contract Number':'ContractNumber','Vendor Number':'VendorID',
              'Lead Department':'Agency/Department','Start Date':'StartDate',
              'End Date':'EndDate','Link':'Link/ContractPDF',
              'Category':'Category/ProcurementType','Vendor Name':'VendorName'}

    elif label == 'CHI':
        cn = {'Purchase Order Description':'Description',
              'Purchase Order (Contract) Number':'ContractNumber',
              'Start Date':'StartDate','End Date':'EndDate',
              'Department':'Agency/Department','Vendor Name':'VendorName',
              'Vendor ID':'VendorID','Address 1':'Address1',
              'Address 2':'Address2','Zip':'ZipCode','Award Amount':'Amount',
              'Procurement Type':'Category/ProcurementType',
              'Contract PDF':'Link/ContractPDF'}

    elif label == 'IL':

        amounts = ['Current Contract Amount','Planned Contract Amount',
                   'Current Expended Amount']

        descriptions = ['Award Description','Type Description','Class Description']

        df['Amount'] = df[amounts].max(axis=1).apply(str)
        df['Description'] = df[descriptions].apply(lambda x: ' || '.join(x), axis=1)

        df = df.drop(amounts + descriptions, axis=1)

        cn = {'Agency':'Agency/Department','Contract Number':'ContractNumber',
        'Vendor Name':'VendorName','Start Date':'StartDate',
        'End Date':'EndDate'}


    df = df.rename(columns=cn,index=str)

    for col in keep:
        if col not in df.columns:
            df[col] = ''

    return df[keep].drop_duplicates().reset_index(drop=True)

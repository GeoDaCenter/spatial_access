import map2 as m2
import numpy as np
import pandas as pd


# This script was written because of problems resulting from earlier mistakes in
# a different script. If running everything from the beginning, and geocoding
# files along the way, this script will probably not be necessary; it has thus
# been omitted from the readme.


GEO1 = '../../../rcc-uchicago/PCNO/CSV/chicago/Geocoded Service Addresses/map2_geocoding_geocoded.csv'
GEO2 = '../../../rcc-uchicago/PCNO/CSV/chicago/Geocoded Service Addresses/map2_geocoding_version2_geocoded.csv'
NEEDS = '../../../rcc-uchicago/PCNO/CSV/chicago/map2_geocoding_version2.csv'
OUT = '../../../rcc-uchicago/PCNO/CSV/chicago/map2_geocoding_version3.csv'


def still_needs():
    '''
    Concatenates GEO1 and GEO2, then merges in NEEDS to determine which address
    strings still need to be geocoded. Returns a dataframe.
    '''

    # Define a converter dictionary for reading in files
    cv = {'Zip':str}

    # Read in a geocoded file, then rename a column
    geo1 = pd.read_csv(GEO1,converters=cv)
    geo1 = geo1.rename(columns={'CSDS_Org_ID':'ID'},index=str)

    # Read in another geocoded file
    geo2 = pd.read_csv(GEO2,converters=cv)

    # Concatenate the two geocoded files, then drop the 'Match Score' column
    master = pd.concat([geo1,geo2])
    master = master.drop('Match Score',axis=1)

    # Read in a file of addresses that need geocoding
    needs = pd.read_csv(NEEDS,converters=cv)

    # Merge the master df and needs df together with an outer merge; anything
    # missing coordinates needs geocoding
    merged = master.merge(needs,how='outer')
    leftovers = merged[pd.isnull(merged['Longitude'])]

    # Drop duplicates based on this subset of fields
    leftovers = leftovers.drop_duplicates(subset=['Address','City','State','Zip'])

    # Drop the lat & long columns and reset the index
    return leftovers.drop(['Longitude','Latitude'],axis=1).reset_index(drop=True)


if __name__ == '__main__':

    leftovers = still_needs()
    leftovers.to_csv(OUT,index=False)

import map2 as m2
import numpy as np
import pandas as pd


GEO1 = '../../../rcc-uchicago/PCNO/CSV/chicago/Geocoded Service Addresses/map2_geocoding_geocoded.csv'
GEO2 = '../../../rcc-uchicago/PCNO/CSV/chicago/Geocoded Service Addresses/map2_geocoding_version2_geocoded.csv'
NEEDS = '../../../rcc-uchicago/PCNO/CSV/chicago/map2_geocoding_version2.csv'
OUT = '../../../rcc-uchicago/PCNO/CSV/chicago/map2_geocoding_version3.csv'
#CODED = m2.read_geo()



def still_needs():
    '''
    '''

    cv = {'Zip':str}

    geo1 = pd.read_csv(GEO1,converters=cv)
    geo1 = geo1.rename(columns={'CSDS_Org_ID':'ID'},index=str)

    geo2 = pd.read_csv(GEO2,converters=cv)

    master = pd.concat([geo1,geo2])
    #master = master.rename(columns={'ID':'CSDS_Org_ID'},index=str)
    master = master.drop('Match Score',axis=1)

    print(list(master.columns))

    needs = pd.read_csv(NEEDS,converters=cv)
    #needs = needs.rename(columns={'ID':'CSDS_Org_ID'},index=str)

    print(list(needs.columns))

    merged = master.merge(needs,how='outer')
    leftovers = merged[pd.isnull(merged['Longitude'])]

    leftovers = leftovers.drop_duplicates(subset=['Address','City','State','Zip'])

    return leftovers.drop(['Longitude','Latitude'],axis=1).reset_index(drop=True)





if __name__ == '__main__':

    leftovers = still_needs()
    leftovers.to_csv(OUT,index=False)

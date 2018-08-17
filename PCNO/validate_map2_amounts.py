import pandas as pd


MAP2_SATELLITES = '../../../rcc-uchicago/PCNO/CSV/chicago/Maps/map2_satellites.csv'
MAP2_HQ = '../../../rcc-uchicago/PCNO/CSV/chicago/Maps/map2_hq.csv'
MAP2B_SATELLITES = '../../../rcc-uchicago/PCNO/CSV/chicago/Maps/map2b_satellites.csv'
MAP2B_HQ = '../../../rcc-uchicago/PCNO/CSV/chicago/Maps/map2b_hq.csv'


if __name__ == '__main__':

    hq = pd.read_csv(MAP2_HQ)
    hq_total = hq.Dollars_Per_Location.sum()

    sat = pd.read_csv(MAP2_SATELLITES)
    sat_total = sat.Dollars_Per_Location.sum()

    map2_total = hq_total + sat_total

    print('Map2 total:  ',map2_total)
    # $3810692646.12



    hqb = pd.read_csv(MAP2B_HQ)
    hqb_total = hqb.Dollars_Per_Contract_Per_Location.sum()

    satb = pd.read_csv(MAP2B_SATELLITES)
    satb_total = satb.Dollars_Per_Contract_Per_Location.sum()

    map2b_total = hqb_total + satb_total

    print('Map2b total: ',map2b_total)

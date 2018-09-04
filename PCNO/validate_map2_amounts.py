import pandas as pd


MAP2_SATELLITES = '../../../rcc-uchicago/PCNO/CSV/chicago/Maps/map2_satellites.csv'
MAP2_HQ = '../../../rcc-uchicago/PCNO/CSV/chicago/Maps/map2_hq.csv'
MAP2B_SATELLITES = '../../../rcc-uchicago/PCNO/CSV/chicago/Maps/map2b_satellites.csv'
MAP2B_HQ = '../../../rcc-uchicago/PCNO/CSV/chicago/Maps/map2b_hq.csv'


if __name__ == '__main__':

    # Define the target amount; format and print
    target = 3810692646.12
    print('Target:      {0:,.2f}'.format(target))

    # Read in the map 2 HQ file and take the total
    hq = pd.read_csv(MAP2_HQ)
    hq_total = hq.Dollars_Per_Location.sum()

    # Read in the map 2 satellite file and take the total
    sat = pd.read_csv(MAP2_SATELLITES)
    sat_total = sat.Dollars_Per_Location.sum()

    # Sum the map 2 HQ and satellite totals; format and print
    map2_total = hq_total + sat_total
    print('Map2 total:  {0:,.2f}'.format(map2_total))

    # Read in the map 2b HQ file and take the total
    hqb = pd.read_csv(MAP2B_HQ)
    hqb_total = hqb.Dollars_Per_Contract_Per_Location.sum()

    # Read in the map 2b satellite file and take the total
    satb = pd.read_csv(MAP2B_SATELLITES)
    satb_total = satb.Dollars_Per_Contract_Per_Location.sum()

    # Sum the map 2b HQ and satellite totals; format and print
    map2b_total = hqb_total + satb_total
    print('Map2b total: {0:,.2f}'.format(map2b_total))

import pandas as pd


MAP1 = '../../../rcc-uchicago/PCNO/CSV/chicago/Maps/map1.csv'
MAP1B = '../../../rcc-uchicago/PCNO/CSV/chicago/Maps/map1b.csv'
HQ = '../../../rcc-uchicago/PCNO/CSV/chicago/contracts_w_hq_addresses.csv'


if __name__ == '__main__':

    print('\nConsidering only the contracts with HQ addresses in IL:\n')

    map1 = pd.read_csv(MAP1)
    map1_total = map1.Summed_Amount.sum()
    print('Map 1 total:  {0:,.2f}'.format(map1_total))

    map1b_df = pd.read_csv(MAP1B)
    map1b_total = map1b_df.Amount.sum()
    print('Map 1b total: {0:,.2f}'.format(map1b_total))

    hq = pd.read_csv(HQ)
    hq = hq[hq['State'] == 'IL']
    hq_total = hq.Amount.sum()
    print('HQ total:     {0:,.2f}'.format(hq_total))

    print('\n_____________________________________________________________\n\n')

    print('Map 1 off by:  {0:,.2f}'.format((hq_total - map1_total)))
    print('Map 1b off by: {0:,.2f}'.format((hq_total - map1b_total)))

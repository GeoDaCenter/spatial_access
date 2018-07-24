import requests
import random
from p2p import TransitMatrix
import pandas as pd
import numpy as np
import sys

#need this because p2p and graphhopper use synonyms for 
#vehicle/route types
p2p_to_graphhopper_type_names = {
    'drive' : 'car',
    'walk' : 'foot',
    'bike' : 'bike'
}

def sample_one_matrix(df, tm, network_type, api_key):
    '''
    Test one distance matrix
    '''

    base_url = "https://graphhopper.com/api/1/matrix"
    first = True
    X_DATA_COL = df.columns.get_loc('x') + 1
    Y_DATA_COL = df.columns.get_loc('y') + 1

    for data in df.itertuples():
    
        x_data = data[X_DATA_COL]
        y_data = data[Y_DATA_COL]
    
        if first:
            point_string = "?point={},{}".format(x_data, y_data)
            first = False
        else:
            point_string = "&point={},{}".format(x_data, y_data)

        base_url += point_string

    param_string = "&type=json&vehicle={}&debug=true&out_array=times&key={}".format(network_type, api_key)
    base_url += param_string


    try:
        r = requests.get(base_url)

        results = r.json()['times']
    except:
        print('there was a problem fetching from GraphHopper. Exiting...')
        sys.exit()


    already_checked = set()
    diffs = []
    for i, row in enumerate(df.index):
        for j, col in enumerate(df.index):
            if (row, col) not in already_checked and row != col:
                calculated_time = tm.get(row, col)
                actual_time = results[i][j]
                diff = calculated_time - actual_time
                diffs.append(diff)
                already_checked.add((row, col))
                already_checked.add((col, row))

    stddev = np.std(diffs)
    mean = np.mean(diffs)


    print('diffs mean: {}, stddev: {}'.format(mean, stddev))


def calibrate(network_type='walk', input_file='resources/LEHD_blocks.csv', 
    sl_file='resources/condensed_street_data.csv', n=1):
    '''
    Show the mean and stddev of the difference between p2p's route time
    and GraphHopper's route time, in seconds.

    IMPORTANT: To use this, must have a valid GraphHopper Matrix API key
    saved in a text file in this directory called GRAPHHOPPER_API_KEY.txt

    Positive differences indicate p2p's route was longer, negative times indicates
    that p2p's route was shorter.
    '''
    if network_type == 'drive':
        assert sl_file is not None, 'must provide sl_file for use with driving network calibration'
    with open('GRAPHHOPPER_API_KEY.txt', 'r') as api_file:
        api_key = api_file.read()
        api_key = api_key.strip()
    gh_type_name = p2p_to_graphhopper_type_names[network_type]

    tm = TransitMatrix(network_type=network_type, primary_input=input_file)
    if network_type == 'drive':
        tm.process(speed_limit_filename=sl_file)
    else:
        tm.process()

    #extract the column names
    xcol = ''
    ycol = ''
    idx = ''

    df = pd.read_csv(input_file)

    #choose the largest possible sample size
    sample_size = min(24, len(df))

    print('The variables in your data set are:')
    df_cols = df.columns.values
    for var in df_cols:
        print('> ',var)
    while xcol not in df_cols:
        xcol = input('Enter the x coordinate (Latitude): ')
    while ycol not in df_cols:
        ycol = input('Enter the y coordinate (Longitude): ')
    while idx not in df_cols:
        idx = input('Enter the index name: ')

    df.rename(columns={xcol:'x',ycol:'y', idx:'idx'},inplace=True)
    df.set_index('idx', inplace=True)

    for i in range(n):

        sample_one_matrix(df.sample(sample_size), tm, gh_type_name, api_key)
    

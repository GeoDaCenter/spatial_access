from p2p import TransitMatrix
from ScoreModel import ModelData
from CommunityAnalytics import HSSAModel, PCSpendModel


#causes unknown exception on loading SP matrix
def run_scoremodel(network_type='drive'):
    model = ModelData(network_type)
    model.load_sources()
    model.load_dests()
    #model.load_sources_nn()
    model.load_sp_matrix()
    model.process()


    return model

def run_p2p(network_type='drive', primary_input='resources/chi_data.csv', 
         secondary_input=None, speed_limit_filename='resources/condensed_street_data.csv', 
         output_filename=None, epsilon=0.05, cleanup=True,
         debug=False, use_logging=True, output_type='csv', 
         n_best_matches=4, read_from_file=None):
    '''
    Main function of this program. Convert one or two .csv files with longitudes
    and latitudes to a matrix showing the network travel time between each point.
    '''

    data = TransitMatrix(network_type, epsilon, primary_input, secondary_input, 
        output_type=output_type, n_best_matches=n_best_matches, read_from_file=read_from_file)

    data.process(speed_limit_filename, output_filename, cleanup, debug)

    return data

def run_p2p_as_main(ays_argv):
    proper_usage = 'Usage: python3 main.py p2p -f data/primary_input_data.csv -f2 data/secondary_input.csv -m walk -o data/output_data.csv -sl speed_limit_data.csv -e 0.08'
    speed_limit_warning = 'WARNING: Unable to load speed limit input data. Preceding to use default values (Will result in lower accuracy for driving networks).'
    mode = None
    speed_limit_filename = None
    primary_input = None
    secondary_input = None
    output_filename = None
    epsilon = 0.05

    error = False

    want_help = 'Enter: "python3 main.py p2p help" for help'
    help_message = '''{}
    Arguments: 
        -f the primary file to compute travel times
        -f2 the secondary file to compute travel times if you need an assymetric matrix [optional]
        -m should be one of: (walk,drive). The type of transit network you want
        -o an output file [optional--if you don't specify, a filename will be generated]
        -sl a .csv containing data about speed limits in your area of interest [optional]
        -e controls how far beyond the last coordinate you want to go when grabbing the street network
            this is a good idea to prevent unreachable locations, but the bigger e is, the longer the 
            computation time [optional. default is 0.05]
    '''.format(proper_usage)

    for i, arg in enumerate(sys_argv):
        if arg == 'help':
            print(help_message)
            sys.exit()
        elif arg == '-m':
            mode = sys_argv[i + 1]
        elif arg == '-sl':
            speed_limit_filename = sys_argv[i + 1]
        elif arg == '-f':
            primary_input = sys_argv[i + 1]
        elif arg == '-f2':
            secondary_input = sys_argv[i + 1]
        elif arg == '-o':
            output_filename = sys_argv[i + 1]
        elif arg == '-e':
            epsilon = float(sys_argv[i + 1])
            if epsilon < 0:
                print("ERROR: Epsilon ({}) must be >= 0".format(epsilon))
            elif epsilon > 0.1:
                print("WARNING: Epsilon ({}) is very large and will result in increased computation times".format(epsilon))

    if mode not in ['drive', 'walk']:
        print('ERROR: Unknown mode of transit detected. Must be one of: "drive" or "walk"')
        error = True
    if not primary_input:
        print('ERROR: Must specify an input file')
        error = True
    if error:
        print(proper_usage)
        print(want_help)
        sys.exit()
    if speed_limit_filename:
        if os.path.isfile(speed_limit_filename):
            print('Found speed limit input data.')
        else:
            print(speed_limit_warning)
    else:
        if mode == 'drive':
            print(speed_limit_warning)
    if output_filename:
        if os.isfile(output_filename):
            print("ERROR: Ouput filename: ({}) already exists".format(output_filename))
            sys.exit()
    if mode == 'drive' and epsilon < 0.05:
        print("WARNING: An epsilon > 0.03 is preferable when using a driving network")

    run_p2p(mode, primary_input, secondary_input, speed_limit_filename, output_filename, epsilon)


if __name__ == '__main__':
    if sys.argv[3] == 'p2p':
        run_p2p_as_main(sys.argv)
    elif sys.argv[3] == 'ScoreModel':
        print('Import ModelData from ScoreModel to use')
        sys.exit()
    elif sys.argv[3] == 'CommunityAnalytics':
        print('Import HSSAModel or PCSpendModel from CommunityAnalytics to use')
        sys.exit()
    else:
        print('Unrecognized program. Exiting...')
        sys.exit()
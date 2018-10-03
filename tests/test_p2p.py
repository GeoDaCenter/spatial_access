from spatial_access.p2p import TransitMatrix

class TestClass(object):
    '''
    Suite of tests for p2p.
    '''

    def test_1(self):
        '''
        Tests that p2p can be imported and instantiated.
        '''
        hints = {'idx':'name', 'ycol':'y', 'xcol':'x'}
        transit_matrix_1 = TransitMatrix('walk', 
            primary_input='test_data/sources.csv',
            secondary_input='test_data/dests.csv',
            primary_hints=hints, secondary_hints=hints)

        assert(True)

    def test_2(self):
        '''
        Tests that p2p.load_inputs() does not cause failure and 
        produces the expected result.
        '''
        hints = {'idx':'name', 'ycol':'y', 'xcol':'x'}
        transit_matrix_1 = TransitMatrix('walk', 
            primary_input='test_data/sources.csv',
            secondary_input='test_data/dests.csv',
            primary_hints=hints, secondary_hints=hints)
        transit_matrix_1._load_inputs()

        try:
            assert(len(transit_matrix_1.primary_data) > 0 and len(transit_matrix_1.secondary_data) > 0)
        except:
            assert(False)

    def test_3(self):
        '''
        Tests that calling the network interface does not cause
        failure and produces the expected result
        '''
        hints = {'idx':'name', 'ycol':'y', 'xcol':'x'}
        transit_matrix_1 = TransitMatrix('walk', 
            primary_input='test_data/sources.csv',
            secondary_input='test_data/dests.csv',
            primary_hints=hints, secondary_hints=hints)
        transit_matrix_1._load_inputs()
        transit_matrix_1.nodes, transit_matrix_1.edges = transit_matrix_1._networkInterface.load_network(transit_matrix_1.primary_data, 
                                                                     transit_matrix_1.secondary_data, 
                                                                     transit_matrix_1.secondary_input,
                                                                     transit_matrix_1.epsilon)

        try:
            assert(len(transit_matrix_1.primary_data) > 0 and len(transit_matrix_1.secondary_data) > 0)
        except:
            assert(False)

    
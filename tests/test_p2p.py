# pylint: skip-file
from spatial_access.p2p import TransitMatrix

class TestClass():
    '''
    Suite of tests for p2p.
    '''

    def test_1(self):
        '''
        Tests that p2p can be imported and instantiated.
        '''
        hints = {'idx':'name', 'ycol':'y', 'xcol':'x'}
        transit_matrix_1 = TransitMatrix('walk', 
            primary_input='tests/test_data/sources.csv',
            secondary_input='tests/test_data/dests.csv',
            primary_hints=hints, secondary_hints=hints)

        assert True

    def test_2(self):
        '''
        Tests that p2p.load_inputs() does not cause failure and 
        produces the expected result.
        '''
        hints = {'idx':'name', 'ycol':'y', 'xcol':'x'}
        transit_matrix_1 = TransitMatrix('walk', 
            primary_input='tests/test_data/sources.csv',
            secondary_input='tests/test_data/dests.csv',
            primary_hints=hints, secondary_hints=hints)
        transit_matrix_1._load_inputs()

        try:
            assert len(transit_matrix_1.primary_data) > 0 and len(transit_matrix_1.secondary_data) > 0
        except:
            assert False

    def test_3(self):
        '''
        Tests that calling the network interface does not cause
        failure and produces the expected result
        '''
        hints = {'idx':'name', 'ycol':'y', 'xcol':'x'}
        transit_matrix_1 = TransitMatrix('walk', 
            primary_input='tests/test_data/sources.csv',
            secondary_input='tests/test_data/dests.csv',
            primary_hints=hints, secondary_hints=hints)
        transit_matrix_1._load_inputs()
        transit_matrix_1._networkInterface.load_network(transit_matrix_1.primary_data, 
                                                        transit_matrix_1.secondary_data, 
                                                        secondary_input=True,
                                                        epsilon=transit_matrix_1.epsilon)


        assert transit_matrix_1._networkInterface.number_of_nodes() > 0
        assert transit_matrix_1._networkInterface.number_of_edges() > 0

    # def test_4(self):
    #     '''
    #     Tests that calling the _parse_network method does not cause
    #     failure
    #     '''
    #     hints = {'idx':'name', 'ycol':'y', 'xcol':'x'}
    #     transit_matrix_1 = TransitMatrix('walk', 
    #         primary_input='tests/test_data/sources.csv',
    #         secondary_input='tests/test_data/dests.csv',
    #         primary_hints=hints, secondary_hints=hints)
    #     transit_matrix_1._load_inputs()
    #     transit_matrix_1._networkInterface.load_network(transit_matrix_1.primary_data, 
    #                                                     transit_matrix_1.secondary_data, 
    #                                                     secondary_input=True,
    #                                                     epsilon=transit_matrix_1.epsilon)

    #     transit_matrix_1._parse_network()

    #     assert True

    # def test_5(self):
    #     '''
    #     Tests that calling the _parse_network method does not cause
    #     failure
    #     '''
    #     hints = {'idx':'name', 'ycol':'y', 'xcol':'x'}
    #     transit_matrix_1 = TransitMatrix('walk', 
    #         primary_input='tests/test_data/sources.csv',
    #         secondary_input='tests/test_data/dests.csv',
    #         primary_hints=hints, secondary_hints=hints)
    #     transit_matrix_1.process()

    #     assert True

    # 
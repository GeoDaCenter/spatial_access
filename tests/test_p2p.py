# pylint: skip-file
from spatial_access.p2p import TransitMatrix

from spatial_access.SpatialAccessExceptions import PrimaryDataNotFoundException
from spatial_access.SpatialAccessExceptions import SecondaryDataNotFoundException
from spatial_access.SpatialAccessExceptions import UnableToParsePrimaryDataException
from spatial_access.SpatialAccessExceptions import UnableToParseSecondaryDataException
from spatial_access.SpatialAccessExceptions import UnknownModeException
from spatial_access.SpatialAccessExceptions import InsufficientDataException


class TestClass():
    """
    Suite of tests for p2p.
    """

    def test_1(self):
        """
        Tests that p2p can be imported and instantiated.
        """
        hints = {'idx':'name', 'lat':'y', 'lon':'x'}
        transit_matrix_1 = TransitMatrix('walk',
            primary_input='tests/test_data/sources.csv',
            secondary_input='tests/test_data/dests.csv',
            primary_hints=hints, secondary_hints=hints)

        assert True

    def test_2(self):
        """
        Tests that p2p.load_inputs() does not cause failure and
        produces the expected result.
        """
        hints = {'idx':'name', 'lat':'y', 'lon':'x'}
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
        """
        Tests that calling the network interface does not cause
        failure and produces the expected result
        """
        hints = {'idx':'name', 'lat':'y', 'lon':'x'}
        transit_matrix_1 = TransitMatrix('walk',
            primary_input='tests/test_data/sources.csv',
            secondary_input='tests/test_data/dests.csv',
            primary_hints=hints, secondary_hints=hints)
        transit_matrix_1._load_inputs()
        transit_matrix_1._network_interface.load_network(transit_matrix_1.primary_data,
                                                        transit_matrix_1.secondary_data,
                                                        secondary_input=True,
                                                        epsilon=transit_matrix_1.epsilon)


        assert transit_matrix_1._network_interface.number_of_nodes() > 0
        assert transit_matrix_1._network_interface.number_of_edges() > 0

    def test_4(self):
        """
        Tests that calling the _parse_network method does not cause
        failure
        """
        hints = {'idx':'name', 'lat':'y', 'lon':'x'}
        transit_matrix_1 = TransitMatrix('walk',
            primary_input='tests/test_data/sources.csv',
            secondary_input='tests/test_data/dests.csv',
            primary_hints=hints, secondary_hints=hints)
        transit_matrix_1._load_inputs()
        transit_matrix_1._network_interface.load_network(transit_matrix_1.primary_data,
                                                        transit_matrix_1.secondary_data,
                                                        secondary_input=True,
                                                        epsilon=transit_matrix_1.epsilon)
        transit_matrix_1._matrix_interface.prepare_matrix(transit_matrix_1._network_interface.number_of_nodes())
        transit_matrix_1._parse_network()

        assert True

    def test_5(self):
        """
        Tests the use_meters flag.
        """
        hints = {'idx':'name', 'lat':'y', 'lon':'x'}
        transit_matrix_1 = TransitMatrix('walk',
            primary_input='tests/test_data/sources.csv',
            secondary_input='tests/test_data/dests.csv',
            primary_hints=hints, secondary_hints=hints,
            use_meters=True)
        transit_matrix_1.process()

        assert True

    def test_6(self):
        """
        Tests bike network and write_csv.
        """
        hints = {'idx':'name', 'lat':'y', 'lon':'x'}
        transit_matrix_1 = TransitMatrix('bike',
            primary_input='tests/test_data/sources.csv',
            secondary_input='tests/test_data/dests.csv',
            primary_hints=hints, secondary_hints=hints)
        transit_matrix_1.process()

        assert True

    def test_7(self):
        """
        Tests symmetric bike network and write_tmx
        """
        hints = {'idx':'name', 'lat':'y', 'lon':'x'}
        transit_matrix_1 = TransitMatrix('bike',
            primary_input='tests/test_data/sources.csv',
            secondary_input='tests/test_data/sources.csv',
            primary_hints=hints, secondary_hints=hints)
        transit_matrix_1.process()

        assert True

    def test_8(self):
        """
        Tests string labels.
        """
        hints = {'idx':'name', 'lat':'y', 'lon':'x'}
        transit_matrix_1 = TransitMatrix('bike',
            primary_input='tests/test_data/sources.csv',
            secondary_input='tests/test_data/dests_a.csv',
            primary_hints=hints, secondary_hints=hints)
        transit_matrix_1.process()

        assert True

    def test_9(self):
        """
        Tests driving assymetric network.
        """
        hints = {'idx':'name', 'lat':'y', 'lon':'x'}
        transit_matrix_1 = TransitMatrix('drive',
            primary_input='tests/test_data/sources.csv',
            secondary_input='tests/test_data/dests_a.csv',
            primary_hints=hints, secondary_hints=hints)
        transit_matrix_1.process()

        assert True

    def test_10(self):
        """
        Tests driving symmetric network.
        """
        hints = {'idx':'name', 'lat':'y', 'lon':'x'}
        transit_matrix_1 = TransitMatrix('drive',
            primary_input='tests/test_data/sources.csv',
            secondary_input='tests/test_data/sources.csv',
            primary_hints=hints, secondary_hints=hints)
        transit_matrix_1.process()

        assert True


    def test_11(self):
        """
        Tests driving symmetric network.
        """
        hints = {'idx':'name', 'lat':'y', 'lon':'x'}
        transit_matrix_1 = TransitMatrix('drive',
            primary_input='tests/test_data/sources.csv',
            secondary_input='tests/test_data/sources.csv',
            primary_hints=hints, secondary_hints=hints)
        transit_matrix_1.prefetch_network()

        assert transit_matrix_1._network_interface.number_of_nodes() > 0
        assert transit_matrix_1._network_interface.number_of_edges() > 0

    def test_12(self):
        """
        Tests write_csv.
        """
        hints = {'idx':'name', 'lat':'y', 'lon':'x'}
        transit_matrix_1 = TransitMatrix('bike',
            primary_input='tests/test_data/sources.csv',
            secondary_input='tests/test_data/dests.csv',
            primary_hints=hints, secondary_hints=hints)
        transit_matrix_1.process()
        transit_matrix_1.write_csv('tests/test_12_file.csv')

        transit_matrix_2 = TransitMatrix('bike', read_from_file='tests/test_12_file.csv')

        assert True

    def test_13(self):
        """
        Tests write_tmx (asymmetric).
        """
        hints = {'idx':'name', 'lat':'y', 'lon':'x'}
        transit_matrix_1 = TransitMatrix('bike',
            primary_input='tests/test_data/sources.csv',
            secondary_input='tests/test_data/dests.csv',
            primary_hints=hints, secondary_hints=hints)
        transit_matrix_1.process()
        transit_matrix_1.write_tmx('tests/test_13_file')

        transit_matrix_2 = TransitMatrix('bike', read_from_file='tests/test_13_file')

        assert True

    def test_14(self):
        """
        Tests write_tmx (symmetric).
        """
        hints = {'idx':'name', 'lat':'y', 'lon':'x'}
        transit_matrix_1 = TransitMatrix('walk',
            primary_input='tests/test_data/sources.csv',
            secondary_input='tests/test_data/sources.csv',
            primary_hints=hints, secondary_hints=hints)
        transit_matrix_1.process()
        transit_matrix_1.write_tmx('tests/test_14_file')

        transit_matrix_2 = TransitMatrix('walk', read_from_file='tests/test_14_file')

        assert True

    def test_15(self):
        """
        Not specifying read_from_file throws InsufficientDataException
        """
        try:
            transit_matrix_1 = TransitMatrix('transit')
            assert False
        except InsufficientDataException:
            assert True



    def test_16(self):
        """
        Tests reading an OTP transit matrix.
        """
        transit_matrix_1 = TransitMatrix('transit', read_from_file='tests/test_data/sample_otp.csv')

        assert transit_matrix_1._matrix_interface.get(530330077002014, 530330077002014) == 0
        assert transit_matrix_1._matrix_interface.get(530330077002014, 530330247021004) == 114
        assert transit_matrix_1._matrix_interface.get(530330322102064, 530330222032019) == 65535

        assert True

    def test_17(self):
        """
        Tests PrimaryDataNotFoundException.
        """
        transit_matrix_1 = TransitMatrix('drive', primary_input="file_that_doesnt_exist.csv",
                                         primary_hints= {'idx':'name', 'lat':'y', 'lon':'x'})
        try:
            transit_matrix_1.process()
        except PrimaryDataNotFoundException:
            assert True
            return
        assert False


    def test_18(self):
        """
        Tests SecondaryDataNotFoundException.
        """
        transit_matrix_1 = TransitMatrix('drive', primary_input="tests/test_data/sources.csv",
                                         secondary_input="secondary_file_that_doesnt_exist.csv",
                                        primary_hints= {'idx':'name', 'lat':'y', 'lon':'x'},
                                        secondary_hints = {'idx':'name', 'lat':'y', 'lon':'x'})
        try:
            transit_matrix_1.process()
        except SecondaryDataNotFoundException:
            assert True
            return
        assert False

    def test_19(self):
        """
        Tests UnableToParsePrimaryDataException.
        """
        transit_matrix_1 = TransitMatrix('drive', primary_input="tests/test_data/sources.csv",
                                         primary_hints= {'idx':'wrong_column_name', 'lat':'y', 'lon':'x'})
        try:
            transit_matrix_1.process()
        except UnableToParsePrimaryDataException:
            assert True
            return
        assert False


    def test_20(self):
        """
        Tests UnableToParseSecondaryDataException.
        """
        transit_matrix_1 = TransitMatrix('drive', primary_input="tests/test_data/sources.csv",
                                         secondary_input="tests/test_data/dests.csv",
                                        primary_hints= {'idx':'name', 'lat':'y', 'lon':'x'},
                                        secondary_hints = {'idx':'wrong_column_name', 'lat':'y', 'lon':'x'})
        try:
            transit_matrix_1.process()
        except UnableToParseSecondaryDataException:
            assert True
            return
        assert False


    def test_21(self):
        """
        Tests UnknownModeException.
        """
        try:
            transit_matrix_1 = TransitMatrix('flying', primary_input="tests/test_data/sources.csv")
        except UnknownModeException:
            assert True
            return
        assert False



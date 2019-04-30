from spatial_access.p2p import TransitMatrix
from spatial_access.Configs import Configs

from spatial_access.SpatialAccessExceptions import PrimaryDataNotFoundException
from spatial_access.SpatialAccessExceptions import SecondaryDataNotFoundException
from spatial_access.SpatialAccessExceptions import UnableToParsePrimaryDataException
from spatial_access.SpatialAccessExceptions import UnableToParseSecondaryDataException
from spatial_access.SpatialAccessExceptions import UnknownModeException
from spatial_access.SpatialAccessExceptions import InsufficientDataException
from spatial_access.SpatialAccessExceptions import WriteTMXFailedException
from spatial_access.SpatialAccessExceptions import UnrecognizedFileTypeException
from spatial_access.SpatialAccessExceptions import ImproperIndecesTypeException

class TestClass:
    """
    Suite of tests for p2p.
    """

    def setup_class(self):
        import os
        self.datapath = 'test_p2p_temp/'
        if not os.path.exists(self.datapath):
            os.mkdir(self.datapath)

    def teardown_class(self):
        import os
        if os.path.exists(self.datapath):
            import shutil
            shutil.rmtree(self.datapath)

    def test_01(self):
        """
        Tests that p2p can be imported and instantiated.
        """
        hints = {'idx':'name', 'lat':'y', 'lon':'x'}
        transit_matrix_1 = TransitMatrix('walk',
            primary_input='tests/test_data/sources.csv',
            secondary_input='tests/test_data/dests.csv',
            primary_hints=hints, secondary_hints=hints)

        assert True

    def test_02(self):
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

    def test_03(self):
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
                                                         epsilon=transit_matrix_1.configs.epsilon)


        assert transit_matrix_1._network_interface.number_of_nodes() > 0
        assert transit_matrix_1._network_interface.number_of_edges() > 0

    def test_5(self):
        """
        Tests the use_meters flag.
        """
        hints = {'idx':'name', 'lat':'y', 'lon':'x'}
        custom_configs = Configs()
        custom_configs.use_meters = True
        transit_matrix_1 = TransitMatrix('walk',
            primary_input='tests/test_data/sources.csv',
            secondary_input='tests/test_data/dests.csv',
            primary_hints=hints, secondary_hints=hints,
            configs=custom_configs)
        transit_matrix_1.process()

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
        transit_matrix_1.write_csv(self.datapath + "test_6.csv")
        assert True

    def test_7(self):
        """
        Tests symmetric bike network and write_tmx
        """
        hints = {'idx':'name', 'lat':'y', 'lon':'x'}
        transit_matrix_1 = TransitMatrix('bike',
            primary_input='tests/test_data/sources.csv',
            primary_hints=hints, secondary_hints=hints)
        transit_matrix_1.process()
        filename = self.datapath + "test_7.tmx"
        transit_matrix_1.write_tmx(filename)
        transit_matrix_2 = TransitMatrix('walk',
                                         read_from_file=filename)

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
            primary_hints=hints)
        transit_matrix_1.prefetch_network()

        assert transit_matrix_1._network_interface.number_of_nodes() > 0
        assert transit_matrix_1._network_interface.number_of_edges() > 0

    def test_15(self):
        """
        Not specifying read_from_file throws InsufficientDataException
        """
        try:
            transit_matrix_1 = TransitMatrix('drive')
            assert False
        except InsufficientDataException:
            assert True

    def test_16(self):
        """
        Tests write_csv (symmetric).
        """
        hints = {'idx':'name', 'lat':'y', 'lon':'x'}
        transit_matrix_1 = TransitMatrix('walk',
            primary_input='tests/test_data/sources.csv',
            primary_hints=hints)
        transit_matrix_1.process()
        filename = self.datapath + 'test_16_file.csv'
        transit_matrix_1.write_csv(filename)

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


    def test_23(self):
        """
        Tests write_tmx.
        """
        hints = {'idx':'name', 'lat':'y', 'lon':'x'}
        transit_matrix_1 = TransitMatrix('bike',
            primary_input='tests/test_data/sources.csv',
            secondary_input='tests/test_data/dests.csv',
            primary_hints=hints, secondary_hints=hints)
        transit_matrix_1.process()
        filename = self.datapath + 'test_23_file.tmx'
        transit_matrix_1.write_tmx(filename)

        transit_matrix_2 = TransitMatrix('bike', read_from_file=filename)

        assert True

    def test_24(self):
        """
        Tests write_tmx (asymmetric).
        """
        hints = {'idx':'name', 'lat':'y', 'lon':'x'}
        transit_matrix_1 = TransitMatrix('bike',
            primary_input='tests/test_data/sources.csv',
            secondary_input='tests/test_data/dests.csv',
            primary_hints=hints, secondary_hints=hints)
        transit_matrix_1.process()
        filename = self.datapath + 'test_24_file.tmx'
        transit_matrix_1.write_tmx(filename)

        transit_matrix_2 = TransitMatrix('bike', read_from_file=filename)

        assert True

    def test_25(self):
        """
        Tests write file with bad filename (symmetric).
        """
        hints = {'idx':'name', 'lat':'y', 'lon':'x'}
        transit_matrix_1 = TransitMatrix('walk',
            primary_input='tests/test_data/sources.csv',
            primary_hints=hints)

        transit_matrix_1.process()
        bad_filename = self.datapath + 'test_25_file.ext'

        try:
            transit_matrix_1.write_tmx(bad_filename)
            assert False
        except WriteTMXFailedException:
            return

    def test_26(self):
        """
        Test read OTP csv.
        """
        transit_matrix = TransitMatrix('otp',
                                       primary_input='tests/test_data/sample_otp.csv')
        try:
            transit_matrix.process()
            assert False
        except AssertionError:
            return

    def test_27(self):
        """
        Test write_csv/read_file
        """
        hints = {'idx': 'name', 'lat': 'y', 'lon': 'x'}
        transit_matrix_1 = TransitMatrix('walk',
                                         primary_input='tests/test_data/sources.csv',
                                         primary_hints=hints)

        transit_matrix_1.process()
        transit_matrix_1.matrix_interface.print_data_frame()
        filename = self.datapath + 'test_27_file.csv'
        transit_matrix_1.write_csv(filename)

        transit_matrix_2 = TransitMatrix('walk', read_from_file=filename)
        transit_matrix_2.matrix_interface.print_data_frame()

    def test_28(self):
        """
        Test ImproperIndecesTypeException is raised
        when indeces are not strings or ints.
        """
        hints = {'idx': 'name', 'lat': 'y', 'lon': 'x'}
        transit_matrix_1 = TransitMatrix('walk',
                                         primary_input='tests/test_data/sources_bad_indeces_type.csv',
                                         primary_hints=hints)

        try:
            transit_matrix_1.process()
            assert False
        except ImproperIndecesTypeException:
            return

    def test_29(self):
        """
        Test UnexpectedFileFormatException is raised
        when file other than .csv or .tmx is given.
        """
        try:
            transit_matrix_1 = TransitMatrix('walk', read_from_file='tests/test_data/sources.tsv')
            assert False
        except UnrecognizedFileTypeException:
            return

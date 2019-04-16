from spatial_access.NetworkInterface import NetworkInterface
import pandas as pd
import pytest

from spatial_access.SpatialAccessExceptions import BoundingBoxTooLargeException


class TestClass:
    """
    Test suite for the Network Interface.
    """

    def setup_class(self):
        import os
        self.datapath = 'tests/test_network_interface_temp/'
        if not os.path.exists(self.datapath):
            os.mkdir(self.datapath)

    def teardown_class(self):
        import os
        if os.path.exists(self.datapath):
            import shutil
            shutil.rmtree(self.datapath)

    @pytest.mark.timeout(20)
    def test_1(self):
        walk_interface = NetworkInterface('walk')
        source_df = self.create_example_source_table()

        walk_interface.load_network(source_df, None, False, 0.005)

        try:
           assert walk_interface.nodes is not None and walk_interface.edges is not None 
           assert len(walk_interface.nodes) > 0 and len(walk_interface.edges) > 0
        except BaseException:
            assert False

    @pytest.mark.timeout(8)
    def test_2(self):
        walk_interface = NetworkInterface('bike')
        source_df = self.create_example_source_table()

        walk_interface.load_network(source_df, None, False, 0.005)

        try:
            assert walk_interface.nodes is not None and walk_interface.edges is not None
            assert len(walk_interface.nodes) > 0 and len(walk_interface.edges) > 0
        except BaseException:
            assert False

    @pytest.mark.timeout(20)
    def test_3(self):
        drive_interface = NetworkInterface('drive')
        source_df = self.create_example_source_table()
        dest_df = self.create_example_dest_table()

        drive_interface.load_network(source_df, dest_df, True, 0.005)

        try:
            assert drive_interface.nodes is not None and drive_interface.edges is not None
            assert len(drive_interface.nodes) > 0 and len(drive_interface.edges) > 0
        except BaseException:
            assert False

    def test_4(self):
        """
        Tests that we catch bounding boxes which are too
        large to handle.
        """
        drive_interface = NetworkInterface('drive')
        source_df = self.create_very_large_table()
        try:
            drive_interface.load_network(source_df, None, False, 0.005)
            assert False
        except BoundingBoxTooLargeException:
            assert True
        


    @staticmethod
    def create_example_source_table():
        data = {'name':['regenstein', 'booth', 'uchicago_medicine', 'smart_museum'],
                'lat': [41.791986, 41.789134, 41.788989, 41.793279],
                'lon': [-87.600212, -87.596212, -87.604949, -87.600277]}

        df = pd.DataFrame.from_dict(data)
        return df

    @staticmethod
    def create_example_dest_table():
        data = {'name':['medici', 'shfe', 'quad_club'],
                'lat': [41.791442, 41.789822, 41.791430],
                'lon': [-87.593769, -87.596445, -87.597717]}

        df = pd.DataFrame.from_dict(data)
        return df

    @staticmethod
    def create_very_large_table():
        data = {'name':['washington', 'florida'],
                'lat': [48.448324, 25.233228],
                'lon': [4.768930, -80.705327]}

        df = pd.DataFrame.from_dict(data)
        return df

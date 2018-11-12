# pylint: skip-file
from spatial_access.NetworkInterface import NetworkInterface
import pandas as pd
import pytest

class TestClass(object):
    '''
    Test suite for the Network Interface.
    '''

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
        '''
        Tests that we catch bounding boxes which are too
        large to handle.
        '''
        drive_interface = NetworkInterface('drive')
        source_df = self.create_very_large_table()
        try:
            drive_interface.load_network(source_df, None, False, 0.005)
            assert False
        except Exception:
            assert True
        


    @staticmethod
    def create_example_source_table():
        data = {'name':['regenstein', 'booth', 'uchicago_medicine', 'smart_museum'],
                'y': [41.791986, 41.789134, 41.788989, 41.793279],
                'x': [-87.600212, -87.596212, -87.604949, -87.600277]}

        df = pd.DataFrame.from_dict(data)
        return df

    @staticmethod
    def create_example_dest_table():
        data = {'name':['medici', 'shfe', 'quad_club'],
                'y': [41.791442, 41.789822, 41.791430],
                'x': [-87.593769, -87.596445, -87.597717]}

        df = pd.DataFrame.from_dict(data)
        return df

    @staticmethod
    def create_very_large_table():
        data = {'name':['washington', 'florida'],
                'y': [48.448324, 25.233228],
                'x': [-124.768930, -80.705327]}

        df = pd.DataFrame.from_dict(data)
        return df

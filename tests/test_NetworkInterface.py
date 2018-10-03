from spatial_access.NetworkInterface import NetworkInterface
import pandas as pd
import pytest

@pytest.mark.timeout(20)
def test_1():
    walk_interface = NetworkInterface('walk')
    source_df = create_example_source_table()

    nodes, edges = walk_interface.load_network(source_df, None, False, 0.005)

    try:
        assert len(nodes) > 0 and len(edges) > 0
    except BaseException:
        assert False

@pytest.mark.timeout(4)
def test_2():
    walk_interface = NetworkInterface('walk')
    source_df = create_example_source_table()

    nodes, edges = walk_interface.load_network(source_df, None, False, 0.005)

    try:
        assert len(nodes) > 0 and len(edges) > 0
    except BaseException:
        assert False

@pytest.mark.timeout(20)
def test_3():
    drive_interface = NetworkInterface('drive')
    source_df = create_example_source_table()
    dest_df = create_example_dest_table()

    nodes, edges = drive_interface.load_network(source_df, dest_df, True, 0.005)

    try:
        assert len(nodes) > 0 and len(edges) > 0
    except BaseException:
        assert False

def create_example_source_table():
    data = {'name':['regenstein', 'booth', 'uchicago_medicine', 'smart_museum'],
            'x': [41.791986, 41.789134, 41.788989, 41.793279],
            'y': [-87.600212, -87.596212, -87.604949, -87.600277]}

    df = pd.DataFrame.from_dict(data)
    return df

def create_example_dest_table():
    data = {'name':['medici', 'shfe', 'quad_club'],
            'x': [41.791442, 41.789822, 41.791430],
            'y': [-87.593769, -87.596445, -87.597717]}

    df = pd.DataFrame.from_dict(data)
    return df

import _p2pExtension


class TestClass:

    def test_1(self):
        edges = [(0, 1),
                 (1, 2),
                 (2, 3),
                 (3, 2),
                 (2, 6),
                 (1, 5),
                 (1, 4),
                 (4, 0),
                 (4, 5),
                 (4, 8),
                 (8, 0),
                 (4, 5),
                 (5, 6),
                 (6, 5),
                 (7, 6),
                 (7, 3)]

        nodes = [0, 1, 2, 3, 4, 5, 6, 7, 8]
        utility = _p2pExtension.pyNetworkUtility(edges, nodes)
        nodes_in_connected_component = utility.getConnectedNetworkNodes()
        assert nodes_in_connected_component == {0, 1, 4, 8}

    def test_2(self):
        edges = [(0, 1), (1, 2)]

        nodes = [0, 1, 2]
        try:
            utility = _p2pExtension.pyNetworkUtility(edges, nodes)
            nodes_in_connected_component = utility.getConnectedNetworkNodes()
            assert False
        except BaseException:
            return

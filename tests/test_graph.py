import os
import unittest
from openeo_pg_parser.translate import translate_process_graph


class GraphTester(unittest.TestCase):
    """  Tests all functionalities of the class `Graph`. """

    def setUp(self):
        """ Setting up variables for one test. """
        pg_dirpath = os.path.join(os.path.dirname(__file__), 'process_graphs')
        self.max_ndvi_pg_filepath =  os.path.join(pg_dirpath, "s2_max_ndvi.json")

    def test_sort_process_graph(self):
        """ Tests sorting of a process graph. """

        graph = translate_process_graph(self.max_ndvi_pg_filepath)
        assert list(graph.ids) == ["apply_0", "linear_scale_range_1", "load_collection_2", "reduce_bands_3", "red_4",
                                   "nir_5", "ndvi_6", "reduce_time_7", "max_8", "save_9"]

        sorted_graph = graph.sort(by='dependency')
        assert list(sorted_graph.ids) == ["load_collection_2", "reduce_bands_3", "red_4", "nir_5", "ndvi_6",
                                          "reduce_time_7", "max_8", "apply_0", "linear_scale_range_1", "save_9"]

    def test_get_parent_process(self):
        """ Tests to retrieve the parent process of an embedded process graph. """
        graph = translate_process_graph(self.max_ndvi_pg_filepath)
        lsr_node = graph['linear_scale_range_1']
        apply_node = graph['apply_0']

        assert lsr_node.parent_process == apply_node

    def test_is_reducer(self):
        """ Tests reducer identification. """
        graph = translate_process_graph(self.max_ndvi_pg_filepath)

        apply_node = graph['apply_0']
        assert not apply_node.is_reducer

        reduce_node = graph['reduce_time_7']
        assert reduce_node.is_reducer

    def test_get_dimension(self):
        """ Tests dimension retrieval. """
        graph = translate_process_graph(self.max_ndvi_pg_filepath)

        apply_node = graph['apply_0']
        assert apply_node.dimension is None

        reduce_node = graph['reduce_time_7']
        assert reduce_node.dimension == 't'

    def test_get_node_by_id(self):
        """ Tests node access in a graph by node id. """
        graph = translate_process_graph(self.max_ndvi_pg_filepath)

        apply_node = graph['apply_0']
        assert apply_node.id == 'apply_0'

    def test_get_node_by_name(self):
        """ Tests node access in a graph by node name. """
        graph = translate_process_graph(self.max_ndvi_pg_filepath)

        apply_node = graph['apply']
        assert apply_node.id == 'apply_0'

    def test_has_descendant_process(self):
        """ Tests if a node has a descendant process. """
        graph = translate_process_graph(self.max_ndvi_pg_filepath)

        dc_node = graph['load_collection_2']
        assert dc_node.has_descendant_process(graph, 'save_result')

    def test_to_igraph(self):
        """ Tests conversion of internal graph to an iGraph object. """
        graph = translate_process_graph(self.max_ndvi_pg_filepath)
        graph.to_igraph(edge_name="process")
        assert True


if __name__ == '__main__':
    unittest.main()
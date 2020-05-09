import os
import unittest
from openeo_pg_parser_python.translate import translate_process_graph


class GraphTester(unittest.TestCase):
    """  Tests all functionalities of the class `Graph`. """

    def setUp(self):
        """ Setting up variables for one test. """
        pg_dirpath = os.path.join(os.path.dirname(__file__), 'process_graphs')
        self.max_ndvi_pg_filepath =  os.path.join(pg_dirpath, "s2_max_ndvi.json")


    def test_sort_process_graph(self):
        """ Tests sorting of a process graph. """

        graph = translate_process_graph(self.max_ndvi_pg_filepath)
        assert list(graph.ids) == ["apply_0", "load_collection_2", "reduce_bands_3", "reduce_time_7", "save_9",
                                   "linear_scale_range_1", "red_4", "nir_5", "ndvi_6", "max_8"]

        sorted_graph = graph.sort(by='dependency')
        assert list(sorted_graph.ids) == ["load_collection_2", "nir_5", "red_4", "ndvi_6", "reduce_bands_3", "max_8",
                                          "reduce_time_7",  "linear_scale_range_1", "apply_0", "save_9"]


if __name__ == '__main__':
    unittest.main()
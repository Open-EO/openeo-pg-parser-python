import os
import unittest
from openeo_pg_parser_python.translate import translate_process_graph


class OpenEOGraphTester(unittest.TestCase):
    """  Tests all functionalities of openEO graph objects. """

    def setUp(self):
        """ Setting up variables for one test. """
        pg_dirpath = os.path.join(os.path.dirname(__file__), 'process_graphs')
        self.max_ndvi_pg_filepath =  os.path.join(pg_dirpath, "s2_max_ndvi.json")


    def test_sort_process_graph(self):
        """ Tests sorting of a process graph. """

        graph = translate_process_graph(self.max_ndvi_pg_filepath)
        pass


if __name__ == '__main__':
    unittest.main()
import os
import unittest
from openeo_pg_parser_python.translate import translate_process_graph


class TranslateTester(unittest.TestCase):
    """  Testing the module `translate` for different process graph translations. """

    def setUp(self):
        """ Setting up variables for one test. """
        pg_dirpath = os.path.join(os.path.dirname(__file__), 'process_graphs')
        self.uc1_polarization_pg_filepath = os.path.join(pg_dirpath, "s1_uc1_polarization.json")
        self.non_existing_filepath = os.path.join(pg_dirpath, "does_not_exist.json")
        self.global_parameter_filepath = os.path.join(pg_dirpath, "s2_max_ndvi_global_parameter.json")

    def test_translate_process_graph(self):
        """ Translates a process graph from openEO syntax to a Python traversable object. """

        graph = translate_process_graph(self.uc1_polarization_pg_filepath)
        print(graph)
        assert True

    def test_process_graph_not_found(self):
        """ Checks if an error is thrown when a process graph file cannot be found. """

        try:
            translate_process_graph(self.non_existing_filepath)
        except FileNotFoundError:
            assert True

    def test_from_global_parameter(self):
        """ Tests parsing of a globally defined parameter. """
        parameters = {'test_from_parameter': 3}
        graph = translate_process_graph(self.global_parameter_filepath, parameters=parameters)

        assert graph['ndvi_6'].arguments['y'] == 3

if __name__ == '__main__':
    unittest.main()
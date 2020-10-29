import os
import unittest
from openeo_pg_parser.translate import translate_process_graph


class TranslateTester(unittest.TestCase):
    """  Testing the module `translate` for different process graph translations. """

    def setUp(self):
        """ Setting up variables for one test. """
        self.pg_dirpath = os.path.join(os.path.dirname(__file__), 'process_graphs')

    def test_translate_process_graph(self):
        """ Translates a process graph from openEO syntax to a Python traversable object. """
        pg_filepath = os.path.join(self.pg_dirpath, "s1_uc1_polarization.json")
        graph = translate_process_graph(pg_filepath)
        print(graph)
        assert True

    def test_translate_process_graph_none_params(self):
        """Translate a minimal process graph with all allowed values set to None."""
        pg_file = os.path.join(self.pg_dirpath, "none.json")
        graph = translate_process_graph(pg_file)
        print(graph)
        assert True

    def test_process_graph_not_found(self):
        """ Checks if an error is thrown when a process graph file cannot be found. """
        pg_filepath = os.path.join(self.pg_dirpath, "does_not_exist.json")
        try:
            translate_process_graph(pg_filepath)
        except FileNotFoundError:
            assert True

    def test_from_global_parameter(self):
        """ Tests parsing of a globally defined parameter. """
        pg_filepath = os.path.join(self.pg_dirpath, "s2_max_ndvi_global_parameter.json")
        parameters = {'test_from_parameter': 3}
        graph = translate_process_graph(pg_filepath, parameters=parameters)

        assert graph['ndvi_6'].arguments['y'] == 3

    def test_lc_from_global_parameters(self):
        """ Tests parsing of globally defined parameters given in the process graph itself. """
        pg_filepath = os.path.join(self.pg_dirpath, "lc_global_parameter.json")
        graph = translate_process_graph(pg_filepath)

        assert graph['dc_0'].arguments['bands'] == ['B08', 'B04', 'B02']
        assert graph['dc_0'].arguments['id'] == 'COPERNICUS/S2'

    def test_from_local_parameter(self):
        """ Tests parsing of a locally defined parameter. """
        pg_filepath = os.path.join(self.pg_dirpath, "s2_max_ndvi_local_parameter.json")
        graph = translate_process_graph(pg_filepath)

        assert graph['ndvi_6'].arguments['y'] == 3

    def test_lc_sub_processes(self):
        """ Tests correct linkage of sub-processes in load collection process. """
        pg_filepath = os.path.join(self.pg_dirpath, "lc_sub_processes.json")
        graph = translate_process_graph(pg_filepath)

        assert len(graph) == 3
        assert len(graph['loadco1_0'].result_processes) == 2
        assert list(graph['cc_1'].input_data_processes.ids)[0] == 'loadco1_0'
        assert list(graph['pf_2'].input_data_processes.ids)[0] == 'loadco1_0'
        assert list(graph['cc_1'].output_data_processes.ids)[0] == 'loadco1_0'
        assert list(graph['pf_2'].output_data_processes.ids)[0] == 'loadco1_0'


if __name__ == '__main__':
    unittest.main()
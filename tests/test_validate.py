import os
import unittest
from openeo_pg_parser.validate import validate_process_graph


class ValidateTester(unittest.TestCase):
    """  Testing the module `validate` for different process graph translations and validations. """

    def setUp(self):
        """ Setting up variables for one test. """
        self.pg_dirpath = os.path.join(os.path.dirname(__file__), 'process_graphs')

    def test_validate_process_graph_local(self):
        """ Validate a process graph using processes defined on a backend. """

        collections_url = "https://earthengine.openeo.org/v1.0/collections"
        pg_filepath = os.path.join(self.pg_dirpath, "s2_max_ndvi.json")

        valid, _ = validate_process_graph(pg_filepath, collections_url)

        assert valid

    def test_validate_process_graph_remote(self):
        """ Validate a process graph using remote specified processes and collections. """
        pg_filepath = os.path.join(self.pg_dirpath, "s2_max_ndvi.json")
        valid, _ = validate_process_graph(pg_filepath, "https://earthengine.openeo.org/v1.0/collections",
                                          processes_src="https://openeo.vito.be/openeo/1.0/processes")
        assert valid

    def test_validate_wrong_band(self):
        """ Validate a process graph using remote specified processes and collections. """

        pg_filepath = os.path.join(self.pg_dirpath, "s2_wrong_band.json")
        valid, _ = validate_process_graph(pg_filepath, "https://earthengine.openeo.org/v1.0/collections",
                                          processes_src="https://openeo.vito.be/openeo/1.0/processes")

        assert not valid

    def test_validate_missing_bands(self):
        """ Validate a process graph, which does not have any bands information stored. """

        pg_filepath = os.path.join(self.pg_dirpath, "s2_missing_bands.json")
        valid, _ = validate_process_graph(pg_filepath, "https://earthengine.openeo.org/v1.0/collections",
                                          processes_src="https://openeo.vito.be/openeo/1.0/processes")

        assert valid


if __name__ == '__main__':
    unittest.main()

import os
import unittest
from openeo_pg_parser.validate import validate_process_graph


class ValidateTester(unittest.TestCase):
    """  Testing the module `validate` for different process graph translations and validations. """

    def setUp(self):
        """ Setting up variables for one test. """
        pg_dirpath = os.path.join(os.path.dirname(__file__), 'process_graphs')
        self.wrong_band_filepath = os.path.join(pg_dirpath, "test_s2_wrong_band.json")
        self.max_ndvi_pg_filepath = os.path.join(pg_dirpath, "s2_max_ndvi.json")

    def test_validate_process_graph_local(self):
        """ Validate a process graph using processes defined on a backend. """

        collections_url = "https://earthengine.openeo.org/v1.0/collections"

        _, valid = validate_process_graph(self.max_ndvi_pg_filepath, collections_url)
        assert valid

    def test_validate_process_graph_remote(self):
        """ Validate a process graph using remote specified processes and collections. """
        # TODO: vito processes are taken at the moment for validation, change this in the future to GEE
        _, valid = validate_process_graph(self.max_ndvi_pg_filepath, "https://earthengine.openeo.org/v1.0/collections",
                                          processes_src="https://openeo.vito.be/openeo/1.0/processes")
        assert valid

    def test_validate_wrong_band(self):
        """ Validate a process graph using remote specified processes and collections. """
        # TODO: vito processes are taken at the moment for validation, change this in the future to GEE
        _, valid = validate_process_graph(self.wrong_band_filepath, "https://earthengine.openeo.org/v1.0/collections",
                                          processes_src="https://openeo.vito.be/openeo/1.0/processes")

        assert not valid


if __name__ == '__main__':
    unittest.main()

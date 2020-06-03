import os
import unittest
import warnings
from json import load
from openeo_pg_parser_python.validate import validate_process_graph


class ValidateTester(unittest.TestCase):
    """  Testing the module `validate` for different process graph translations and validations. """

    def setUp(self):
        """ Setting up variables for one test. """
        pg_dirpath = os.path.join(os.path.dirname(__file__), 'process_graphs')
        self.wrong_band_filepath = os.path.join(pg_dirpath, "test_s2_wrong_band.json")
        self.max_ndvi_pg_filepath = os.path.join(pg_dirpath, "s2_max_ndvi.json")


    def test_validate_process_graph_local(self):
        """ Validate a process graph using processes defined on a backend. """

        warnings.filterwarnings("ignore")  # suppress warnings caused by validation

        collections_url = "https://earthengine.openeo.org/v1.0/collections"

        valid = validate_process_graph(self.max_ndvi_pg_filepath, collections_url)
        assert not valid  # not valid because not all processes and collections are available


    def test_validate_process_graph_remote(self):
        """ Validate a process graph using remote specified processes and collections. """

        valid = validate_process_graph(self.max_ndvi_pg_filepath,
                                       processes_src="https://earthengine.openeo.org/v1.0/processes",
                                       collections_src="https://earthengine.openeo.org/v1.0/collections")

        assert valid


    def test_validate_wrong_band(self):
        """ Validate a process graph using remote specified processes and collections. """

        warnings.filterwarnings("ignore")  # suppress warnings caused by validation

        valid = validate_process_graph(self.wrong_band_filepath,
                                       processes_src="https://earthengine.openeo.org/v1.0/processes",
                                       collections_src="https://earthengine.openeo.org/v1.0/collections")

        assert valid  # TODO: should be not valid: no band information at the GEE backend?

if __name__ == '__main__':
    unittest.main()

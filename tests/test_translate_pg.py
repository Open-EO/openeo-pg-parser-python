import unittest
from openeo_pg_parser_python.translate_process_graph import translate_graph


class PGTranslateTester(unittest.TestCase):
    """ Responsible for testing the translation of an openEO process graph. """

    def setUp(self):
        """ Specifies paths to the test data. """

        self.pg_test_1_filepath = r"process_graphs/test_1.json"

    def test_pg_not_found(self):
        pg_filepath = r"process_graphs/does_not_exist.json"
        try:
            translate_graph(pg_filepath)
        except FileNotFoundError:
            assert True

if __name__ == '__main__':
    unittest.main()
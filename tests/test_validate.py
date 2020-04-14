import os
import unittest
from json import load
from openeo_pg_parser_python.validate import validate_graph

from tests import PG_FOLDER, LOCAL_PROCESSES_FOLDER


def test_validate_process_graph_local():
    """ Validate a process graph using processes defined on a backend. """

    # Validate input file
    validate_graph(os.path.join(PG_FOLDER, "use_case_1.json"), processes_dirpath=LOCAL_PROCESSES_FOLDER)
    # Validate input dictionary
    validate_graph(load(open(os.path.join(PG_FOLDER, "use_case_1.json"))), processes_dirpath=LOCAL_PROCESSES_FOLDER)


def test_validate_process_graph_remote():
    """ Validate a process graph using locally specified processes. """

    validate_graph(os.path.join(PG_FOLDER, "test_1.json"),
                   processes_url="http://openeo.vgt.vito.be/openeo/0.4.0/processes")

if __name__ == '__main__':
    unittest.main()
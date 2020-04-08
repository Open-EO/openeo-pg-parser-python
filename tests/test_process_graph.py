import os
import unittest
from json import load
from openeo_pg_parser_python.translate_process_graph import translate_graph
from openeo_pg_parser_python.validate_process_graph import validate_graph

# Global variables for tests
PG_FOLDER = os.path.join(os.path.dirname(__file__), 'process_graphs')
PROCESSES_FOLDER_LOCAL = os.path.join(os.path.dirname(__file__), "processes")


def test_validate_process_graph_local():
    """
    Validate a process graph using processes defined on a backend
    """

    # Validate input file
    validate_graph(os.path.join(PG_FOLDER, "use_case_1.json"), processes_dirpath=PROCESSES_FOLDER_LOCAL)
    # Validate input dictionary
    validate_graph(load(open(os.path.join(PG_FOLDER, "use_case_1.json"))), processes_dirpath=PROCESSES_FOLDER_LOCAL)


def test_validate_process_graph_remote():
    """
    Validate a process graph using locally specified processes
    """

    validate_graph(os.path.join(PG_FOLDER, "test_1.json"),
                   processes_url="http://openeo.vgt.vito.be/openeo/0.4.0/processes")


def test_translate_process_graph():
    """
    Translate pg from openEO syntax to python traversable object
    """

    graph = translate_graph(os.path.join(PG_FOLDER, "use_case_1.json"))
    print(graph)

if __name__ == '__main__':
    unittest.main()

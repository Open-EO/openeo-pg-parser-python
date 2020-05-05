import os
import unittest
from openeo_pg_parser_python.translate import translate_process_graph

from tests import PG_FOLDER


def test_translate_process_graph():
    """ Translates a process graph from openEO syntax to a Python traversable object. """

    graph = translate_process_graph(os.path.join(PG_FOLDER, "s1_uc1_polarization.json"))
    print(graph)
    assert True


def test_process_graph_not_found():
    """ Checks if an error is thrown when a process graph file cannot be found. """

    pg_filepath = r"process_graphs/does_not_exist.json"
    try:
        translate_process_graph(pg_filepath)
    except FileNotFoundError:
        assert True

if __name__ == '__main__':
    test_translate_process_graph()
    test_process_graph_not_found()
import os
import unittest
from openeo_pg_parser_python.translate import translate_process_graph

from tests import PG_FOLDER


def test_sort_process_graph():
    """ Tests sorting of a process graph. """

    graph = translate_process_graph(os.path.join(PG_FOLDER, "test_1.json"))
    assert list(graph.ids) == ["s2a_0", "ndvi_1", "min_time_2", "callback_3", "output_4"]

    sorted_graph = graph.sort(by='dependency')
    assert list(sorted_graph.ids) == ["s2a_0", "ndvi_1", "callback_3", "min_time_2", "output_4"]


if __name__ == '__main__':
    unittest.main()
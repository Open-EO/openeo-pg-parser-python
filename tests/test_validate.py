import os
import unittest
import warnings
from json import load
from openeo_pg_parser_python.validate import validate_process_graph

from tests import PG_FOLDER, LOCAL_PROCESSES_FOLDER


# TODO: Fix local process definitions first
# def test_validate_process_graph_local():
#     """ Validate a process graph using processes defined on a backend. """
#
#     warnings.filterwarnings("ignore")  # suppress warnings caused by validation
#
#     collections_url = "https://earthengine.openeo.org/v1.0/collections"
#
#     # Validate input file
#     valid = validate_process_graph(os.path.join(PG_FOLDER, "s2_max_ndvi.json"),
#                                    processes_src=LOCAL_PROCESSES_FOLDER,
#                                    collections_src=collections_url)
#     assert not valid  # not valid because not all processes and collections are available
#
#     # Validate input dictionary
#     valid = validate_process_graph(load(open(os.path.join(PG_FOLDER, "s2_max_ndvi.json"))),
#                                    processes_src=LOCAL_PROCESSES_FOLDER,
#                                    collections_src=collections_url)
#     assert not valid  # not valid because not all processes and collections are available


def test_validate_process_graph_remote():
    """ Validate a process graph using remote specified processes and collections. """

    valid = validate_process_graph(os.path.join(PG_FOLDER, "s2_max_ndvi.json"),
                                   processes_src="https://earthengine.openeo.org/v1.0/processes",
                                   collections_src="https://earthengine.openeo.org/v1.0/collections")

    assert valid


def test_validate_wrong_band():
    """ Validate a process graph using remote specified processes and collections. """

    warnings.filterwarnings("ignore")  # suppress warnings caused by validation

    valid = validate_process_graph(os.path.join(PG_FOLDER, "test_s2_wrong_band.json"),
                                   processes_src="https://earthengine.openeo.org/v1.0/processes",
                                   collections_src="https://earthengine.openeo.org/v1.0/collections")

    assert valid  # TODO: should be not valid: no band information at the GEE backend?

if __name__ == '__main__':
    test_validate_process_graph_remote()
    test_validate_wrong_band()

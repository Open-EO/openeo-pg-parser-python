import os
from openeo_pg_parser.translate import translate_process_graph
from openeo_pg_parser.utils import load_processes
from openeo_pg_parser.utils import load_collections


def validate_processes(process_graph, processes_src):
    """
    Validate the input process graph according to the given list of processes.

    Parameters
    ----------
    process_graph : graph.Graph
        Traversable Python process graph.
    processes_src : dict or str or list
        It can be:
            - dictionary of loaded process definitions (keys are the process ID's)
            - directory path to processes (.json)
            - URL of the remote process endpoint (e.g., "https://earthengine.openeo.org/v1.0/processes")
            - list of loaded process definitions

    Returns
    -------
    valid : bool
        If True, the given process graph is valid with respect to the given process definitions.
    err_msgs : list
        List of strings containing error or user information messages if `valid` is False.

    """

    process_defs = load_processes(processes_src)

    err_msgs = []
    for node in process_graph.nodes:
        if node.process_id not in process_defs.keys():
            err_msg = "'{}' is not in the current set of process definitions.".format(node.process_id)
            err_msgs.append(err_msg)
        else:
            # First, check if required parameter is set in the process graph
            for parameter in node.process.parameters.values():
                if not parameter.is_required:
                    if parameter.name not in node.arguments.keys():
                        err_msg = "Parameter '{}' is required for process '{}'".format(parameter.name,
                                                                                       node.process_id)
                        err_msgs.append(err_msg)

    valid = len(err_msgs) == 0
    return valid, err_msgs


def validate_collections(process_graph, collections_src):
    """
    Validate the input process graph according to the given list of processes.

    Parameters
    ----------
    process_graph : graph.Graph
        Traversable Python process graph.
    collections_src : dict or str or list, optional
        It can be:
            - dictionary of loaded collection definitions (keys are the collection ID's)
            - directory path to collections (.json)
            - URL of the remote collection endpoint (e.g., "https://earthengine.openeo.org/v1.0/collections")
            - list of loaded collection definitions

    Returns
    -------
    valid : bool
        If True, the given process graph is valid with respect to the given collection definitions.
    err_msgs : list
        List of strings containing error or user information messages if `valid` is False.

    """

    err_msgs = []
    for node in process_graph.nodes:
        if node.process_id == 'load_collection':
            collection_id = node.arguments['id']
            collection_defs = load_collections(collections_src, collection_ids=[collection_id])
            if node.arguments['id'] not in collection_defs.keys():
                err_msg = "'{}' is not in the current set of collections.".format(collection_id)
                err_msgs.append(err_msg)
            else:
                collection = collection_defs[collection_id]
                collection_dims = collection['cube:dimensions']
                available_bands = []
                for _, collection_dim in collection_dims.items():
                    if collection_dim['type'] == 'bands':
                        available_bands.extend([band.lower() for band in collection_dim['values']])

                # check bands
                if node.arguments.get('bands') is not None and available_bands:
                    node_bands = [band.lower() for band in node.arguments['bands']]
                    for node_band in node_bands:
                        if node_band not in available_bands:
                            available_bands_str = ', '.join(["'{}'".format(available_band)
                                                             for available_band in available_bands])
                            err_msg = "'{}' is not a valid band name for collection '{}' " \
                                      "with the following bands: {}.".format(node_band,
                                                                             collection_id,
                                                                             available_bands_str)
                            err_msgs.append(err_msg)

    valid = len(err_msgs) == 0
    return valid, err_msgs


def validate_process_graph(pg_filepath, collections_src, processes_src=None, parameters=None):
    """
    Validate the input process graph with respect to:
        - processes
        - collections
        - node names

    Parameters
    ----------
    pg_filepath : str or dict
        File path to process graph (json file) or parsed file as a dictionary.
    collections_src : dict or str or list
        It can be:
            - dictionary of loaded collection definitions (keys are the collection ID's)
            - directory path to collections (.json)
            - URL of the remote collection endpoint (e.g., "https://earthengine.openeo.org/v1.0/collections")
            - list of loaded collection definitions
    processes_src : dict or str or list, optional
        It can be:
            - dictionary of loaded process definitions (keys are the process ID's)
            - directory path to processes (.json)
            - URL of the remote process endpoint (e.g., "https://earthengine.openeo.org/v1.0/processes")
            - list of loaded process definitions
        The default value points to the "processes" repository of the parser.
    parameters : dict, optional
        Globally defined parameters, which can be used in 'from_parameter'.

    Returns
    -------
    valid : bool
        If True, the given process graph is valid.
    err_msgs : list
        List of strings containing error or user information messages if `valid` is False.

    """
    # define source of process definitions
    process_defs = os.path.join(os.path.dirname(__file__), "processes") \
        if processes_src is None else processes_src

    process_graph = translate_process_graph(pg_filepath, process_defs=process_defs, parameters=parameters)

    proc_valid, proc_err_msgs = validate_processes(process_graph, process_defs)
    coll_valid, coll_err_msgs = validate_collections(process_graph, collections_src)

    pg_err_msgs = proc_err_msgs + coll_err_msgs
    pg_valid = proc_valid & coll_valid

    return pg_valid, pg_err_msgs


if __name__ == '__main__':
    pass

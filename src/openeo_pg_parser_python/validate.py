import warnings
from openeo_pg_parser_python.translate import translate_process_graph
from openeo_pg_parser_python.utils import load_processes
from openeo_pg_parser_python.utils import load_collections


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

    """

    process_defs = load_processes(processes_src)

    valid = True
    for node in process_graph.nodes:
        if node.content['process_id'] not in process_defs.keys():
            valid = False
            wrn_msg = "'{}' is not in the current set of process definitions.".format(node.content['process_id'])
            warnings.warn(wrn_msg)
        else:
            process_def = process_defs[node.content['process_id']]
            # check all parameters
            # NB key 'parameters' is used in the processes' definition
            # NB key 'arguments' is used in the process graph
            for parameter_def in process_def['parameters']:
                if 'required' in parameter_def:
                    if parameter_def['name'] not in node.content['arguments'].keys():
                        valid = False
                        wrn_msg = "Parameter '{}' is required for process '{}'".format(parameter_def['name'],
                                                                                       node.content['process_id'])
                        warnings.warn(wrn_msg)

    return valid

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
        If True, the given process graph is valid with respect to the given process definitions.
    """

    collection_defs  = load_collections(collections_src)

    valid = True
    for node in process_graph.nodes:
        if node.content['process_id'] == 'load_collection':
            if node.content['arguments']['id'] not in collection_defs.keys():
                valid = False
                wrn_msg = "'{}' is not in the current set of collections.".format(node.content['arguments']['id'])
                warnings.warn(wrn_msg)
            else:
                collection = collection_defs[node.content['arguments']['id']]
                # check bands
                if 'bands' in node.content['arguments'] and 'bands' in collection:
                    node_bands = [band.lower() for band in node.content['arguments']['bands']]
                    available_bands = [band_properties['name'].lower() for band_properties in collection['bands']
                                       if 'name' in band_properties]
                    for node_band in node_bands:
                        if node_band not in available_bands:
                            valid = False
                            available_bands_str = ', '.join(["'{}'".format(available_band)
                                                             for available_band in available_bands])
                            wrn_msg = "'{}' is not a valid band name for collection '{}' " \
                                      "with the following bands: {}.".format(node_band,
                                                                             collection['id'],
                                                                             available_bands_str)
                            warnings.warn(wrn_msg)

    return valid

def validate_process_graph(pg_filepath, processes_src, collections_src):
    """
    Validate the input process graph according to the given list of processes.

    Parameters
    ----------
    pg_filepath : str or dict
        Filepath to process graph (json file) or parsed file as a dictionary.
    processes_src : dict or str or list
        It can be:
            - dictionary of loaded process definitions (keys are the process ID's)
            - directory path to processes (.json)
            - URL of the remote process endpoint (e.g., "https://earthengine.openeo.org/v1.0/processes")
            - list of loaded process definitions
    collections_src : dict or str or list, optional
        It can be:
            - dictionary of loaded collection definitions (keys are the collection ID's)
            - directory path to collections (.json)
            - URL of the remote collection endpoint (e.g., "https://earthengine.openeo.org/v1.0/collections")
            - list of loaded collection definitions

    Returns
    -------
    valid : bool
        If True, the given process graph is valid with respect to the given process definitions.
    """

    process_graph = translate_process_graph(pg_filepath)

    processes_valid = validate_processes(process_graph, processes_src)
    collections_valid = validate_collections(process_graph, collections_src)

    process_graph_valid = processes_valid & collections_valid

    return process_graph_valid

if __name__ == '__main__':
    pass

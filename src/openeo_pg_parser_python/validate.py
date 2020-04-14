import re
import os
import requests
from json import load
from openeo_pg_parser_python.translate import translate_process_graph


def list_to_dict(processes_list):
    """
    Convert a list of processes (dict objects) to a dict of dicts.

    Parameters
    ----------
    processes_list : list of dicts
        List of process dictionaries (i.e., openEO processes)

    Returns
    -------
    process_defs : dict
    """

    process_defs = dict()
    for process in processes_list:
        process_defs[process['id']] = process

    return process_defs

def load_local_processes(dirpath):
    """
    Collects process definitions (JSON files) from a local process directory.

    Parameters
    ----------
    dirpath : str
        Directory path of the process files (.json) folder.

    Returns
    -------
    list
        List of processes decoded as dictionaries.
    """

    pattern = re.compile(".*.json$")
    filenames = [filename for filename in os.listdir(dirpath) if re.match(pattern, filename)]
    filepaths = [os.path.join(dirpath, filename) for filename in filenames]
    processes_list = []
    for filepath in filepaths:
        processes_list.append(load(open(filepath)))

    return processes_list

def load_processes(processes_url=None, processes_dirpath=None):
    """
    Collects process definitions (JSON files) from a local or remote process directory.

    Parameters
    ----------
    processes_url : str, optional
        URL of the remote process endpoint (e.g., "http://openeo.vgt.vito.be/openeo/0.4.0/processes").
    processes_dirpath : str, optional
        Directory path of the process files (.json) folder.

    Notes
    -----
    Either `processes_url` or `processes_dirpath` needs to be given.
    """

    if processes_url:
        r = requests.get(url=processes_url)
        data = r.json()
        processes_list = data['processes']
    elif processes_dirpath:
        processes_list = load_local_processes(processes_dirpath)
    else:
        err_msg = "Either a processes URL or a local directory path must be specified."
        raise ValueError(err_msg)

    return processes_list


def validate_graph(pg_filepath, processes_url=None, processes_dirpath=None):
    """
    Validate the input process graph according to the given list of processes.

    Parameters
    ----------
    pg_filepath : str,
        filepath to process graph (json file)
    processes_url : str, optional
        URL of the remote process endpoint (e.g., "http://openeo.vgt.vito.be/openeo/0.4.0/processes").
    processes_dirpath : str, optional
        Directory path of the process files (.json) folder.

    Returns
    -------
    valid : bool
        If True, the given process graph is valid with respect to the given process definitions.
    """

    process_graph = translate_process_graph(pg_filepath)

    processes_list = load_processes(processes_url=processes_url, processes_dirpath=processes_dirpath)
    process_defs = list_to_dict(processes_list)

    valid = False
    for node in process_graph.nodes.values():
        node_content = node.content
        if node_content['process_id'] in process_defs.keys():
            process_def = process_defs[node_content['process_id']]
            # check all parameters
            # NB key 'parameters' is used in the processes' definition
            # NB key 'arguments' is used in the process graph
            for parameter_def in process_def['parameters']:
                if 'required' in process_def['parameters'][parameter_def]:
                    if parameter_def not in node_content['arguments'].keys():
                        err_msg = "Parameter '{}' is required for process '{}'".format(parameter_def['name'],
                                                                                       node_content['process_id'])
                        raise Exception(err_msg)
            valid = True
        else:
            err_msg = "'{}' is not in the current set of process definitions.".format(node_content['process_id'])
            raise Exception(err_msg)

    return valid

if __name__ == '__main__':
    pass

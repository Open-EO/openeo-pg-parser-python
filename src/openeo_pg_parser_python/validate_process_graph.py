import re
import os
import requests
from json import load
from openeo_pg_parser_python.translate_process_graph import translate_graph


def list_to_dict(processes_list):
    """
    Convert a list of processes (dict objects) to a dict of dicts.

    Parameters
    ----------
    processes_list: list of dictionaries (openEO processes)

    Returns:
    --------
    process_defs: dictionary
    """

    process_defs = dict()
    for process in processes_list:
        process_defs[process['id']] = process

    return process_defs

def load_local_processes(dirpath):
    """

    """
    pattern = re.compile(".*.json$")
    filenames = [filename for filename in os.listdir(dirpath) if re.match(pattern, filename)]
    filepaths = [os.path.join(dirpath, filename) for filename in filenames]
    processes_list = []
    for filepath in filepaths:
        processes_list.append(load(open(filepath)))

    return processes_list

def load_processes(processes_url=None, processes_dirpath=None):

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
    pg_filepath: str, filepath to process graph (json file)
    processes_list: list of processes (as dict), e.g. get request on openeo.backend_url.com/processes

    Returns:
    --------
    validated: boolean (or raises error)
    """

    graph = translate_graph(pg_filepath)

    processes_list = load_processes(processes_url=processes_url, processes_dirpath=processes_dirpath)
    process_defs = list_to_dict(processes_list)

    validated = False
    for node in graph.nodes.values():
        pg = node.graph
        if pg['process_id'] in process_defs.keys():
            process_def = process_defs[pg['process_id']]
            # check all parameters
            # NB key 'parameters' is used in the processes' definition
            # NB key 'arguments' is used in the process graph
            for parameter_def in process_def['parameters']:
                if 'required' in process_def['parameters'][parameter_def]:
                    if parameter_def not in pg['arguments'].keys():
                        raise Exception("Parameter '{}' is required for process '{}'".format(parameter_def['name'],
                                                                                                  pg['process_id']))
            validated = True
        else:
            raise Exception("'{}' is not in the current set of process definitions.".format(pg['process_id']))

    return validated

if __name__ == '__main__':
    pass

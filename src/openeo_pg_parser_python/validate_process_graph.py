from openeo_pg_parser_python.translate_process_graph import translate_graph


def check_result_nodes(graph):
    pass


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


def validate_graph(pg_filepath, processes_list):
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
    process_defs = list_to_dict(processes_list)

    for node in graph.nodes.values():
        pg = node.graph
        if pg['process_id'] in process_defs.keys():
            process_def = process_defs[pg['process_id']]
            # check all parameters
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

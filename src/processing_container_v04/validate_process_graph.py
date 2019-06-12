import os
import re
from json import load


def load_processes_definitions():
    dirpath = os.path.join(os.path.dirname(__file__), "..", "processes")
    pattern = re.compile(".*.json$")
    filenames = [filename for filename in os.listdir(dirpath) if re.match(pattern, filename)]
    filepaths = [os.path.join(dirpath, filename) for filename in filenames]
    process_defs = dict()
    for filepath in filepaths:
        process_def = load(open(filepath))
        process_defs[process_def['id']] = process_def

    return process_defs


def check_result_nodes(graph):
    pass


def validate_graph(graph):
    process_defs = load_processes_definitions()
    for node in graph.nodes.values():
        pg = node.graph
        if pg['process_id'] in process_defs.keys():
            process_def = process_defs[pg['process_id']]
            # check all parameters
            for parameter_def in process_def['parameters'].values():
                if 'required' in parameter_def.keys() and parameter_def['required']:
                    if parameter_def['name'] not in pg['arguments'].keys():
                        raise Exception("Parameter '{}' is required for process '{}'".format(parameter_def['name'],
                                                                                                  pg['process_id']))
        else:
            raise Exception("'{}' is not in the current set of process definitions.".format(pg['process_id']))

if __name__ == '__main__':
    pass
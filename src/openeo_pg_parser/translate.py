import os
import copy
from collections import OrderedDict
from openeo_pg_parser.graph import OpenEONode, Edge, Graph
from openeo_pg_parser.utils import set_obj_elem_from_keys
from openeo_pg_parser.utils import get_obj_elem_from_keys
from openeo_pg_parser.utils import load_processes
from openeo_pg_parser.utils import load_json_file
from openeo_pg_parser.utils import walk_process_dictionary
from openeo_pg_parser.definitions import OpenEOParameter


def walk_process_graph(process_graph, nodes, process_defs, node_ids=None, level=0, keys=None):
    """
    Recursively walks through an openEO process graph dictionary and transforms the dictionary into a list of graph
    nodes.

    Parameters
    ----------
    process_graph : dict
        Dictionary to walk through.
    nodes : collections.OrderedDict
        Ordered dictionary containing the node IDs as keys and the `graph.Node` instances as values.
    process_defs : dict or str or list
        It can be:
            - dictionary of loaded process definitions (keys are the process ID's)
            - directory path to processes (.json)
            - URL of the remote process endpoint (e.g., "https://earthengine.openeo.org/v1.0/processes")
            - list of loaded process definitions
    node_ids : list, optional
        List of Node ID's for one dictionary branch (only internally used in the recursive process, can be ignored)
    level : int, optional
        Current level/deepness in the dictionary (default is 0,
        only internally used in the recursive process, can be ignored).
    keys : list of str
        List of process graph dictionary keys pointing to the current node.

    Returns
    -------
    nodes : collections.OrderedDict
    node_ids : list
    level : int
    keys : list of str

    """

    process_defs = load_processes(process_defs)

    if keys is None:
        keys = []

    for key, value in process_graph.items():
        if isinstance(value, dict):
            keys = copy.deepcopy(keys)
            keys.append(key)
            if "process_id" in value.keys():  # process node found
                node_counter = len(nodes)
                node_id = "_".join([key, str(node_counter)])
                node = OpenEONode(id=node_id, name=key, content=value, edges=[], depth=level,
                                  processes_src=process_defs)
                node.keys = keys
                if node_ids:
                    filtered_node_ids = [prev_node_id for prev_node_id in node_ids if prev_node_id]
                    parent_node_id = filtered_node_ids[-1]
                    parent_node = nodes[parent_node_id]
                    create_edge(node, parent_node, name="callback")

                    # overwrite depth using parent information
                    node.depth = parent_node.depth + 1

                nodes[node_id] = node
            else:
                node_id = None

            if node_ids is None:
                node_ids = []
            node_ids.append(node_id)
            level += 1
            nodes, node_ids, level, keys = walk_process_graph(value, nodes, process_defs, node_ids=node_ids, level=level,
                                                              keys=keys)

    level += -1
    if node_ids:
        node_ids = node_ids[:-1]
    if keys:
        keys = keys[:-1]

    return nodes, node_ids, level, keys


def find_node_inputs(node, data_link):
    """
    Find input node IDs corresponding to a given linkage for a sub process graph.

    Parameters
    ----------
    node : openEONode
        Node of interest.
    data_link : str
        Linkage name, e.g. "from_node" or "from_parameter".

    Returns
    -------
    keys_lineage : list of lists
        Adjusted keys indexes/lineage to go from the sub process graph to input node ID.
    """

    keys_lineage = []
    for key, value in node.arguments.items():
        keys_lineage_arg, _, _, _ = walk_process_dictionary(value, break_points=["process_graph"])
        if keys_lineage_arg:
            keys_lineage.extend([[key] + elem for elem in keys_lineage_arg if elem[-1] == data_link])

    return keys_lineage


def adjust_from_nodes(process_graph):
    """
    Resets 'from_node' content with corresponding Node IDs.

    Parameters
    ----------
    process_graph : graph.Graph
        openEO process graph as a graph object.

    Returns
    -------
    graph.Graph

    """

    for node in process_graph.nodes:
        pg_same_level = process_graph.find_partners(node, link="callback", include_node=True)
        keys_lineage = find_node_inputs(node, "from_node")
        for key_lineage in keys_lineage:
            data_entry = get_obj_elem_from_keys(node.content['arguments'], key_lineage)
            if data_entry in process_graph.ids:  # data entry already exists as it was created during the recursive walk
                continue
            node_other = pg_same_level.get_node_by_name(data_entry)
            if node_other:
                set_obj_elem_from_keys(node.content['arguments'], key_lineage, node_other.id)
                create_edge(node_other, node)
            else:
                raise Exception('"from_node: {}" reference is wrong.'.format(data_entry))

    return process_graph


def create_edge(node_from, node_to, name="data", hidden=False):
    """
    Creates a directed edge of type `graph.Edge` between the nodes `node_from` and `node_to`.

    Parameters
    ----------
    node_from : graph.Node
        Start node of the edge.
    node_to : graph.Node
        End node of the edge.
    name : str, optional
        Name of the edge (default is "data")
    hidden : bool, optional
            True if edge should be ignored, e.g. for sorting (defaults to False).

    Returns
    -------
    graph.Edge
        Created directed edge consisting of the two given nodes.

    """
    edge_nodes = [node_from, node_to]
    edge_id = "_".join([edge_node.id for edge_node in edge_nodes])
    edge = Edge(id=edge_id, name=name, nodes=edge_nodes, hidden=hidden)
    node_to.add_edge(edge)
    node_from.add_edge(edge)


def adjust_from_parameters(process_graph, parameters=None):
    """"
    Resets 'from_parameter' content with corresponding Node IDs.

    Parameters
    ----------
    process_graph : graph.Graph
        openEO process graph as a graph object.
    parameters : dict, optional
        Globally defined parameters, which can be used in 'from_parameter'.

    Returns
    -------
    graph.Graph

    Notes
    -----
    Attention: after this routine, the graph is sorted by depth!

    """
    parameters = {} if parameters is None else parameters

    # sort graph by depth to complete nodes at a lower level/depth first
    process_graph = process_graph.sort(by='depth')
    for node in process_graph.nodes:
        keys_lineage = find_node_inputs(node, "from_parameter")
        for key_lineage in keys_lineage:
            from_parameter_name = get_obj_elem_from_keys(node.content['arguments'], key_lineage)
            # get all higher level process-graphs, starting from the embedded one
            parent_nodes = process_graph.lineage(node, link="callback", ancestors=False, include_node=False)
            parameter_found = False
            for parent_node in parent_nodes:  # backtrace as long a parent process exists
                process = parent_node.process
                # First, check if parameter is contained in the parameters of the sub-process
                sub_parameters = process.sub_parameters
                if sub_parameters is not None and from_parameter_name in sub_parameters.keys():
                    parameter = process.sub_parameters[from_parameter_name]
                    node_relatives = parent_node.relatives(link="data", ancestor=True)
                    # parameter is required, but the start node has no input data -> take parent node as data reference
                    if parameter.is_required and not node_relatives:
                        create_edge(parent_node, node, hidden=True)
                        node_argument = {'from_node': '{}'.format(parent_node.id)}
                        set_obj_elem_from_keys(node.content['arguments'], key_lineage[:-1], node_argument)
                    # parameter is required and parent node has input data -> add all data relatives of parent node later
                    elif parameter.is_required and node_relatives:
                        node_arguments = []
                        if len(keys_lineage) == len(node_relatives):  # each from parameter points to each input argument, e.g., in overlap_resolver
                            from_parameter_idx = list(sub_parameters.keys()).index(from_parameter_name)  # get node index referring to sub-parameter index
                            node_relatives = [node_relatives[from_parameter_idx]]
                        for node_relative in node_relatives:
                            create_edge(node_relative, node)
                            node_arguments.append({'from_node': '{}'.format(node_relative.id)})
                        if len(node_arguments) == 1:
                            set_obj_elem_from_keys(node.content['arguments'], key_lineage[:-1], node_arguments[0])
                        else:
                            set_obj_elem_from_keys(node.content['arguments'], key_lineage[:-1], node_arguments)
                    # parameter is not required -> take its default value
                    else:
                        set_obj_elem_from_keys(node.content['arguments'], key_lineage[:-1], parameter.default_value)
                    parameter_found = True
                # Second, check if parameter is contained in process (take the default values)
                elif from_parameter_name in process.parameters.keys():
                    parameter = process.parameters[from_parameter_name]
                    set_obj_elem_from_keys(node.content['arguments'], key_lineage[:-1], parameter.default_value)
                    parameter_found = True
                # Third, check if parameter is contained in parameter definition at the same level
                elif parent_node.parameters:
                    for parameter in parent_node.parameters:
                        if from_parameter_name == parameter.name:
                            set_obj_elem_from_keys(node.content['arguments'], key_lineage[:-1], parameter.default_value)
                            parameter_found = True
                            break

                if parameter_found:
                    break

            # if the parameter name is still not available, try to look into the globally defined parameters
            if not parameter_found:
                if from_parameter_name in parameters.keys():
                    parameter_found = True
                    set_obj_elem_from_keys(node.content['arguments'], key_lineage[:-1], parameters[from_parameter_name])

            # parameter seems not to be available, raise an error
            if not parameter_found:
                err_msg = "'from_parameter' reference name '{}' " \
                          "can't be found or is not defined.".format(from_parameter_name)
                raise ValueError(err_msg)

    return process_graph


def adjust_callbacks(process_graph):
    """
    Resets embedded process graphs with their respective callback node ID.

    Parameters
    ----------
    process_graph : graph.Graph
        openEO process graph as a graph object.

    Returns
    -------
    graph.Graph

    """

    for node in process_graph.nodes:
        # set parent node process graph content with child node ID if 'result' is true
        if node.is_result and node.parent_process is not None:
            keys = node.keys[len(node.parent_process.keys):-2]  # exclude "process_graph" and node id at the end
            set_obj_elem_from_keys(node.parent_process.content, keys, {"from_node": node.id})

    return process_graph


def link_nodes(process_graph, parameters=None):
    """
    Links all nodes in the graph, i.e. links 'from_node', 'from_argument' and 'callback' with the corresponding
    Node IDs.


    Parameters
    ----------
    process_graph : graph.Graph
        Process graph to connect the nodes within.
    parameters : dict, optional
        Globally defined parameters, which can be used in 'from_parameter'.

    Returns
    -------
    graph.Graph

    """

    # fill in all from_node parameters and create edges
    process_graph = adjust_from_nodes(process_graph)

    # update the edges of the graph
    process_graph.update()

    # fill in all from_argument parameters
    process_graph = adjust_from_parameters(process_graph, parameters=parameters)

    # update the edges of the graph
    process_graph.update()

    # replace all embedded process graphs with the respective node IDs
    process_graph = adjust_callbacks(process_graph)

    return process_graph


def translate_process_graph(pg_filepath, process_defs=None, parameters=None):
    """
    Translates an openEO process graph into a graph.Graph object.

    Parameters
    ----------
    pg_filepath : str or dict
        openEO process graph given as full file path or a stacked dictionary.
    process_defs : dict or str or list, optional
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
    graph.Graph
        Parsed openEO process graph.

    """

    if isinstance(pg_filepath, str):
        process_graph = load_json_file(pg_filepath)
    elif isinstance(pg_filepath, dict):
        process_graph = pg_filepath
    else:
        raise ValueError("'pg_filepath must either be file path to a JSON file or a dictionary.'")

    # remove first layer of the process graph
    parameters = {} if parameters is None else parameters
    if "parameters" in process_graph.keys():
        for parameter_def in process_graph['parameters']:
            parameter = OpenEOParameter(parameter_def)
            parameters.update({parameter.name: parameter.default_value})

    if "process_graph" in process_graph.keys():
        process_graph = process_graph['process_graph']
    else:
        err_msg = "Process graph structure is invalid: " \
                  "Processes need to be declared/wrapped inside 'process_graph' layer."
        raise Exception(err_msg)

    # define source of process definitions
    process_defs = os.path.join(os.path.dirname(__file__), "processes") \
        if process_defs is None else process_defs

    # traverse process graph
    nodes = OrderedDict()
    nodes, _, _, _ = walk_process_graph(process_graph, nodes, process_defs)

    # create graph object
    process_graph = Graph(nodes)

    # link all nodes and fill in from_node and from_argument
    process_graph = link_nodes(process_graph, parameters=parameters)

    return process_graph


if __name__ == '__main__':
    pass

import os
import copy
from collections import OrderedDict
from openeo_pg_parser.graph import OpenEONode, Graph, create_edge
from openeo_pg_parser.utils import set_obj_elem_from_keys
from openeo_pg_parser.utils import get_obj_elem_from_keys
from openeo_pg_parser.utils import load_processes
from openeo_pg_parser.utils import load_json_file
from openeo_pg_parser.utils import find_node_inputs
from openeo_pg_parser.definitions import OpenEOParameter


def walk_process_graph(process_graph, nodes, process_defs, node_ids=None, level=0, keys=None, global_parameters=None):
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
    global_parameters : dict, optional
        Globally defined parameters, which can be used in 'from_parameter'.

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

                    # a process graph callback is present, create a respective edge
                    create_edge(node, parent_node, name="callback")

                    # if this node returns a result, then create a process dependency for the parent node
                    if node.is_result:
                        create_edge(node, parent_node, name="process")

                    # overwrite depth using parent information
                    node.depth = parent_node.depth + 1

                # if this node contains a 'from_parameter' argument create a data link to a parent node
                # and fill in default values
                if node.expects_parent_input:
                    current_graph = Graph(nodes)
                    node, data_parent_nodes = resolve_from_parameter(node, current_graph,
                                                                     global_parameters=global_parameters)
                    for data_parent_node in data_parent_nodes:
                        create_edge(data_parent_node, node, name="data")

                nodes[node_id] = node
            else:
                node_id = None

            if node_ids is None:
                node_ids = []
            node_ids.append(node_id)
            level += 1
            nodes, node_ids, level, keys = walk_process_graph(value, nodes, process_defs, node_ids=node_ids, level=level,
                                                              keys=keys, global_parameters=global_parameters)

    level += -1
    if node_ids:
        node_ids = node_ids[:-1]
    if keys:
        keys = keys[:-1]

    return nodes, node_ids, level, keys


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
            node_other = pg_same_level.get_node_by_name(data_entry)
            if node_other:
                set_obj_elem_from_keys(node.content['arguments'], key_lineage, node_other.id)
                create_edge(node_other, node, name="process")
                create_edge(node_other, node, name="data")
            else:
                raise Exception('"from_node: {}" reference is wrong.'.format(data_entry))

    return process_graph


def resolve_from_parameter(node, process_graph, global_parameters=None):
    """
    Resolves "from_parameter" relationship between a node and its parents.
    This means "from_parameter" attributes are replaced with default or global values.

    Parameters
    ----------
    node : OpenEONode
        Node containing 'from_parameter' in argument.
    process_graph : graph.Graph
        Subset or complete openEO process graph as a graph object.
    global_parameters : dict, optional
        Globally defined parameters, which can be used in 'from_parameter'.

    Returns
    -------
    node : OpenEONode
        Node with optional 'from_parameter' argument reset to default parameter values.
    parent_node : OpenEONode
        Parent data node corresponding to the 'from_parameter' argument.

    """
    keys_lineage = find_node_inputs(node, "from_parameter")
    parent_nodes_found = []
    for key_lineage in keys_lineage:
        from_parameter_name = get_obj_elem_from_keys(node.content['arguments'], key_lineage)
        # get all higher level process-graphs, starting from the embedded one
        parent_nodes = process_graph.lineage(node, link="callback", ancestors=False, include_node=False)
        for parent_node in parent_nodes:  # backtrace as long a parent process exists
            process = parent_node.process
            # First, check if parameter is contained in the parameters of the sub-process
            sub_parameters = process.sub_parameters
            if sub_parameters is not None and from_parameter_name in sub_parameters.keys():
                parameter = process.sub_parameters[from_parameter_name]
                if parameter.default_value is not None:
                    set_obj_elem_from_keys(node.content['arguments'], key_lineage[:-1], parameter.default_value)
                parent_nodes_found.append(parent_node)
            # Second, check if parameter is contained in process (take the default values)
            elif from_parameter_name in process.parameters.keys():
                parameter = process.parameters[from_parameter_name]
                if parameter.default_value is not None:
                    set_obj_elem_from_keys(node.content['arguments'], key_lineage[:-1], parameter.default_value)
                parent_nodes_found.append(parent_node)
            # Third, check if parameter is contained in parameter definition at the same level
            elif parent_node.parameters:
                for parameter in parent_node.parameters:
                    if from_parameter_name == parameter.name:
                        if parameter.default_value is not None:
                            set_obj_elem_from_keys(node.content['arguments'], key_lineage[:-1], parameter.default_value)
                        parent_nodes_found.append(parent_node)

        # if the parameter name is still not available, try to look into the globally defined parameters
        if global_parameters and global_parameters.get(from_parameter_name):
            set_obj_elem_from_keys(node.content['arguments'], key_lineage[:-1], global_parameters[from_parameter_name])
        else:
            if not parent_nodes_found:  # parameter seems not to be available, raise an error
                err_msg = "'from_parameter' reference name '{}' " \
                          "can't be found or is not defined.".format(from_parameter_name)
                raise ValueError(err_msg)

    return node, parent_nodes_found


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


def link_nodes(process_graph):
    """
    Links all nodes in the graph, i.e. links 'from_node', 'from_argument' and 'callback' with the corresponding
    Node IDs.


    Parameters
    ----------
    process_graph : graph.Graph
        Process graph to connect the nodes within.

    Returns
    -------
    graph.Graph

    """

    # fill in all from_node parameters and create edges
    process_graph = adjust_from_nodes(process_graph)

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
    if process_graph.get("parameters"):
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
    nodes, _, _, _ = walk_process_graph(process_graph, nodes, process_defs, global_parameters=parameters)

    # create graph object
    process_graph = Graph(nodes)

    # link all nodes and fill in from_node and from_argument
    process_graph = link_nodes(process_graph)

    return process_graph


if __name__ == '__main__':
    pass

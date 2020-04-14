import copy
from json import load
from collections import OrderedDict
from openeo_pg_parser_python.graph import Node, Edge, Graph


def keys2str(keys):
    """
    Converts list of keys to a string, which can be used for indexing (e.g., a dictionary).

    Parameters
    ----------
    keys : list of str
        List of keys.

    Returns
    -------
    str
        Indexing string.
    """

    key_str = ""
    for key in keys:
        if isinstance(key, str):
            key = "'{}'".format(key)
        key_str += "[{}]".format(key)

    return key_str


def get_obj_elem_from_keys(obj, keys):
    """
    Returns values stored in `obj` by using a list of keys for indexing.

    Parameters
    ----------
    obj : object
        Python object offering indexing, e.g., a dictionary.
    keys : list of str
        List of keys for indexing.

    Returns
    -------
    object
        Values of the indexed object.
    """

    key_str = keys2str(keys)
    return copy.deepcopy(eval('obj' + key_str))


def set_obj_elem_from_keys(obj, keys, value):
    """
    Sets values in `obj` by using a list of keys for indexing.

    Parameters
    ----------
    obj : object
        Python object offering indexing, e.g., a dictionary.
    keys : list of str
        List of keys for indexing.
    value : object
        Python object to store in `obj`.

    Returns
    -------
    object
        Reset object including the given `value`.
    """

    key_str = keys2str(keys)
    exec('obj{}={}'.format(key_str, value))
    return obj


def walk_process_graph(process_graph, nodes, node_ids=None, level=0, prev_level=0):
    """
    Recursively walks through an openEO process graph dictionary and transforms the dictionary into a list of graph
    nodes.

    Parameters
    ----------
    process_graph : dict
        Dictionary to walk through.
    nodes : collections.OrderedDict
        Ordered dictionary containing the node IDs as keys and the `graph.Node` instances as values.
    node_ids : list, optional
        List of Node ID's for one dictionary branch (only internally used in the recursive process, can be ignored)
    level : int, optional
        Current level/deepness in the dictionary (default is 0,
        only internally used in the recursive process, can be ignored).
    prev_level : int, optional
        Previous level/deepness in the dictionary (default is 0,
        only internally used in the recursive process, can be ignored)).

    Returns
    -------
    nodes : collections.OrderedDict
    node_ids : list
    level : int
    prev_level : int
    """

    for key, value in process_graph.items():
        if isinstance(value, dict):
            if "process_id" in value.keys():
                node_counter = len(nodes)
                node_id = "_".join([key, str(node_counter)])
                node = Node(id=node_id, name=key, content=value, edges=[])
                if node_ids:
                    filtered_node_ids = [prev_node_id for prev_node_id in node_ids if prev_node_id]
                    parent_node = nodes[filtered_node_ids[-1]]
                    edge_nodes = [parent_node, node]
                    edge_id = "_".join([edge_node.id for edge_node in edge_nodes])
                    edge_name = "callback"
                    edge = Edge(id=edge_id, name=edge_name, nodes=edge_nodes)
                    node.add_edge(edge)
                    # trim pg graph of previous node
                    parent_node.content = replace_callback(parent_node.content, {'callback': None})

                nodes[node_id] = node
            else:
                node_id = None

            if node_ids is None:
                node_ids = []

            node_ids.append(node_id)
            prev_level = level
            level += 1
            nodes, node_ids, level, prev_level = walk_process_graph(value, nodes, node_ids=node_ids, level=level,
                                                                    prev_level=prev_level)

    level += -1
    if node_ids:
        node_ids = node_ids[:-1]

    return nodes, node_ids, level, prev_level


def walk_pg_arguments(process_graph, keys_lineage=None, key_lineage=None, level=0, prev_level=0):
    """
    Recursively walks through an "argument" process graph dictionary and collects the keys lineage/the keys to the
    process input arguments.

    Parameters
    ----------
    process_graph : dict
        Dictionary to walk through.
    keys_lineage : list of lists, optional
        List of key lineages. (only internally used in the recursive process, can be ignored).
    key_lineage: list of str, optional
        Keys necessary to get the name of the input process id (only internally used in the recursive process,
        can be ignored)
    level : int, optional
        Current level/deepness in the dictionary (default is 0,
        only internally used in the recursive process, can be ignored).
    prev_level : int, optional
        Previous level/deepness in the dictionary (default is 0,
        only internally used in the recursive process, can be ignored)).

    Returns
    -------
    keys_lineage : list of lists
    key_lineage : list of str
    level : int
    prev_level : int
    """

    if key_lineage is None:
        key_lineage = []

    if keys_lineage is None:
        keys_lineage = []

    if isinstance(process_graph, dict):
        for k, v in process_graph.items():
            key_lineage.append(k)
            sub_pg_graph = process_graph[k]
            level += 1
            prev_level = level
            keys_lineage, key_lineage, level, prev_level = walk_pg_arguments(sub_pg_graph, keys_lineage=keys_lineage,
                                                                        key_lineage=key_lineage, level=level,
                                                                        prev_level=prev_level)
    elif isinstance(process_graph, list):
        for i, elem in enumerate(process_graph):
            key_lineage.append(i)
            sub_pg_graph = process_graph[i]
            level += 1
            prev_level = level
            keys_lineage, key_lineage, level, prev_level = walk_pg_arguments(sub_pg_graph, keys_lineage=keys_lineage,
                                                                        key_lineage=key_lineage, level=level,
                                                                        prev_level=prev_level)

    level -= 1
    if key_lineage and (key_lineage not in keys_lineage):
        if (level - prev_level) == -1:
            keys_lineage.append(key_lineage)
        key_lineage = key_lineage[:-1]

    return keys_lineage, key_lineage, level, prev_level


def find_node_inputs(process_graph, data_link):
    """
    Find input node IDs corresponding to a given linkage for a sub process graph.

    Parameters
    ----------
    process_graph : dict
        Sub process graph/dictionary to walk through.
    data_link : str
        Linkage name, e.g. "from_node" or "from_argument".

    Returns
    -------
    keys_lineage : list of lists
        Adjusted keys indexes/lineage to go from the sub process graph to input node ID.
    """

    keys_lineage = []
    for key, value in process_graph['arguments'].items():
        keys_lineage_arg, _, _, _ = walk_pg_arguments(value)
        if keys_lineage_arg:
            keys_lineage.extend([[key] + elem for elem in keys_lineage_arg if elem[-1] == data_link])

    return keys_lineage


def replace_callback(process_graph, value):
    """
    Removes redundant callback layer.

    Parameters
    ----------
    process_graph : dict
        Sub process graph/dictionary.
    value : object
        Python object to store in `process_graph`.

    Returns
    -------
    dict
        Sub process graph/dictionary.
    """

    for k, v in process_graph['arguments'].items():
        if isinstance(v, dict) and 'callback' in v.keys():
            process_graph['arguments'][k] = value
    return process_graph


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

    for node in process_graph.nodes.values():
        pg_same_level = process_graph.find_siblings(node, link="callback", include_node=True)
        keys_lineage = find_node_inputs(node.content, "from_node")
        for key_lineage in keys_lineage:
            data_entry = get_obj_elem_from_keys(node.content['arguments'], key_lineage)
            if data_entry in process_graph.ids:
                continue
            node_other = pg_same_level.get_node_by_name(data_entry)
            if node_other:
                set_obj_elem_from_keys(node.content['arguments'], key_lineage, "'{}'".format(node_other.id))
                edge_nodes = [node_other, node]
                edge_id = "_".join([edge_node.id for edge_node in edge_nodes])
                edge_name = "data"
                edge = Edge(id=edge_id, name=edge_name, nodes=edge_nodes)
                node.add_edge(edge)
            else:
                raise Exception('"from_node: {}" reference is wrong.'.format(data_entry))

    return process_graph


def adjust_from_arguments(process_graph):
    """"
    Resets 'from_arguments' content with corresponding Node IDs.

    Parameters
    ----------
    process_graph : graph.Graph
        openEO process graph as a graph object.

    Returns
    -------
    graph.Graph
    """

    for node in process_graph.nodes.values():
        keys_lineage = find_node_inputs(node.content, "from_argument")
        for key_lineage in keys_lineage:
            nodes_lineage = process_graph.lineage(node, link="callback")
            if nodes_lineage:
                root_node = nodes_lineage[-1]
                node_other = root_node.parent('data')
                if node_other:
                    set_obj_elem_from_keys(node.content['arguments'], key_lineage[:-1],
                                           {'from_node': '{}'.format(node_other.id)})
                    edge_nodes = [node_other, node]
                    edge_id = "_".join([edge_node.id for edge_node in edge_nodes])
                    edge_name = "data"
                    edge = Edge(id=edge_id, name=edge_name, nodes=edge_nodes)
                    node.add_edge(edge)
            else:
                raise Exception('"from_argument" reference is wrong.')

    return process_graph


def adjust_callbacks(process_graph):
    """
    Resets callback with 'from_node' and corresponding Node IDs.

    Parameters
    ----------
    process_graph : graph.Graph
        openEO process graph as a graph object.

    Returns
    -------
    graph.Graph
    """

    for node in process_graph.nodes.values():
        node_descendants = node.descendants(link="callback")
        if node_descendants:
            node_result = None
            for node_descendant in node_descendants:
                if ("result" in node_descendant.content.keys()) and node_descendant.content['result']:
                    node_result = node_descendant
                    break
            if node_result:
                node.content = replace_callback(node.content, {'from_node': node_result.id})
            else:
                raise Exception('There must be one result node within the scope of {}'.format(node.name))

    return process_graph


def link_nodes(process_graph):
    """
    Links all nodes in the graph, i.e. links 'from_node', 'from_argument' and 'callback' with the corresponding
    Node IDs.


    Parameters
    ----------
    process_graph : graph.Graph


    Returns
    -------
    graph.Graph
    """


    # fill in all from_node parameters and create edges
    process_graph = adjust_from_nodes(process_graph)

    # update the edges of the graph
    process_graph.update()

    # fill in all from_argument parameters
    process_graph = adjust_from_arguments(process_graph)

    # update the edges of the graph
    process_graph.update()

    # fill in the callback result nodes
    process_graph = adjust_callbacks(process_graph)

    # update the edges of the graph
    process_graph.update()

    return process_graph


def translate_process_graph(pg_filepath):
    """
    Translates an openEO process graph into a graph.Graph object.

    Parameters
    ----------
    pg_filepath : str or dict
        openEO process graph given as full file path or a stacked dictionary.

    Returns
    -------
    graph.Graph
        Parsed openEO process graph.
    """

    if isinstance(pg_filepath, str):
        process_graph = load(open(pg_filepath))
    elif isinstance(pg_filepath, dict):
        process_graph = pg_filepath
    else:
        raise ValueError("'pg_filepath must either be file path to a JSON file or a dictionary.'")

    nodes = OrderedDict()
    nodes, _, _, _ = walk_process_graph(process_graph, nodes)

    # create graph object
    process_graph = Graph(nodes)

    # link all nodes and fill in from_node and from_argument
    process_graph = link_nodes(process_graph)

    return process_graph

if __name__ == '__main__':
    pass

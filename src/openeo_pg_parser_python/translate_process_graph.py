import copy
import secrets
from json import load
from collections import OrderedDict
from openeo_pg_parser_python.graph import Node, Edge, Graph


def walk_pg_graph(nodes, data, node_ids=None, level=0, prev_level=0):
    for key, value in data.items():
        if isinstance(value, dict):
            if "process_id" in value.keys():
                token = secrets.token_hex(nbytes=8)
                node_id = "_".join([key, token])
                node = Node(id=node_id, name=key, graph=value, edges=[])
                if node_ids:
                    filtered_node_ids = [prev_node_id for prev_node_id in node_ids if prev_node_id]
                    parent_node = nodes[filtered_node_ids[-1]]
                    edge_nodes = [node, parent_node]
                    edge_id = "_".join([edge_node.id for edge_node in edge_nodes])
                    edge_name = "callback"
                    edge = Edge(id=edge_id, name=edge_name, nodes=edge_nodes)
                    node.add_edge(edge)
                    # trim pg graph of previous node
                    parent_node.graph = replace_callback(parent_node.graph, {'callback': None})

                nodes[node_id] = node
            else:
                node_id = None

            if node_ids is None:
                node_ids = []

            node_ids.append(node_id)
            prev_level = level
            level += 1
            nodes, node_ids, level, prev_level = walk_pg_graph(nodes, value, node_ids=node_ids, level=level,
                                                               prev_level=prev_level)

    level += -1
    if node_ids:
        node_ids = node_ids[:-1]

    return nodes, node_ids, level, prev_level


def keys2str(keys):
    key_str = ""
    for key in keys:
        if isinstance(key, str):
            key = "'{}'".format(key)
        key_str += "[{}]".format(key)

    return key_str


def get_obj_elem_from_keys(obj, keys):
    key_str = keys2str(keys)
    return copy.deepcopy(eval('obj' + key_str))


def set_obj_elem_from_keys(obj, keys, value):
    key_str = keys2str(keys)
    exec('obj{}={}'.format(key_str, value))
    return obj


# TODO: this function could need a refactoring depending on the process graph design
def walk_pg_arguments(pg_graph, keys_lineage=None, key_lineage=None, level=0, prev_level=0):
    if key_lineage is None:
        key_lineage = []

    if keys_lineage is None:
        keys_lineage = []

    if isinstance(pg_graph, dict):
        for k, v in pg_graph.items():
            key_lineage.append(k)
            sub_pg_graph = pg_graph[k]
            level += 1
            prev_level = level
            keys_lineage, key_lineage, level, prev_level = walk_pg_arguments(sub_pg_graph, keys_lineage=keys_lineage,
                                                                        key_lineage=key_lineage, level=level,
                                                                        prev_level=prev_level)
    elif isinstance(pg_graph, list):
        for i, elem in enumerate(pg_graph):
            key_lineage.append(i)
            sub_pg_graph = pg_graph[i]
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


def find_node_inputs(pg_graph, data_link):
    keys_lineage = []
    for key, value in pg_graph['arguments'].items():
        keys_lineage_arg, _, _, _ = walk_pg_arguments(value)
        if keys_lineage_arg:
            keys_lineage.extend([[key] + elem for elem in keys_lineage_arg if elem[-1] == data_link])

    return keys_lineage


def replace_callback(pg_graph, value):
    for k, v in pg_graph['arguments'].items():
        if isinstance(v, dict) and 'callback' in v.keys():
            pg_graph['arguments'][k] = value
    return pg_graph


def from_node(nodes, node_name):
    for node in nodes:
        if node.name == node_name:
            return node

    return None


def adjust_from_nodes(graph):

    for node in graph.nodes.values():
        nodes_same_level = graph.nodes_at_same_level(node, link="callback", include_node=True)
        keys_lineage = find_node_inputs(node.graph, "from_node")
        for key_lineage in keys_lineage:
            data_entry = get_obj_elem_from_keys(node.graph['arguments'], key_lineage)
            if data_entry in graph.ids:
                continue
            node_other = from_node(nodes_same_level, data_entry)
            if node_other:
                set_obj_elem_from_keys(node.graph['arguments'], key_lineage, "'{}'".format(node_other.id))
                edge_nodes = [node_other, node]
                edge_id = "_".join([edge_node.id for edge_node in edge_nodes])
                edge_name = "data"
                edge = Edge(id=edge_id, name=edge_name, nodes=edge_nodes)
                node.add_edge(edge)
            else:
                raise Exception('"from_node: {}" reference is wrong.'.format(data_entry))

    return graph


def adjust_from_arguments(graph):

    # TODO: keep binary behaviour in mind
    for node in graph.nodes.values():
        keys_lineage = find_node_inputs(node.graph, "from_argument")
        for key_lineage in keys_lineage:
            nodes_lineage = graph.node_lineage(node, link="callback", ancestors=False)
            if nodes_lineage:
                root_node = nodes_lineage[-1]
                node_other = root_node.parent('data')
                if node_other:
                    set_obj_elem_from_keys(node.graph['arguments'], key_lineage[:-1],
                                           {'from_node': '{}'.format(node_other.id)})
                    edge_nodes = [node_other, node]
                    edge_id = "_".join([edge_node.id for edge_node in edge_nodes])
                    edge_name = "data"
                    edge = Edge(id=edge_id, name=edge_name, nodes=edge_nodes)
                    node.add_edge(edge)
            else:
                raise Exception('"from_argument" reference is wrong.')

    return graph


def adjust_callbacks(graph):

    for node in graph.nodes.values():
        node_descendants = node.ancestors(link="callback")
        if node_descendants:
            node_result = None
            for node_descendant in node_descendants:
                if ("result" in node_descendant.graph.keys()) and node_descendant.graph['result']:
                    node_result = node_descendant
                    break
            if node_result:
                node.graph = replace_callback(node.graph, {'from_node': node_result.id})
            else:
                raise Exception('There must be one result node within the scope of {}'.format(node.name))

    return graph


# TODO is an update after every step even necessary?
def link_nodes(graph):
    # update graph regarding "callback" nodes
    graph.update()

    # fill in all from_node parameters and create edges
    graph = adjust_from_nodes(graph)

    # update the graph regarding "data" nodes
    graph.update()

    # fill in all from_argument parameters
    graph = adjust_from_arguments(graph)

    # update the graph regarding "data" nodes
    graph.update()

    # fill in the callback result nodes
    graph = adjust_callbacks(graph)

    return graph


def translate_graph(pg_filepath):
    pg_dict = load(open(pg_filepath))
    nodes = OrderedDict()
    nodes, _, _, _ = walk_pg_graph(nodes, pg_dict)

    # create graph object
    graph = Graph(nodes)

    # link all nodes and fill in from_node and from_argument
    graph = link_nodes(graph)

    return graph

if __name__ == '__main__':
    pass

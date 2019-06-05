import copy
import secrets
import numpy as np
from json import load
from pprint import pformat
from collections import OrderedDict


class Node(object):
    def __init__(self, id=None, name=None, graph=None, edges=None, parent_nodes=None, child_nodes=None):
        self.id = id
        self.name = name
        self.graph = graph
        self.edges = edges
        self.parent_nodes = parent_nodes
        self.child_nodes = child_nodes

    def __repr__(self):
        pass

    def __str__(self):
        pg_str = pformat(self.graph)
        repr_str = "Node ID: {} \nNode Name: {} \n{}".format(self.id, self.name, pg_str)

        return repr_str

# class ProcessingNode(Node):
#     def __init__(self, ):
#         super(ProcessingNode).__init__(id, name, graph)
#
#     @classmethod
#     def from_node(cls, node):

class Edge(object):
    def __init__(self, id=None, name=None, nodes=None):
        self.id = id
        self.name = name
        self.nodes = nodes

    @property
    def node_ids(self):
        return [node.id for node in self.nodes]


class Graph(object):
    def __init__(self, nodes=None, edges=None, tree_ids=None, branch_ids=None, leaf_ids=None):
        self.nodes = nodes
        self.edges = edges
        self.tree_ids = tree_ids
        self.branch_ids = branch_ids
        self.leaf_ids = leaf_ids

    @property
    def nnodes(self):
        return len(self.nodes)

    @property
    def nedges(self):
        return len(self.edges)

    def __str__(self):
        repr_str = ""
        tree_ids = list(self.tree_ids.values())
        nodes = list(self.nodes.values())
        nodes_sorted = np.array(nodes)[np.argsort(tree_ids)].tolist()
        for node in nodes_sorted:
            repr_str_per_node = str(node) + "\n\n"
            repr_str += repr_str_per_node

        return repr_str


def walk_pg_graph(nodes, data, node_ids=[], level=0, prev_level=0):
    for key, value in data.items():
        if isinstance(value, dict):
            if "process_id" in value.keys():
                token = secrets.token_hex(nbytes=8)
                node_id = "_".join([key, token])
                node = Node(id=node_id, name=key, graph=value, edges=[])
                if node_ids:
                    filtered_node_ids = [prev_node_id for prev_node_id in node_ids if prev_node_id]
                    parent_node = nodes[filtered_node_ids[-1]]
                    edge_nodes = [parent_node, node]
                    edge_id = "_".join([edge_node.id for edge_node in edge_nodes])
                    edge = Edge(id=edge_id, nodes=edge_nodes)
                    node.edges.append(edge)
                nodes[node_id] = node
            else:
                node_id = None

            node_ids.append(node_id)
            prev_level = level
            level += 1
            nodes, node_ids, level, prev_level = walk_pg_graph(nodes, value, node_ids=node_ids, level=level,
                                                               prev_level=prev_level)

    level += -1
    if node_ids:
        node_ids = node_ids[:-1]

    return nodes, node_ids, level, prev_level


def validate_pg_graph():
    pass

def from_node(nodes, node_name):
    for node in nodes:
        if node.name == node_name:
            return node

    return None

def find_siblings(nodes, node):
    siblings = []
    for node_other in nodes:
        if node_other.id != node.id:
            if node.parent_nodes[-1].id == node_other.parent_nodes[-1].id:
                siblings.append(node)

    return siblings


# TODO: code is repeated twice, outsource it to function
def link_nodes(nodes):
    # fill in all from_node parameters and create edges
    for node in nodes.values():
        siblings = find_siblings(nodes, node)
        for arg in node.graph['arguments'].keys():
            data_arg = node.graph['arguments'][arg]
            if not isinstance(data_arg, list):
                data_arg = [data_arg]
            for i, data_entry in enumerate(data_arg):
                if 'from_node' in data_entry.keys():
                    node_other = from_node(siblings, data_entry['from_node'])
                    if node_other:
                        if len(data_arg) > 1:
                            node.graph['arguments'][arg][i]['from_node'] = node_other.id
                        else:
                            node.graph['arguments'][arg]['from_node'] = node_other.id
                        edge_nodes = [node_other, node]
                        edge_id = "_".join([edge_node.id for edge_node in edge_nodes])
                        edge = Edge(id=edge_id, nodes=edge_nodes)
                        node.edges.append(edge)
                    else:
                        raise Exception('') # TODO

    # fill in all from_argument parameters
    # TODO: keep binary behaviour in mind
    for node in nodes.values():
        for arg in node.graph['arguments'].keys():
            data_arg = node.graph['arguments'][arg]
            if not isinstance(data_arg, list):
                data_arg = [data_arg]
            for i, data_entry in enumerate(data_arg):
                if 'from_argument' in data_entry.keys():
                    node_other =
                    if node_other:
                        if len(data_arg) > 1:
                            node.graph['arguments'][arg][i]['from_node'] = node_other.id
                        else:
                            node.graph['arguments'][arg]['from_node'] = node_other.id
                        edge_nodes = [node_other, node]
                        edge_id = "_".join([edge_node.id for edge_node in edge_nodes])
                        edge = Edge(id=edge_id, nodes=edge_nodes)
                        node.edges.append(edge)
                    else:
                        raise Exception('') # TODO




def translate(pg_filepath):
    pg_dict = load(open(pg_filepath))
    nodes = OrderedDict()
    nodes, _, _, _ = walk_pg_graph(nodes, pg_dict)
    # create graph and sub_graph


    return

if __name__ == '__main__':
    #test_dict = {'a': {'b': {'c': 3}, 'd': {'e': 4}}, 'd': 9, 'g': {'f': 3, 't': {'h': {'z': 5}}}}
    #keys_tree, _, _, _ = walkdict(test_dict)
    pass
import copy
import numpy as np
from json import load
from pprint import pformat
from collections import OrderedDict


class Node(object):
    def __init__(self, id=None, name=None, graph=None, edges=None):
        self.id = id
        self.name = name
        self.graph = graph
        self.edges = edges

    def __repr__(self):
        pass

    def __str__(self):
        pg_str = pformat(self.graph)
        repr_str = "Node ID: {} \nNode Name: {} \n{}".format(self.id, self.name, pg_str)

        return repr_str


class Edge(object):
    def __init__(self, id=None, name=None, nodes=None):
        self.id = id
        self.name = name
        self.nodes = nodes

    @property
    def node_ids(self):
        return [node.id for node in self.nodes]


class Graph(object):
    def __init__(self, nodes=None, edges=None, levels=None, branch_ids=None, tree_ids=None):
        self.nodes = nodes
        self.edges = edges
        self.levels = levels
        self.branch_ids = branch_ids
        self.tree_ids = tree_ids

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


def walkdict(data, keys_tree=None, keys_branch=None, counter=0, prev_counter=0):
    for k, v in data.items():
        if isinstance(v, dict):
            if keys_branch is None:
                keys_branch = []
            keys_branch.append(k)
            counter +=1
            prev_counter = counter
            keys_tree, keys_branch, counter, prev_counter = walkdict(v, keys_tree=keys_tree, keys_branch=keys_branch,
                                                                     counter=counter, prev_counter=prev_counter)

    counter += -1
    if keys_tree is None:
        keys_tree = []
    if keys_branch not in keys_tree and keys_branch != []:
        if (counter - prev_counter) == -1:
            keys_tree.append(keys_branch)
        keys_branch = keys_branch[:-1]

    return keys_tree, keys_branch, counter, prev_counter


def find_parent_leafs(forest, tree_id, links, level):
    tree_nodes = np.array([node for node in forest.nodes.values() if (tree_id == forest.tree_ids[node.id])])
    tree_node_levels = np.array([forest.levels[tree_node.id] for tree_node in tree_nodes])
    tree_nodes = tree_nodes[tree_node_levels < level]
    tree_node_levels = tree_node_levels[tree_node_levels < level]
    sort_idxs = np.argsort(tree_node_levels)
    tree_nodes = tree_nodes[sort_idxs]
    tree_nodes = tree_nodes.tolist()
    tree_node_levels = tree_node_levels.tolist()
    parent_nodes = [tree_nodes[0]]

    if len(tree_nodes) > 1:
        link_idx = 0
        prev_level = 0
        for i, tree_node in enumerate(tree_nodes):
            parent_node = parent_nodes[-1]
            curr_level = tree_node_levels[i]
            if curr_level <= prev_level:
                continue

            edge_id = "{}__{}__{}".format(parent_node.id, links[link_idx], tree_node.id)
            if edge_id in forest.edges.keys():
                parent_nodes.append(tree_node)
                link_idx += 1

    return parent_nodes


def create_links(branch_keys):
    links = []
    for i in range(1, len(branch_keys)):
        if branch_keys[i-1] == 'arguments':
            links.append(branch_keys[i])

    return links


def from_node(forest, node_name):
    node_id = None
    for node_other in forest.nodes.values():
        if node_other.name == node_name:
            node_id = node_other.id

    return node_id


# TODO: check if two argument parsing parts are necessary
def from_argument(forest, tree_id, links, link_name, level):
    parent_node_id = None
    parent_nodes = find_parent_leafs(forest, tree_id, links, level)
    # if from argument is linked inside the same tree
    for i in range(1, len(parent_nodes)):
        parent_edge_id = "{}__{}__{}".format(parent_nodes[i-1].id, link_name, parent_nodes[i].id)
        if parent_edge_id in forest.edges.keys():
            parent_node_id = parent_nodes[i-1].id
            break

    # if from argument contains node from other tree
    if not parent_node_id:
        for parent_node in parent_nodes:
            if 'arguments' in parent_node.graph.keys():
                if link_name in parent_node.graph['arguments'].keys():
                    if 'from_node' in parent_node.graph['arguments'][link_name]:
                        node_id = parent_node.graph['arguments'][link_name]['from_node']
                        if node_id not in forest.nodes.keys():
                            parent_node_id = from_node(forest, node_id)
                        else:
                            parent_node_id = node_id
                        break

    return parent_node_id


# TODO: should this be a class function?
def update_sub_graphs(forest):
    for edge in forest.edges.values():
        same_tree = forest.tree_ids[edge.node_ids[0]] == forest.tree_ids[edge.node_ids[1]]
        same_stem_level = forest.levels[edge.node_ids[0]] == forest.levels[edge.node_ids[1]]
        if same_tree and not same_stem_level:
            node = forest.nodes[edge.node_ids[0]]
            node.graph['arguments'][edge.name] = {'from_node': edge.node_ids[1]}
            forest.nodes[node.id] = node

    return forest


def translate(pg_filepath):
    pg_dict = load(open(pg_filepath))
    keys_tree, _, _, _ = walkdict(pg_dict)
    # create graph and sub_graph
    nodes = OrderedDict()
    edges = OrderedDict()
    tree_ids = OrderedDict()
    branch_ids = OrderedDict()
    levels = OrderedDict()
    forest = Graph(nodes=nodes, edges=edges, levels=levels, branch_ids=branch_ids, tree_ids=tree_ids)
    # iterate over graph dictionary keys
    prev_keys_branches = []
    tree_id = 0
    for branch_id, keys_branch in enumerate(keys_tree):
        leaf_id = 0
        stem_level = -1

        branches_ignore = []
        for i in range(len(keys_branch)):
            for j, prev_keys_branch in enumerate(prev_keys_branches):
                if j not in branches_ignore:
                    if i > (len(prev_keys_branch)-1):
                        branches_ignore.append(j)
                    elif prev_keys_branch[i] != keys_branch[i]:
                        branches_ignore.append(j)
            if len(branches_ignore) == len(prev_keys_branches):
                break
            stem_level = i

        if stem_level == -1:  # branches have a different root -> new tree
            tree_id += 1
            prev_keys_branches = [keys_branch]
        else:
            prev_keys_branches.append(keys_branch)

        for i, key in enumerate(keys_branch):
            parent_keys = keys_branch[:(i+1)]
            idx_str = ''
            for parent_key in parent_keys:
                idx_str += "['{}']".format(parent_key)
            sub_pg_dict = copy.deepcopy(eval('pg_dict' + idx_str))
            if 'arguments' in sub_pg_dict.keys():
                #leaf_id += 1
                if i < stem_level:
                    continue

                if key == 'callback':
                    node_id = "_".join(["C", str(tree_id), str(branch_id), str(i)])
                    node_name = node_id
                    node = Node(id=node_id, name=node_name, graph=sub_pg_dict)
                else:
                    node_id = "_".join([key, str(tree_id), str(branch_id), str(i)])
                    node_name = key
                    node = Node(id=node_id, name=node_name, graph=sub_pg_dict)

                # create edge
                if 'callback' in parent_keys:
                    links = create_links(parent_keys)
                    parent_nodes = find_parent_leafs(forest, tree_id, links, i)
                    parent_node = parent_nodes[-1]
                    edge_name = links[-1]
                    edge_id = "{}__{}__{}".format(parent_node.id, edge_name, node.id)
                    edge = Edge(id=edge_id, name=edge_name, nodes=[parent_node, node])
                    forest.edges[edge_id] = edge


                # add and tag node in graph
                forest.nodes[node_id] = node
                forest.levels[node_id] = i
                forest.tree_ids[node_id] = tree_id
                forest.branch_ids[node_id] = branch_id

                for arg_key in sub_pg_dict['arguments'].keys():
                    sub_pg_args = sub_pg_dict['arguments'][arg_key]
                    if type(sub_pg_args) != list:
                        sub_pg_args = [sub_pg_args]
                    for l, sub_pg_arg in enumerate(sub_pg_args):
                        if type(sub_pg_arg) != dict:
                            continue
                        parent_node_id = None
                        if 'from_node' in sub_pg_arg.keys():
                            parent_node_name = sub_pg_arg['from_node']
                            parent_node_id = from_node(forest, parent_node_name)
                            if len(sub_pg_args) == 1:
                                sub_pg_dict['arguments'][arg_key]['from_node'] = parent_node_id
                            else:
                                sub_pg_dict['arguments'][arg_key][l]['from_node'] = parent_node_id
                        elif 'from_argument' in sub_pg_arg.keys():
                            parent_arg_name = sub_pg_dict['arguments'][arg_key]['from_argument']
                            links = create_links(parent_keys)
                            parent_node_id = from_argument(forest, tree_id, links, parent_arg_name, i)
                            if len(sub_pg_args) == 1:
                                sub_pg_dict['arguments'][arg_key] = {'from_node': parent_node_id}
                            else:
                                sub_pg_dict['arguments'][arg_key][l] = {'from_node': parent_node_id}

                        if parent_node_id:
                            forest.nodes[node_id].graph = sub_pg_dict
                            # create edge
                            parent_node = forest.nodes[parent_node_id]
                            edge_id = "{}__{}__{}".format(parent_node.id, arg_key, node.id)
                            edge_name = arg_key
                            edge = Edge(id=edge_id, name=edge_name, nodes=[parent_node, node])
                            forest.edges[edge_id] = edge

    forest = update_sub_graphs(forest)

    return forest

if __name__ == '__main__':
    #test_dict = {'a': {'b': {'c': 3}, 'd': {'e': 4}}, 'd': 9, 'g': {'f': 3, 't': {'h': {'z': 5}}}}
    #keys_tree, _, _, _ = walkdict(test_dict)
    pass
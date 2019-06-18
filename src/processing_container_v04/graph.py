import copy
from pprint import pformat
from collections import OrderedDict


class Node(object):
    def __init__(self, id=None, name=None, graph=None, edges=None):
        self.id = id
        self.name = name
        self.graph = graph
        self.edges = edges

    def __str__(self):
        pg_str = pformat(self.graph)
        repr_str = "Node ID: {} \nNode Name: {} \n{}".format(self.id, self.name, pg_str)

        return repr_str

    def relatives(self, link, ancestor=True):
        idx = 1
        idx_other = 0
        if not ancestor:
            idx = 0
            idx_other = 1

        relatives = []
        for edge in self.edges:
            if edge.name == link and edge.nodes[idx].id == self.id:
                relatives.append(edge.nodes[idx_other])

        return relatives

    def parent(self, link):
        ancestors = self.ancestors(link)
        num_ancestors = len(ancestors)
        if num_ancestors > 1:
            raise Exception('Child nodes are restricted to only have one parent node.')
        elif num_ancestors == 0:
            return None
        else:
            return ancestors[0]

    def child(self, link):
        descendants = self.descendants(link)
        num_descendants = len(descendants)
        if num_descendants > 1:
            raise Exception('Parent nodes are restricted to only have one child node.')
        elif num_descendants == 0:
            return None
        else:
            return descendants[0]

    def descendants(self, link):
        relatives = self.relatives(link, ancestor=False)
        return relatives

    def ancestors(self, link):
        relatives = self.relatives(link, ancestor=True)
        return relatives

    @property
    def dependencies(self):
        dependencies = []
        for edge in self.edges:
            if self.id == edge.nodes[1].id:
                dependencies.append(edge.nodes[0])

        return dependencies

    def add_edge(self, edge):
        add_egde = True
        for edge_this in self.edges:
            if edge_this == edge:
                add_egde = False

        if add_egde:
            self.edges.append(edge)


class Edge(object):
    def __init__(self, id=None, name=None, nodes=None):
        self.id = id
        self.name = name
        self.nodes = nodes

    @property
    def node_ids(self):
        return [node.id for node in self.nodes]

    def __eq__(self, other):
        return (self.nodes[0].id == other.nodes[0].id) & \
               (self.nodes[1].id == other.nodes[1].id) & \
               (self.name == other.name)


class Graph(object):
    def __init__(self, nodes):
        self.nodes = nodes

    @property
    def nnodes(self):
        return len(self.nodes)

    @property
    def ids(self):
        return self.nodes.keys()

    def __str__(self):
        repr_str = ""
        for node in self.nodes.values():
            repr_str_per_node = str(node) + "\n\n"
            repr_str += repr_str_per_node

        return repr_str

    def node_lineage(self, node, link=None, ancestors=True):
        idx = 1
        idx_other = 0
        if not ancestors:
            idx = 0
            idx_other = 1

        nodes_lineage = []
        nodes_current = [node]
        while True:
            nodes_other = []
            for node_current in nodes_current:
                edges = [edge for edge in node_current.edges
                         if (edge.name == link) and (edge.nodes[idx].id == node_current.id)]
                nodes_other.extend([edge.nodes[idx_other] for edge in edges])
            nodes_current = copy.deepcopy(nodes_other)  # TODO: is a deepcopy needed?

            if not nodes_current:
                break
            else:
                nodes_lineage.extend(nodes_current)

        return nodes_lineage

    # TODO: this needs to be refactored, it would be good to have the same functionality for parent and none parent nodes
    def nodes_at_same_level(self, node, link=None, include_node=True):
        nodes = []
        child_node = node.child(link)
        for node_other in self.nodes.values():
            if node_other.id != node.id:
                child_node_other = node_other.child(link)
                if child_node and child_node_other and (child_node_other.id == child_node.id):
                    nodes.append(node_other)
                elif not child_node and not child_node_other:
                    nodes.append(node_other)

        if include_node:
            nodes.append(node)

        return nodes

    # def node_children(self, node, link=None):
    #     children = []
    #     for node_other in self.nodes.values():
    #         if node.id != node_other.id:
    #             node_parent = node_other.parent(link=link)
    #             if node_parent and (node_parent.id == node.id):
    #                 children.append(node_other)
    #
    #     return children

    def order(self, by=None):

        if by == "dependency":
            nodes = self.nodes.values()
            nodes_ordered = []
            for node in nodes:
                insert_idx = 0
                for node_dependency in node.dependencies:
                    for idx, node_ordered in enumerate(nodes_ordered):
                        if (idx >= insert_idx) and (node_dependency.id == node_ordered.id):
                            insert_idx = idx + 1  # place the node after the dependency
                nodes_ordered.insert(insert_idx, node)

            self.nodes = OrderedDict()
            for node_ordered in nodes_ordered:
                self.nodes[node_ordered.id] = node_ordered

    def update(self):
        for node in self.nodes.values():
            for edge in node.edges:
                for i, edge_node in enumerate(edge.nodes):
                    if edge_node.id != node.id:
                        edge_node.add_edge(edge)

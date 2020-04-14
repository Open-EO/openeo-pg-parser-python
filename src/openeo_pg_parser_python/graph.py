import copy
from pprint import pformat
from collections import OrderedDict


class Node:
    """
    A node of a graph, containing information about its edges, an ID, a name and a sub-graph/dictionary.
    """
    def __init__(self, id=None, name=None, content=None, edges=None):
        """
        Constructor of `graph.Node`.

        Parameters
        ----------
        id : int or str, optional
            An ID for finding a node in a graph.
        name : str, optional
            Name of the node.
        content : dictionary or object, optional
            A sub-graph/dictionary (e.g., sub process graph in openEO) or an arbitrary object representing the
            information/content stored in a node.
        edges : list of graph.Edge
            List containing all edges related to this node.
        """

        self.id = id
        self.name = name
        self.content = content
        self.edges = edges

    def __str__(self):
        """
        String representation of this class, i.e.,
        the ID, the name and the content are converted to a string.

        Returns
        -------
        str
        """

        pg_str = pformat(self.content)
        repr_str = "Node ID: {} \nNode Name: {} \n{}".format(self.id, self.name, pg_str)

        return repr_str

    def relatives(self, link, ancestor=True):
        """
        Finds direct relatives of the node, i.e. parents or children.

        Parameters
        ----------
        link : str
            Link/edge name connecting two nodes.
        ancestor : bool, optional
            If true, all ancestors/parents are returned (default).
            If false, all descendants/children are returned.

        Returns
        -------
        graph.Graph
        """

        idx = 1
        idx_other = 0
        if not ancestor:
            idx = 0
            idx_other = 1

        relatives = []
        for edge in self.edges:
            if edge.name == link and edge.nodes[idx].id == self.id:
                relatives.append(edge.nodes[idx_other])

        return Graph.from_list(relatives)

    def parent(self, link):
        """
        Returns parent node.

        Parameters
        ----------
        link : str
            Link/edge name connecting two nodes.

        Returns
        -------
        graph.Node

        Notes
        -----
        Only one node is allowed as a parent.
        """

        ancestors = self.ancestors(link)
        num_ancestors = len(ancestors)
        if num_ancestors > 1:
            raise Exception('Child nodes are restricted to only have one parent node.')
        elif num_ancestors == 0:
            return None
        else:
            return ancestors[0]

    def child(self, link):
        """
        Returns child node.

        Parameters
        ----------
        link : str
            Link/edge name connecting two nodes.

        Returns
        -------
        graph.Node

        Notes
        -----
        Only one node is allowed as a child.
        """
        descendants = self.descendants(link)
        num_descendants = len(descendants)
        if num_descendants > 1:
            raise Exception('Parent nodes are restricted to only have one child node.')
        elif num_descendants == 0:
            return None
        else:
            return descendants[0]

    def descendants(self, link):
        """
        Returns all descendants/childs with the specified linkage as a graph.

        Parameters
        ----------
        link : str
            Link/edge name connecting two nodes.

        Returns
        -------
        graph.Graph
        """

        return self.relatives(link, ancestor=False)

    def ancestors(self, link):
        """
        Returns all ancestors/parents with the specified linkage as a graph.

        Parameters
        ----------
        link : str
            Link/edge name connecting two nodes.

        Returns
        -------
        graph.Graph
        """

        return self.relatives(link, ancestor=True)

    def add_edge(self, edge):
        """
        Adds an edge to the node if not already given.

        Parameters
        ----------
        edge : graph.Edge
            Edge connecting two nodes.

        Returns
        -------
        graph.Node
        """

        add_egde = True
        for edge_this in self.edges:
            if edge_this == edge:
                add_egde = False

        if add_egde:
            self.edges.append(edge)

        return self


class Edge(object):
    """ An edge connects two nodes. The connection has a label/name. """

    def __init__(self, id=None, name=None, nodes=None):
        """
        Constructor of `graph.Edge`.

        Parameters
        ----------
        id : int or str, optional
            An ID for finding an edge/connection in a graph.
        name : str, optional
            Name of the edge/connection.
        nodes : list of graph.Nodes, optional
            List containing two nodes comprising an edge.
        """

        if nodes is not None:
            n_nodes = len(nodes)
            if n_nodes != 2:
                err_msg = "Only 2 nodes are allowed for one edge ({} given).".format(n_nodes)
                raise ValueError(err_msg)

        self.id = id
        self.name = name
        self.nodes = nodes

    @property
    def node_ids(self):
        """ list : Returns the node ID's of the two edge nodes. """
        return [node.id for node in self.nodes]

    def __eq__(self, other):
        """
        Checks if two edges are equal, i.e. if the nodes and their order are the same.

        Parameters
        ----------
        other : graph.Edge
            Edge to compare with.

        Returns
        -------
        bool
            True if two edges are equal.
        """

        return (self.nodes[0].id == other.nodes[0].id) & \
               (self.nodes[1].id == other.nodes[1].id) & \
               (self.name == other.name)


class Graph(object):
    """ Represents an arbitrary graph containing `graph.Node` instances as nodes. """

    def __init__(self, nodes):
        """
        Constructor for `Graph` class.

        Parameters
        ----------
        nodes : collections.OrderedDict
            Dictionary containing node ID's as keys and `graph.Node` objects as values.
        """

        self.nodes = nodes

    @classmethod
    def from_list(cls, nodes):
        """
        Initialises a `Graph` object from a list of nodes.

        Parameters
        ----------
        nodes : list
            List of `graph.Node` instances.

        Returns
        -------
        Graph
        """

        nodes_dict = OrderedDict()
        for node in nodes:
            nodes_dict[node.id] = node

        return cls(nodes_dict)

    @property
    def ids(self):
        """ view : view on Node ID's """
        return self.nodes.keys()

    def __len__(self):
        """ int : number of nodes in the graph. """
        return len(self.nodes)

    def __getitem__(self, item):
        """
        Returns node at the given index.

        Parameters
        ----------
        item : int
            Index of node in graph.

        Returns
        -------
        graph.Node
        """

        if item in self.nodes.keys():
            return self.nodes[item]
        else:
            if isinstance(item, int):
                return list(self.nodes.values())[item]
            else:
                err_msg = "'{}' is not a valid key.".format(item)
                raise KeyError(err_msg)

    def __str__(self):
        """ str : string version of the class, i.e., creates a multi-line string from all nodes.  """

        repr_str = ""
        for node in self.nodes.values():
            repr_str_per_node = str(node) + "\n\n"
            repr_str += repr_str_per_node

        return repr_str

    def get_node_by_name(self, name):
        """
        Returns first node matching the given name.

        Parameters
        ----------
        name : str
            Name of the node.

        Returns
        -------
        graph.Node
        """

        for node in self.nodes.values():
            if node.name == name:
                return node

        return None

    def lineage(self, node, link=None, ancestors=True, level=None):
        """
        Finds all nodes following a specific lineage in the graph/family tree.

        node : graph.Node
            Starting node of lineage search.
        link : str, optional
            Link/edge name connecting two nodes.
        ancestors : bool, optional
            If true, search is proceeded for all ancestors (default).
            If false, search is proceeded for all descendants.
        level : int, optional


        Returns
        -------
        graph.Graph
        """

        idx = 1
        idx_other = 0
        if not ancestors:
            idx = 0
            idx_other = 1

        lineage_nodes = []
        current_nodes = [node]
        while True:
            other_nodes = []
            for node_current in current_nodes:
                edges = [edge for edge in node_current.edges
                         if (edge.name == link) and (edge.nodes[idx].id == node_current.id)]
                other_nodes.extend([edge.nodes[idx_other] for edge in edges])
            current_nodes = copy.deepcopy(other_nodes)

            if not current_nodes:
                break
            else:
                lineage_nodes.extend(current_nodes)

        return Graph.from_list(lineage_nodes)

    def find_siblings(self, node, link=None, include_node=True):
        """
        Finds all nodes on the same level, i.e. which have the same parent.

        Parameters
        ----------
        node : graph.Node
            Node for searching its siblings.
        link : str, optional
            Link/edge name connecting two nodes.
        include_node : bool, optional
            If true, the given node is added to its siblings (default is True).

        Returns
        -------
        graph.Graph
        """

        nodes = []
        parent_node = node.parent(link)
        for node_other in self.nodes.values():
            if node_other.id != node.id:
                parent_node_other = node_other.parent(link)
                if parent_node and parent_node_other and (parent_node_other.id == parent_node.id):
                    nodes.append(node_other)
                elif not parent_node and not parent_node_other:
                    nodes.append(node_other)

        if include_node:
            nodes.append(node)

        return Graph.from_list(nodes)

    def sort(self, by='dependency'):
        """
        Sorts graph according to sorting strategy.

        Parameters
        ----------
        by : str
            Sorting strategy:
                - 'dependency': Sorts graph by each node dependency,
                                i.e., nodes being dependent on another node come after this node.

        Returns
        -------
        graph.Graph
            Sorted graph.
        """

        nodes_ordered = []
        if by == "dependency":
            nodes = self.nodes.values()
            for node in nodes:
                insert_idx = 0
                for node_dependency in node.dependencies:
                    for idx, node_ordered in enumerate(nodes_ordered):
                        if (idx >= insert_idx) and (node_dependency.id == node_ordered.id):
                            insert_idx = idx + 1  # place the node after the dependency
                nodes_ordered.insert(insert_idx, node)
        else:
            err_msg = "Sorting strategy '{}' unknown ".format(by)
            raise ValueError(err_msg)

        return Graph.from_list(nodes_ordered)

    def update(self):
        """
        Updates all edges and their nodes in a graph.

        Returns
        -------
        graph.Graph
            Updated graph with linked nodes.
        """

        for node in self.nodes.values():
            for edge in node.edges:
                for i, edge_node in enumerate(edge.nodes):
                    if edge_node.id != node.id:
                        edge_node.add_edge(edge)

        return self

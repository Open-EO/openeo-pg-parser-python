import copy
import numpy as np
from pprint import pformat
from collections import OrderedDict
from openeo_pg_parser_python.definitions import OpenEOProcess


class Node:
    """
    A node of a graph, containing information about its edges, an ID, a name and a sub-graph/dictionary.
    """
    def __init__(self, id=None, name=None, content=None, edges=None, depth=None):
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
        depth : int, optional
            Stores depth level if the node is in a hierarchical graph.
        """

        self.id = id
        self.name = name
        self.content = content
        self.edges = edges
        self.depth = depth

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

    @property
    def dependencies(self):
        """ graph.Graph : Direct dependencies of this node. """

        return self.ancestors()

    def relatives(self, link=None, ancestor=True):
        """
        Finds direct relatives of the node, i.e. parents or children.

        Parameters
        ----------
        link : str, optional
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
            if edge.nodes[idx].id == self.id:
                if link is not None and edge.name == link:
                    relatives.append(edge.nodes[idx_other])
                elif link is None:
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

    def descendants(self, link=None):
        """
        Returns all descendants/childs with the specified linkage as a graph.

        Parameters
        ----------
        link : str, optional
            Link/edge name connecting two nodes.

        Returns
        -------
        graph.Graph
        """

        return self.relatives(link=link, ancestor=False)

    def ancestors(self, link=None):
        """
        Returns all ancestors/parents with the specified linkage as a graph.

        Parameters
        ----------
        link : str, optional
            Link/edge name connecting two nodes.

        Returns
        -------
        graph.Graph
        """

        return self.relatives(link=link, ancestor=True)

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

    def __eq__(self, other):
        """ bool : Checks if two nodes are equal. """
        return self.id == other.id


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

        self._nodes = nodes

    @property
    def nodes(self):
        """ View : Returns all nodes in the graph as a view. """
        return self._nodes.values()

    @property
    def ids(self):
        """ view : View on Node ID's. """
        return self._nodes.keys()

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

        if item in self.ids:
            return self._nodes[item]
        else:
            if isinstance(item, int):
                return list(self.nodes)[item]
            else:
                err_msg = "'{}' is not a valid key.".format(item)
                raise KeyError(err_msg)

    def __str__(self):
        """ str : string version of the class, i.e., creates a multi-line string from all nodes.  """

        repr_str = ""
        for node in self.nodes:
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

        for node in self.nodes:
            if node.name == name:
                return node

        return None

    def lineage(self, node, link=None, ancestors=True):
        """
        Finds all nodes following a specific lineage in the graph/family tree.

        node : graph.Node
            Starting node of lineage search.
        link : str, optional
            Link/edge name connecting two nodes.
        ancestors : bool, optional
            If true, search is proceeded for all ancestors (default).
            If false, search is proceeded for all descendants.

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
        for node_other in self.nodes:
            if node_other.id != node.id:
                parent_node_other = node_other.parent(link)
                if parent_node and parent_node_other and (parent_node_other.id == parent_node.id):
                    nodes.append(node_other)
                elif not parent_node and not parent_node_other:
                    nodes.append(node_other)

        if include_node:
            nodes.append(node)

        return Graph.from_list(nodes)

    def find_partners(self, node, link=None, include_node=True):
        """
        Finds all nodes on the same level, i.e. which have the same child.

        Parameters
        ----------
        node : graph.Node
            Node for searching its partners.
        link : str, optional
            Link/edge name connecting two nodes.
        include_node : bool, optional
            If true, the given node is added to its partners (default is True).

        Returns
        -------
        graph.Graph
        """

        nodes = []
        child_node = node.child(link)
        for node_other in self.nodes:
            if node_other.id != node.id:
                child_node_other = node_other.child(link)
                if child_node and child_node_other and (child_node_other.id == child_node.id):
                    nodes.append(node_other)
                elif not child_node and not child_node_other:
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
            for node in self.nodes:
                insert_idx = 0
                for node_dependency in node.dependencies:
                    for idx, node_ordered in enumerate(nodes_ordered):
                        if (idx >= insert_idx) and (node_dependency.id == node_ordered.id):
                            insert_idx = idx + 1  # place the node after the dependency
                nodes_ordered.insert(insert_idx, node)
        elif by == "depth":
            depths = [node.depth for node in self.nodes]
            order = np.argsort(depths)
            nodes_ordered = np.array(list(self.nodes))[order].tolist()
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

        for node in self.nodes:
            for edge in node.edges:
                for i, edge_node in enumerate(edge.nodes):
                    if edge_node.id != node.id:
                        edge_node.add_edge(edge)

        return self



class OpenEONode(Node):
    """
    A node of an openEO process graph, containing information about its edges, an ID, a name, its arguments,
    a description and so on.

    """

    def __init__(self, id=None, name=None, content=None, edges=None, depth=None, processes_src=None):
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
        depth : int, optional
            Stores depth level if the node is in a hierarchical graph.
        processes_src : dict or str or list, optional
            It can be:
                - dictionary of loaded process definitions (keys are the process ID's)
                - directory path to processes (.json)
                - URL of the remote process endpoint (e.g., "https://earthengine.openeo.org/v1.0/processes")
                - list of loaded process definitions

        """
        super().__init__(id=id, name=name, content=content, edges=edges, depth=depth)

        self.process = OpenEOProcess.from_name(self.process_id, src=processes_src)

    @property
    def process_id(self):
        """ str : returns the process ID of an openEO process. """
        return None if self.content is None else self.content['process_id']

    @property
    def arguments(self):
        """ dict : returns the arguments of an openEO process. """

        if self.content is not None:
            exp_args = self.process.parameters
            args = copy.deepcopy(self.content['arguments'])
            for exp_arg_name in exp_args.keys():
                if exp_arg_name not in args.keys():
                    args[exp_arg_name] = exp_args[exp_arg_name]
            return args
        else:
            return None

    @property
    def dependencies(self):
        """ graph.Graph : Direct dependencies of this node. """
        data_dependencies = list(self.ancestors(link="data").nodes)  # get input data nodes
        callback_dependencies = [node for node in self.ancestors(link="callback").nodes
                                 if node.is_result]  # get input callback node, where node is a result node

        return Graph.from_list(data_dependencies + callback_dependencies)

    @property
    def parent_process(self):
        """ list of graph.Node : Returns the parent process node. """
        parents = self.descendants("callback")
        if len(parents) > 1:
            err_msg = "Only one parent process is allowed."
            raise Exception(err_msg)
        else:
            return parents[0] if len(parents) == 1 else None

    @property
    def child_processes(self):
        """ list of graph.Node : Returns the child process nodes. """
        return self.ancestors("callback")

    @property
    def description(self):
        """ str : returns the description of an openEO process. """
        return self.content['description'] \
            if (self.content is not None) and ('description' in self.content.keys()) else None

    @property
    def is_result(self):
        """ bool : returns the result value of an openEO process, i.e. if this node is a result node or not. """
        is_result = False
        if (self.content is not None) and ("result" in self.content.keys()):
            is_result = self.content['result']

        return is_result

    @property
    def is_reducer(self):
        """ bool : Checks if the current process is a reducer or not. """
        return self.process.is_reducer

    @property
    def dimension(self):
        """ str : Returns the dimension over which is reduced if the process is a reducer. """
        if self.is_reducer:
            if 'dimension' in self.arguments.keys():
                return self.arguments['dimension']
            else:
                return self.parent_process.dimension
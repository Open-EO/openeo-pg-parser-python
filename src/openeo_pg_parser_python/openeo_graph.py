import os
from json import load
from openeo_pg_parser_python.utils import load_processes
from openeo_pg_parser_python.graph import Node

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
            args = self.content['arguments']
            for exp_arg_name in exp_args.keys():
                if exp_arg_name not in args.keys():
                    args[exp_arg_name] = exp_args[exp_arg_name]
            return args
        else:
            return None

    @property
    def parent_process(self):
        """ list of graph.Node : Returns the parent process node. """
        parents = self.descendants("callback")
        if len(parents) > 1:
            err_msg = "Only one parent process is allowed."
            raise Exception(err_msg)
        else:
            return parents[0]

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
            return self.arguments['dimension']



class OpenEOProcess:
    """ Class representing an OpenEO process definition. """
    def __init__(self, process_def):
        """
        Constructor of `OpenEOProcess` class.

        Parameters
        ----------
        process_def : dict
            A dictionary defining an openEO process definition/schema.

        """
        self.definition = process_def

    @classmethod
    def from_file(cls, filepath):
        """
        Creates an `OpenEOProcess` instance from a process definition (JSON) file.

        Parameters
        ----------
        filepath : str
            Full filepath to the process definition (JSON) file.

        Returns
        -------
        OpenEOProcess

        """
        if os.path.splitext(filepath)[1] != 'json':
            err_msg = "The given file must be a json file."
            raise IOError(err_msg)

        process_def = load(filepath)
        return cls(process_def)

    @classmethod
    def from_name(cls, name, src=None):
        """
        Creates an `OpenEOProcess` instance from an process name/ID.

        Parameters
        ----------
        name : str
            The name of the process, i.e. its ID.
        src : dict or str or list, optional
            It can be:
                - dictionary of loaded process definitions (keys are the process ID's)
                - directory path to processes (.json)
                - URL of the remote process endpoint (e.g., "https://earthengine.openeo.org/v1.0/processes")
                - list of loaded process definitions

        Returns
        -------
        OpenEOProcess

        """

        # use standard directory
        if src is None:
            src = os.path.join("..", "..", "processes")

        processes = load_processes(src)

        if name not in processes.keys():
            err_msg = "Process '{}' could not be found in the list of processes.".format(name)
            raise ValueError(err_msg)
        else:
            return cls(processes[name])

    @property
    def id(self):
        """ str : ID/name of the process. """
        return self.definition['id']

    @property
    def description(self):
        """ str : Description of the process. """
        return self.definition['description'] if self._has_description else None

    @property
    def parameters(self):
        """
        dict : Dictionary containing the process argument names as keys and parameter definitions
        (`OpenEOParameter` instances) as values.

        """
        parameters = {}
        for param_def in self.definition['parameters']:
            parameter = OpenEOParameter(param_def)
            parameters[parameter.name] = parameter

        return parameters

    @property
    def is_reducer(self):
        """ bool : Checks if the current process is a reducer or not. """
        return self._has_categories and "reducer" in self.definition["categories"]

    @property
    def returns(self):
        """ dict : Returns 'return' schema of the process. """
        return self.definition['returns']

    @property
    def exceptions(self):
        """ dict : Returns 'exceptions' schema of the process. """
        return self.definition['exceptions'] if self._has_exceptions else None

    @property
    def process_graph(self):
        """ dict : Returns 'process_graph' schema of the process. """
        return self.definition['process_graph'] if self._has_process_graph else None

    @property
    def _has_description(self):
        """ bool : Checks if the process has a description ('description'). """
        return "description" in self.definition.keys()

    @property
    def _has_categories(self):
        """ bool : Checks if the process has categories ('categories'). """
        return "categories" in self.definition.keys()

    @property
    def _has_process_graph(self):
        """ bool : Checks if the process has an alternative process graph ('process_graph'). """
        return "process_graph" in self.definition.keys()

    @property
    def _has_exceptions(self):
        """ bool : Checks if the process has exceptions ('exceptions'). """
        return "exceptions" in self.definition.keys()


class OpenEOParameter:
    """ Class representing an OpenEO parameter definition. """

    def __init__(self, param_def):
        """
        Constructor of `OpenEOParameter` class.

        Parameters
        ----------
        param_def : dict
            A dictionary defining an openEO parameter schema.

        """
        self.definition = param_def

    @property
    def name(self):
        """ str : Name of the parameter. """
        return self.definition['name']

    @property
    def is_optional(self):
        """ bool : Name of the parameter. """
        return self.definition['optional'] if self._has_optional else False

    @property
    def default_value(self):
        """ object : Default value/s of the paramter. """
        return self.definition['default'] if self._has_default else None

    @property
    def _has_default(self):
        """ bool : Checks if 'default' argument is given. """
        return 'default' in self.definition.keys()

    @property
    def _has_optional(self):
        """ bool : Checks if default 'optional' argument is given. """
        return 'optional' in self.definition.keys()
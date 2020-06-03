import os
from json import load
from openeo_pg_parser_python.utils import load_processes


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
        self.sub_process = None

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

            if "parameters" in parameter.schema:  # check if this condition fulfills all needs
                self.sub_process = OpenEOProcess(parameter.schema)

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
    def schema(self):
        """ dict : Parameter schema. """
        return self.definition['schema']

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
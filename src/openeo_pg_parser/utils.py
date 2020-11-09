import os
import glob
import requests
from json import load

def url_is_valid(url):
    """
    Very simple check if URL exists/is valid or not.

    Parameters
    ----------
    url : str
        URL to validate.

    Returns
    -------
    bool

    """
    try:
        r = requests.get(url=url)
        if r.status_code != 200:
            return False
        return True
    except:
        return False


def load_json_file(filepath):
    """
    Loads json file as dictionary.

    Parameters
    ----------
    filepath : str
        Full file path to JSON file.

    Returns
    -------
    dict

    """
    with open(filepath) as file:
        return load(file)


def load_processes(src):
    """
    Collects process definitions from a local process directory, from a URL or a list of process definitions.

    Parameters
    ----------
    src : dict or str or list, optional
            It can be:
                - dictionary of loaded process definitions (keys are the process ID's)
                - directory path to processes (.json)
                - URL of the remote process endpoint (e.g., "https://earthengine.openeo.org/v1.0/processes")
                - list of loaded process definitions

    Returns
    -------
    dict :
        Dictionary linking process IDs with the respective process definitions.

    Notes
    -----
    When an URL is given, this function downloads the process specifications from the overview endpoint.

    """

    if isinstance(src, dict):
        processes = src
    else:
        if isinstance(src, str) and os.path.isdir(src):
            filepaths = glob.glob(os.path.join(src, "*.json"))
            process_list = [load_json_file(filepath) for filepath in filepaths]
        elif isinstance(src, str) and url_is_valid(src):
            r = requests.get(url=src)
            data = r.json()
            process_list = data['processes']
        elif isinstance(src, list):
            process_list = src
        else:
            err_msg = "Either a processes URL or a local directory path must be specified."
            raise ValueError(err_msg)

        processes = {}
        for process in process_list:
            processes[process['id']] = process

    return processes


def load_collections(src, collection_ids=None):
    """
    Collects collection definitions from a local collections directory, from a URL or a list of collection
    definitions.

    Parameters
    ----------
    src : dict or str or list, optional
        It can be:
            - dictionary of loaded collection definitions (keys are the collection ID's)
            - directory path to collections (.json)
            - URL of the remote collection endpoint (e.g., "https://earthengine.openeo.org/v1.0/collections")
            - list of loaded collection definitions
    collection_ids : list of str, optional
        List of collection ID's used when an URL is given as a source.

    Returns
    -------
    dict :
        Dictionary linking collection IDs with the respective collection definitions.

    Notes
    -----
    When an URL is given, this function downloads the collections from each exact collection endpoint.
    Note that downloading all collections can take quite some time.

    """

    if isinstance(src, dict):
        collections = src
    else:
        if isinstance(src, str) and os.path.isdir(src):
            filepaths = glob.glob(os.path.join(src, "*.json"))
            collection_list = [load_json_file(filepath) for filepath in filepaths]
        elif isinstance(src, str) and url_is_valid(src):
            if not collection_ids:
                r = requests.get(url=src)
                data = r.json()
                collection_ids = [collection['id'] for collection in data['collections']]
            collection_list = []
            for collection_id in collection_ids:
                collection_url = src + "/" + collection_id
                r = requests.get(url=collection_url)
                collection_list.append(r.json())
        elif isinstance(src, list):
            collection_list = src
        else:
            err_msg = "Either a collections URL or a local directory path must be specified."
            raise ValueError(err_msg)

        collections = {}
        for collection in collection_list:
            collections[collection['id']] = collection

    return collections


def walk_process_dictionary(proc_dict, keys_lineage=None, key_lineage=None, level=0, prev_level=0,
                            break_points=None):
    """
    Recursively walks through a dictionary until the specified key is reached and collects the keys lineage/the keys.

    Parameters
    ----------
    proc_dict : dict
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
    break_points : list, optional
        List of strings/keys in the dictionary, where the recursive process should stop.

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

    if isinstance(proc_dict, dict):
        for k, v in proc_dict.items():
            if break_points and k in break_points:  # ignore further arguments
                break
            key_lineage.append(k)
            sub_pg_graph = proc_dict[k]
            level += 1
            prev_level = level
            keys_lineage, key_lineage, level, prev_level = walk_process_dictionary(sub_pg_graph, keys_lineage=keys_lineage,
                                                                                   key_lineage=key_lineage, level=level,
                                                                                   prev_level=prev_level,
                                                                                   break_points=break_points)
    elif isinstance(proc_dict, list):
        for i, elem in enumerate(proc_dict):
            key_lineage.append(i)
            sub_pg_graph = proc_dict[i]
            level += 1
            prev_level = level
            keys_lineage, key_lineage, level, prev_level = walk_process_dictionary(sub_pg_graph, keys_lineage=keys_lineage,
                                                                                   key_lineage=key_lineage, level=level,
                                                                                   prev_level=prev_level,
                                                                                   break_points=break_points)

    level -= 1
    if key_lineage and (key_lineage not in keys_lineage):
        if (level - prev_level) == -1:
            keys_lineage.append(key_lineage)
        key_lineage = key_lineage[:-1]

    return keys_lineage, key_lineage, level, prev_level


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

    if len(keys) > 1:
        return get_obj_elem_from_keys(obj[keys[0]], keys[1:])
    else:
        return obj[keys[0]]


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

    if len(keys) > 1:
        return set_obj_elem_from_keys(obj[keys[0]], keys[1:], value)
    else:
        obj[keys[0]] = value


def find_node_inputs(node, data_link):
    """
    Find input node IDs corresponding to a given linkage for a sub process graph.

    Parameters
    ----------
    node : openEONode
        Node of interest.
    data_link : str
        Linkage name, e.g. "from_node" or "from_parameter".

    Returns
    -------
    keys_lineage : list of lists
        Adjusted keys indexes/lineage to go from the sub process graph to input node ID.
    """

    keys_lineage = []
    for key, value in node.arguments.items():
        keys_lineage_arg, _, _, _ = walk_process_dictionary(value, break_points=["process_graph"])
        if keys_lineage_arg:
            keys_lineage.extend([[key] + elem for elem in keys_lineage_arg if elem[-1] == data_link])

    return keys_lineage



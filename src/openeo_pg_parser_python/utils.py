import os
import glob
import requests
from json import load

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

    """

    if isinstance(src, dict):
        processes = src
    else:
        if isinstance(src, str) and os.path.isdir(src):
            filepaths = glob.glob(os.path.join(src, "*.json"))
            process_list = [load(open(filepath)) for filepath in filepaths]
        elif isinstance(src, str):
            r = requests.get(url=src)
            if r.status_code == 200:
                data = r.json()
                process_list = data['processes']
            else:
                err_msg = "The specified URL is wrong."
                raise ValueError(err_msg)
        elif isinstance(src, list):
            process_list = src
        else:
            err_msg = "Either a processes URL or a local directory path must be specified."
            raise ValueError(err_msg)

        processes = {}
        for process in process_list:
            processes[process.id] = process

    return processes


def load_collections(src):
    """
    Collects collection definitions from a local process directory, from a URL or a list of collection
    definitions.

    Parameters
    ----------
    src : dict or str or list, optional
            It can be:
                - dictionary of loaded collection definitions (keys are the collection ID's)
                - directory path to collections (.json)
                - URL of the remote collection endpoint (e.g., "https://earthengine.openeo.org/v1.0/collections")
                - list of loaded collection definitions

    Returns
    -------
    dict :
        Dictionary linking collection IDs with the respective collection definitions.

    """

    if isinstance(src, dict):
        collections = src
    else:
        if isinstance(src, str) and os.path.isdir(src):
            filepaths = glob.glob(os.path.join(src, "*.json"))
            collection_list = [load(open(filepath)) for filepath in filepaths]
        elif isinstance(src, str):
            r = requests.get(url=src)
            if r.status_code == 200:
                data = r.json()
                collection_list = data['collections']
            else:
                err_msg = "The specified URL is wrong."
                raise ValueError(err_msg)
        elif isinstance(src, list):
            collection_list = src
        else:
            err_msg = "Either a collections URL or a local directory path must be specified."
            raise ValueError(err_msg)

        collections = {}
        for collection in collection_list:
            collections[collection.id] = collection

    return collections
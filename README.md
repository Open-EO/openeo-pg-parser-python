# openeo-pg-parser-python

This package allows to parse an *openEO* process graph (JSON) to a traversable Python object (`graph`), describing process dependencies and contents.


## Installation

### Install miniconda and clone repository

```
wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh
bash miniconda.sh -b -p $HOME/miniconda
export PATH="$HOME/miniconda/bin:$PATH"
git clone https://github.com/Open-EO/openeo-pg-parser-python.git
cd openeo-pg-parser-python
 ```

### Create the conda environment

```
conda env create -f conda_environment.yml
```

### Install package in the conda environment

```
source activate openeo-pg-parser-python
python setup.py install
```

Change 'install' with 'develop' if you plan to further develop the package.


## Example

Here, we show how an *openEO* process graph can be translated into a `graph` object.
An exemplary process graph is stored in a file named *"process_graph_example.json"* and is given below:
```json
{
  "s2a": {
    "process_id": "load_collection",
    "process_description": "Loading S2A data.",
    "arguments": {
      "id": "CGS_SENTINEL2_RADIOMETRY_V102_001",
      "spatial_extent": {
        "north": 48.40,
        "south": 47.90,
        "east": 16.84,
        "west": 15.96
      },
      "temporal_extent": ["2017-09-05", "2017-10-01"]
    }
  },
  "ndvi": {
    "process_id": "ndvi",
    "process_description": "Calculate NDVI.",
    "arguments": {
      "data": {"from_node": "s2a"},
      "name": "ndvi"
    }
  },
  "min_time": {
    "process_id": "reduce",
    "process_description": "Take the minimum value in the time series.",
    "arguments": {
      "data": {"from_node": "ndvi"},
      "dimension": "temporal",
      "reducer": {
        "callback": {
          "process_id": "min",
          "process_description": "Calculate minimum",
          "arguments": {
            "data": {"from_argument": "data"}
          },
          "result": true
        }
      }
    }
  },
  "output": {
    "process_id": "save_result",
    "description": "Save to disk",
    "arguments": {
      "data": {"from_node": "min_time"},
      "format": "Gtiff"
    }
  }
}
```
To translate the JSON file into a python object, use:
```python
from openeo_pg_parser_python.translate import translate_process_graph

pg_filepath = "process_graph_example.json"
process_graph = translate_process_graph(pg_filepath)
```
If you print the `graph` you get the information contained in each node:
```
Node ID: s2a_0
Node Name: s2a
{'arguments': {'id': 'CGS_SENTINEL2_RADIOMETRY_V102_001',
               'spatial_extent': {'east': 16.84,
                                  'north': 48.4,
                                  'south': 47.9,
                                  'west': 15.96},
               'temporal_extent': ['2017-09-05', '2017-10-01']},
 'process_description': 'Loading S2A data.',
 'process_id': 'load_collection'}

Node ID: ndvi_1
Node Name: ndvi
{'arguments': {'data': {'from_node': 's2a_0'}, 'name': 'ndvi'},
 'process_description': 'Calculate NDVI.',
 'process_id': 'ndvi'}

Node ID: min_time_2
Node Name: min_time
{'arguments': {'data': {'from_node': 'ndvi_1'},
               'dimension': 'temporal',
               'reducer': {'from_node': 'callback_3'}},
 'process_description': 'Take the minimum value in the time series.',
 'process_id': 'reduce'}

Node ID: callback_3
Node Name: callback
{'arguments': {'data': {'from_node': 'ndvi_1'}},
 'process_description': 'Calculate minimum',
 'process_id': 'min',
 'result': True}

Node ID: output_4
Node Name: output
{'arguments': {'data': {'from_node': 'min_time_2'}, 'format': 'Gtiff'},
 'description': 'Save to disk',
 'process_id': 'save_result'}
```
It also possible to sort the process graph by the dependency of each node
with:
```python
sorted_process_graph = process_graph.sort(by='dependency')
```
```
Node ID: s2a_0
Node Name: s2a
{'arguments': {'id': 'CGS_SENTINEL2_RADIOMETRY_V102_001',
               'spatial_extent': {'east': 16.84,
                                  'north': 48.4,
                                  'south': 47.9,
                                  'west': 15.96},
               'temporal_extent': ['2017-09-05', '2017-10-01']},
 'process_description': 'Loading S2A data.',
 'process_id': 'load_collection'}

Node ID: ndvi_1
Node Name: ndvi
{'arguments': {'data': {'from_node': 's2a_0'}, 'name': 'ndvi'},
 'process_description': 'Calculate NDVI.',
 'process_id': 'ndvi'}

Node ID: callback_3
Node Name: callback
{'arguments': {'data': {'from_node': 'ndvi_1'}},
 'process_description': 'Calculate minimum',
 'process_id': 'min',
 'result': True}

Node ID: min_time_2
Node Name: min_time
{'arguments': {'data': {'from_node': 'ndvi_1'},
               'dimension': 'temporal',
               'reducer': {'from_node': 'callback_3'}},
 'process_description': 'Take the minimum value in the time series.',
 'process_id': 'reduce'}

Node ID: output_4
Node Name: output
{'arguments': {'data': {'from_node': 'min_time_2'}, 'format': 'Gtiff'},
 'description': 'Save to disk',
 'process_id': 'save_result'}
```
If you are interested in a specific node, you can use Python indexing:
```python
print(sorted_process_graph['min_time_2'])
```
which results in:
```
Node ID: min_time_2
Node Name: min_time
{'arguments': {'data': {'from_node': 'ndvi_1'},
               'dimension': 'temporal',
               'reducer': {'from_node': 'callback_3'}},
 'process_description': 'Take the minimum value in the time series.',
 'process_id': 'reduce'}
```
A node has also offers access to its ancestors/parents/dependencies:
```python
print(sorted_process_graph['min_time_2'].dependencies)
```

```
Node ID: ndvi_1
Node Name: ndvi
{'arguments': {'data': {'from_node': 's2a_0'}, 'name': 'ndvi'},
 'process_description': 'Calculate NDVI.',
 'process_id': 'ndvi'}

Node ID: callback_3
Node Name: callback
{'arguments': {'data': {'from_node': 'ndvi_1'}},
 'process_description': 'Calculate minimum',
 'process_id': 'min',
 'result': True}
```

## Note

This project has been set up using PyScaffold 3.1. For details and usage
information on PyScaffold see https://pyscaffold.org/.

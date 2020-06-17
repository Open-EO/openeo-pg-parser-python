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
source activate openeo-pg-parser
python setup.py install
```

Change 'install' with 'develop' if you plan to further develop the package.


## Example

Here, we show how an *openEO* process graph can be translated into a `graph` object.
An exemplary process graph is stored in a file named *"process_graph_example.json"* and is given below:
```json
{
  "process_graph":
  {
    "apply": {
      "process_id": "apply",
      "arguments": {
        "data": {
          "from_node": "reduce_time"
        },
        "process": {
          "process_graph": {
            "linear_scale_range": {
              "process_id": "linear_scale_range",
              "arguments": {
                "x": {
                  "from_parameter": "x"
                },
                "inputMin": -1,
                "inputMax": 1,
                "outputMax": 255
              },
              "result": true
            }
          }
        }
      },
      "description": "Stretch range from -1 / 1 to 0 / 255 for PNG visualization."
    },
    "load_collection": {
      "process_id": "load_collection",
      "arguments": {
        "id": "COPERNICUS/S2",
        "spatial_extent": {
          "type": "Polygon",
          "coordinates": [
            [
              [
                7.246856689453125,
                47.167543112150554
              ],
              [
                7.218189239501953,
                47.13520594493793
              ],
              [
                7.23552703857422,
                47.11570074493338
              ],
              [
                7.2803306579589835,
                47.11488300552253
              ],
              [
                7.305736541748048,
                47.14793302647546
              ],
              [
                7.279300689697265,
                47.16999386399103
              ],
              [
                7.246856689453125,
                47.167543112150554
              ]
            ]
          ]
        },
        "temporal_extent": [
          "2018-01-01T00:00:00Z",
          "2018-01-31T23:59:59Z"
        ],
        "bands": [
          "B4",
          "B8"
        ]
      },
      "description": "Loading the data; The order of the specified bands is important for the following reduce operation."
    },
    "reduce_bands": {
      "process_id": "reduce_dimension",
      "arguments": {
        "data": {
          "from_node": "load_collection"
        },
        "reducer": {
          "process_graph": {
            "red": {
              "process_id": "array_element",
              "arguments": {
                "data": {
                  "from_parameter": "data"
                },
                "label": "B4"
              }
            },
            "nir": {
              "process_id": "array_element",
              "arguments": {
                "data": {
                  "from_parameter": "data"
                },
                "label": "B8"
              }
            },
            "ndvi": {
              "process_id": "normalized_difference",
              "arguments": {
                "x": {
                  "from_node": "nir"
                },
                "y": {
                  "from_node": "red"
                }
              },
              "result": true
            }
          }
        },
        "dimension": "bands"
      },
      "description": "Compute the NDVI: (NIR - RED) / (NIR + RED)"
    },
    "reduce_time": {
      "process_id": "reduce_dimension",
      "arguments": {
        "data": {
          "from_node": "reduce_bands"
        },
        "reducer": {
          "process_graph": {
            "max": {
              "process_id": "max",
              "arguments": {
                "data": {
                  "from_parameter": "data"
                }
              },
              "result": true
            }
          }
        },
        "dimension": "t"
      },
      "description": "Compute a minimum time composite by reducing the temporal dimension"
    },
    "save": {
      "process_id": "save_result",
      "arguments": {
        "data": {
          "from_node": "apply"
        },
        "format": "PNG"
      },
      "result": true
    }
  }
}
```
To translate the JSON file into a python object, use:
```python
from openeo_pg_parser.translate import translate_process_graph

pg_filepath = "process_graph_example.json"
process_graph = translate_process_graph(pg_filepath)
```
Note that there are additional parameters for `translate_process_graph`:

* `process_defs`: This can be a list, dictionary, directory path or URL containing JSON file paths of process definitions.
* `parameters`: A dictionary of globally defined parameters, which can be accessed via 'from_parameter' from the process graph.

If you print the `graph` you get the information contained in each node:
```
Node ID: apply_0
Node Name: apply
{'arguments': {'data': {'from_node': 'reduce_time_7'},
               'process': {'from_node': 'linear_scale_range_1'}},
 'description': 'Stretch range from -1 / 1 to 0 / 255 for PNG visualization.',
 'process_id': 'apply'}

Node ID: load_collection_2
Node Name: load_collection
{'arguments': {'bands': ['B4', 'B8'],
               'id': 'COPERNICUS/S2',
               'spatial_extent': {'coordinates': [[[7.246856689453125,
                                                    47.167543112150554],
                                                   [7.218189239501953,
                                                    47.13520594493793],
                                                   [7.23552703857422,
                                                    47.11570074493338],
                                                   [7.2803306579589835,
                                                    47.11488300552253],
                                                   [7.305736541748048,
                                                    47.14793302647546],
                                                   [7.279300689697265,
                                                    47.16999386399103],
                                                   [7.246856689453125,
                                                    47.167543112150554]]],
                                  'type': 'Polygon'},
               'temporal_extent': ['2018-01-01T00:00:00Z',
                                   '2018-01-31T23:59:59Z']},
 'description': 'Loading the data; The order of the specified bands is '
                'important for the following reduce operation.',
 'process_id': 'load_collection'}

Node ID: reduce_bands_3
Node Name: reduce_bands
{'arguments': {'data': {'from_node': 'load_collection_2'},
               'dimension': 'bands',
               'reducer': {'from_node': 'ndvi_6'}},
 'description': 'Compute the NDVI: (NIR - RED) / (NIR + RED)',
 'process_id': 'reduce_dimension'}

Node ID: reduce_time_7
Node Name: reduce_time
{'arguments': {'data': {'from_node': 'reduce_bands_3'},
               'dimension': 't',
               'reducer': {'from_node': 'max_8'}},
 'description': 'Compute a minimum time composite by reducing the temporal '
                'dimension',
 'process_id': 'reduce_dimension'}

Node ID: save_9
Node Name: save
{'arguments': {'data': {'from_node': 'apply_0'}, 'format': 'PNG'},
 'process_id': 'save_result',
 'result': True}

Node ID: linear_scale_range_1
Node Name: linear_scale_range
{'arguments': {'inputMax': 1,
               'inputMin': -1,
               'outputMax': 255,
               'x': {'from_node': 'reduce_time_7'}},
 'process_id': 'linear_scale_range',
 'result': True}

Node ID: red_4
Node Name: red
{'arguments': {'data': {'from_node': 'load_collection_2'}, 'label': 'B4'},
 'process_id': 'array_element'}

Node ID: nir_5
Node Name: nir
{'arguments': {'data': {'from_node': 'load_collection_2'}, 'label': 'B8'},
 'process_id': 'array_element'}

Node ID: ndvi_6
Node Name: ndvi
{'arguments': {'x': {'from_node': 'nir_5'}, 'y': {'from_node': 'red_4'}},
 'process_id': 'normalized_difference',
 'result': True}

Node ID: max_8
Node Name: max
{'arguments': {'data': {'from_node': 'reduce_bands_3'}},
 'process_id': 'max',
 'result': True}
```
It also possible to sort the process graph by the dependency of each node
with:
```python
sorted_process_graph = process_graph.sort(by='dependency')
```
```
Node ID: load_collection_2
Node Name: load_collection
{'arguments': {'bands': ['B4', 'B8'],
               'id': 'COPERNICUS/S2',
               'spatial_extent': {'coordinates': [[[7.246856689453125,
                                                    47.167543112150554],
                                                   [7.218189239501953,
                                                    47.13520594493793],
                                                   [7.23552703857422,
                                                    47.11570074493338],
                                                   [7.2803306579589835,
                                                    47.11488300552253],
                                                   [7.305736541748048,
                                                    47.14793302647546],
                                                   [7.279300689697265,
                                                    47.16999386399103],
                                                   [7.246856689453125,
                                                    47.167543112150554]]],
                                  'type': 'Polygon'},
               'temporal_extent': ['2018-01-01T00:00:00Z',
                                   '2018-01-31T23:59:59Z']},
 'description': 'Loading the data; The order of the specified bands is '
                'important for the following reduce operation.',
 'process_id': 'load_collection'}

Node ID: nir_5
Node Name: nir
{'arguments': {'data': {'from_node': 'load_collection_2'}, 'label': 'B8'},
 'process_id': 'array_element'}

Node ID: red_4
Node Name: red
{'arguments': {'data': {'from_node': 'load_collection_2'}, 'label': 'B4'},
 'process_id': 'array_element'}

Node ID: ndvi_6
Node Name: ndvi
{'arguments': {'x': {'from_node': 'nir_5'}, 'y': {'from_node': 'red_4'}},
 'process_id': 'normalized_difference',
 'result': True}

Node ID: reduce_bands_3
Node Name: reduce_bands
{'arguments': {'data': {'from_node': 'load_collection_2'},
               'dimension': 'bands',
               'reducer': {'from_node': 'ndvi_6'}},
 'description': 'Compute the NDVI: (NIR - RED) / (NIR + RED)',
 'process_id': 'reduce_dimension'}

Node ID: max_8
Node Name: max
{'arguments': {'data': {'from_node': 'reduce_bands_3'}},
 'process_id': 'max',
 'result': True}

Node ID: reduce_time_7
Node Name: reduce_time
{'arguments': {'data': {'from_node': 'reduce_bands_3'},
               'dimension': 't',
               'reducer': {'from_node': 'max_8'}},
 'description': 'Compute a minimum time composite by reducing the temporal '
                'dimension',
 'process_id': 'reduce_dimension'}

Node ID: linear_scale_range_1
Node Name: linear_scale_range
{'arguments': {'inputMax': 1,
               'inputMin': -1,
               'outputMax': 255,
               'x': {'from_node': 'reduce_time_7'}},
 'process_id': 'linear_scale_range',
 'result': True}

Node ID: apply_0
Node Name: apply
{'arguments': {'data': {'from_node': 'reduce_time_7'},
               'process': {'from_node': 'linear_scale_range_1'}},
 'description': 'Stretch range from -1 / 1 to 0 / 255 for PNG visualization.',
 'process_id': 'apply'}

Node ID: save_9
Node Name: save
{'arguments': {'data': {'from_node': 'apply_0'}, 'format': 'PNG'},
 'process_id': 'save_result',
 'result': True}
```
If you are interested in a specific node, you can use Python indexing:
```python
print(process_graph['reduce_time_7'])
```
which results in:
```
Node ID: reduce_time_7
Node Name: reduce_time
{'arguments': {'data': {'from_node': 'reduce_bands_3'},
               'dimension': 't',
               'reducer': {'from_node': 'max_8'}},
 'description': 'Compute a minimum time composite by reducing the temporal '
                'dimension',
 'process_id': 'reduce_dimension'}
```
A node also offers access to its relatives. This can for instance be a
sub-graph containing all node dependencies:
```python
print(process_graph['reduce_time_7'].dependencies)
```
```
Node ID: reduce_bands_3
Node Name: reduce_bands
{'arguments': {'data': {'from_node': 'load_collection_2'},
               'dimension': 'bands',
               'reducer': {'from_node': 'ndvi_6'}},
 'description': 'Compute the NDVI: (NIR - RED) / (NIR + RED)',
 'process_id': 'reduce_dimension'}

Node ID: max_8
Node Name: max
{'arguments': {'data': {'from_node': 'reduce_bands_3'}},
 'process_id': 'max',
 'result': True}
```
The dependencies reflect the processed data flow, which means that in
the case above, the node 'reduce_time' has to wait until 'reduce_bands' and 'max' (embedded process graph) is complete.
Moreover, one can access a parent process, where the current process_graph is embedded in:
```python
print(process_graph['max_8'].parent_process)
```
```
Node ID: reduce_time_7
Node Name: reduce_time
{'arguments': {'data': {'from_node': 'reduce_bands_3'},
               'dimension': 't',
               'reducer': {'from_node': 'max_8'}},
 'description': 'Compute a minimum time composite by reducing the temporal '
                'dimension',
 'process_id': 'reduce_dimension'}
```
or the child, embedded process graph:
```python
print(process_graph['reduce_time_7'].child_processes)
```
```
Node ID: max_8
Node Name: max
{'arguments': {'data': {'from_node': 'reduce_bands_3'}},
 'process_id': 'max',
 'result': True}
```

Not only information on node connections within a graph can be retrieved, also specific node information, e.g. if a node is a reducer:
```python
process_graph['reduce_time_7'].is_reducer
```
```python
True
```
and if so, the dimension over which the reduction takes place:
```python
process_graph['reduce_time_7'].dimension
```
```python
't'
```
## Note

This project has been set up using PyScaffold 3.1. For details and usage
information on PyScaffold see https://pyscaffold.org/.

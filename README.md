# openeo-pg-parser-python

This package allows to parse an *openEO* process graph (JSON) and convert it to a traversable Python object (`graph`).
The resulting directed `graph` object consists of nodes and edges and can help for instance to identify node relationships 
or to sort a graph by a specific attribute. The nodes are instances of `OpenEONode`, which can be used to extract information from itself, e.g., if it is a reducer and if so what dimension is used for reduction, or the direct neighbours, i.e., parent and child processes.
The nodes are connected via directed edges which represent the data flow (input and output) and can have two values: "data" or "callback". "data" specifies that the output of one node is the input for the second node.
"callback" is a connection between two processes, whereas the parent process is the embedded process graph (because the data is passed to the process, which is embedding the current one, after processing is done). 

Moreover, one can display a parsed process graph `process graph` in two ways. Once via `print(process graph)` to print the string representation of all the nodes in the graph and once via `process_graph.plot()`.
The latter option uses the Python package *igraph* to plot the graph on a map.
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

As short example, we can translate the following process graph, which loads S-2 data and computes the maximum NDVI value over a specific time span.
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
After parsing this process graph we get the following graph structure:

<img align="center" src="examples/s2_max_ndvi_graph.png" height="700" width="700">

Please have a look at the Juypter Notebooks under "examples" for further details.

## Note

This project has been set up using PyScaffold 3.1. For details and usage
information on PyScaffold see https://pyscaffold.org/.

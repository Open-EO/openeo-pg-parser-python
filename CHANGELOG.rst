=========
Changelog
=========

Version 1.0.0
=============

- Restructuring of graph classes and module setup. The following things changed in terms of the code:
    - renamed `node.graph` to `node.content`
    - all operations on a graph (dependencies, ancestors, lineage, ...) return now a subgraph
    - a graph has two new properties: `ids` and `nodes`. `ids` are the node IDs and `nodes` the nodes. Both are views
    - `nnodes` was removed and can be replaced by calling `len(graph)`
    - new class method `from_list` converts a list of nodes to a graph
    - `__getitem__` method in the graph class supports indexing by integer and node ID
    - `get_node_by_name` method in the graph class returns the first node matching a given name
    - `nodes_at_same_level` in the graph class was renamed and adapted to `find_siblings` (all nodes having the same parent)
- Additional tests


Version 0.0.1
=============

- First release for the openEO API 0.4

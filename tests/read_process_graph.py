import os
from processing_container_v04.translate_process_graph import translate

def main(pg_filename):
    pg_filepath = os.path.join(os.path.dirname(__file__), 'process_graphs', pg_filename)
    graph = translate(pg_filepath)
    graph.order(by="dependency", links=["data", "callback"], other_idxs=[0, 1])
    print(graph)

if __name__ == '__main__':
    pg_filename = "use_case_1.json"
    #pg_filename = "test_1.json"
    main(pg_filename)

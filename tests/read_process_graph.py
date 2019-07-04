import os
from openeo_pg_parser_python.translate_process_graph import translate

def main(pg_filename):
    pg_filepath = os.path.join(os.path.dirname(__file__), 'process_graphs', pg_filename)
    graph = translate(pg_filepath)
    graph.order(by="dependency")
    print(graph)

if __name__ == '__main__':
    pg_filename = "use_case_1.json"
    #pg_filename = "test_1.json"
    main(pg_filename)

import os
from processing_container_v04.translate_process_graph import translate

def main(pg_filename):
    pg_filepath = os.path.join(os.path.dirname(__file__), 'process_graphs', pg_filename)
    forest = translate(pg_filepath)
    print(forest)

if __name__ == '__main__':
    pg_filename = "use_case_1.json"
    main(pg_filename)

import pandas as pd
import os
import sys

try:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)

    from indexing import AVLTree

except ImportError as e:
    print(f"FATAL ERROR: Failed to import AVLTree and EmployeeGraph. Error: {e}")
    print("Troubleshooting: Please ensure 'indexing.py' and 'graph.py' are in the same 'core' folder as 'storage.py'.")
    sys.exit(1)
except NameError:
    print("FATAL ERROR: Could not determine file path.")
    sys.exit(1)


class MiniDBStorage:
    def __init__(self, data_file='data/records.csv'):
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.abspath(os.path.join(current_dir, '..'))
            self.data_file = os.path.join(project_root, data_file)
        except NameError:
            self.data_file = os.path.abspath(data_file)
            
        self.storage = {}
        self.score_index = AVLTree()
        self.is_loaded = False

    def load_data(self):
        if not os.path.exists(self.data_file):
            print(f"Error: Data file not found at expected path: {self.data_file}")
            print("Please ensure you have run the data generator script (data/pokec_ingest.py or data/generator.py).")
            return False

        print("Loading and indexing data... This may take a moment for 1M records.")
        
        try:
            df = pd.read_csv(self.data_file)
        except FileNotFoundError:
             print(f"Data file not found at {self.data_file}. Please run the data generator first.")
             return False
        
        df['record_id'] = df['record_id'].astype(int)
        df['index_score'] = df['index_score'].astype(int)
        df['manager_id'] = df['manager_id'].astype(int)

        self.storage = {}
        self.score_index = AVLTree()

        for index, row in df.iterrows():
            record = row.to_dict()
            record_id = record['record_id']
            index_score = record['index_score']

            self.storage[record_id] = record

            self.score_index.insert(index_score, record_id)

        print(f"Loaded {len(self.storage):,} records.")
        if self.score_index.root:
             print(f"AVL Index built successfully. Root key: {self.score_index.root.key}")
        
        self.employee_graph.build_from_dataframe(df)

        self.is_loaded = True
        return True

    def get_record(self, record_id):
        return self.storage.get(record_id)

    def get_all_records(self, record_ids):
        return [self.storage.get(rid) for rid in record_ids if rid in self.storage]
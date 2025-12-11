import csv
import sys
import os
import time

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from indexing import AVLTree
from graph import Graph 

class Storage:
    def __init__(self, data_path):
        self.data_path = data_path
        self.hash_map = {}
        self.age_index = AVLTree()
        self.hierarchy_graph = Graph()
        self.is_loaded = False

    def initialize(self):
        self._load_user_data()
        self.is_loaded = True

    def _load_user_data(self):
        data_file_path = self.data_path
        
        if not os.path.exists(data_file_path):
            print("="*80)
            print(f"CRITICAL ERROR: Data file not found at: {data_file_path}")
            print("="*80)
            sys.exit(1)
            
        row_count = 0
        update_interval = 100000 
        
        print("Loading data and building graph...")
        start_time = time.time()

        with open(data_file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                row_count += 1
                
                if row_count % update_interval == 0:
                    print(f"Loading data: {row_count:,} records processed...")

                try:
                    user_id = int(float(row['user_id'])) if row.get('user_id') else None
                    manager_id = int(float(row.get('manager_id', 0))) if row.get('manager_id') else 0 
                    age = int(float(row.get('age', 0))) if row.get('age') and float(row.get('age')) > 0 else None
                    
                    if user_id is None:
                        continue
                        
                    user_data = {
                        'user_id': user_id,
                        'gender': row.get('gender'),
                        'age': age,
                        'eye_color': row.get('eye_color'),
                        'education': row.get('education'),
                        'languages': row.get('languages'),
                        'music': row.get('music'),
                        'manager_id': manager_id
                    }
                    
                    self.hash_map[user_id] = user_data
                    
                    if age is not None:
                        self.age_index.insert(age, user_id)

                    if manager_id != user_id:
                        self.hierarchy_graph.add_edge(manager_id, user_id)
                
                except (ValueError, TypeError, KeyError) as e:
                    print(f"Skipping bad row {row_count} due to error: {e}")
                    pass
            
        end_time = time.time()
        print(f"Finished processing {row_count:,} total records.")
        print(f"Data loaded and Graph built. Time taken: {end_time - start_time:.4f} seconds.")

    def get_user_by_id(self, user_id):
        return self.hash_map.get(user_id)
    
    def get_all_records(self, record_ids):
        return [self.hash_map[uid] for uid in record_ids if uid in self.hash_map]

    def linear_search_by_age_range(self, min_age, max_age):
        if min_age > max_age:
            min_age, max_age = max_age, min_age
            
        results = []
        
        for user_data in self.hash_map.values():
            age = user_data.get('age')
            if age is not None and min_age <= age <= max_age:
                results.append(user_data)
        
        return results

    def search_by_age_range(self, min_age, max_age):
        if min_age > max_age:
            min_age, max_age = max_age, min_age
        
        user_ids = self.age_index.range_query(min_age, max_age)
        
        results = self.get_all_records(user_ids)
        return results

    def find_shortest_path(self, user_a_id, user_b_id):
        return self.hierarchy_graph.shortest_path(user_a_id, user_b_id)

    def get_direct_reports(self, manager_id):
        return self.hierarchy_graph.get_neighbors(manager_id)

    def add_user(self, user_data):
        user_id = user_data.get('user_id')
        age = user_data.get('age')
        manager_id = user_data.get('manager_id', 0)
        
        if user_id is None or user_id in self.hash_map:
            raise ValueError(f"User ID {user_id} is invalid or already exists.")
        
        self.hash_map[user_id] = user_data
        
        if age is not None:
            self.age_index.insert(age, user_id)

        self.hierarchy_graph.add_edge(manager_id, user_id)

    def delete_user(self, user_id):
        if user_id not in self.hash_map:
            return False

        user_data = self.hash_map.pop(user_id)
        age = user_data.get('age')

        if age is not None:
            self.age_index.delete_record_id(age, user_id)
            
        self.hierarchy_graph.remove_node(user_id)
        
        return True

    def modify_user(self, user_id, updates):
        if user_id not in self.hash_map:
            return False

        current_data = self.hash_map[user_id]
        old_age = current_data.get('age')
        new_age = updates.get('age')
        
        if new_age is not None and new_age != old_age:
            if old_age is not None:
                self.age_index.delete_record_id(old_age, user_id)
            current_data['age'] = new_age
            self.age_index.insert(new_age, user_id)
        
        for key, value in updates.items():
            if key != 'age':
                current_data[key] = value
        
        return True
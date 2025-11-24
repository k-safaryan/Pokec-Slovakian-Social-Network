import csv
import time
from indexing import AVLTree

class Storage:
    def __init__(self, data_path, relationships_path):
        self.data_path = data_path
        self.relationships_path = relationships_path
        self.hash_map = {}
        self.avl_index = AVLTree()
        self.graph = {}
        self.users = []
        self.is_initialized = False

    def load_user_data(self):
        with open(self.data_path, mode='r', encoding='utf-8') as file:
            reader = csv.reader(file)
            header = next(reader)
            
            for row in reader:
                try:
                    user_id = int(float(row[0]))
                    user = {
                        'user_id': user_id,
                        'gender': row[1] if len(row) > 1 else 'Unknown',
                        'age': int(float(row[2])) if len(row) > 2 and row[2] and row[2].strip() else None,
                        'eye_color': row[3] if len(row) > 3 else 'Unknown',
                        'education': row[4] if len(row) > 4 else 'Unknown',
                        'languages': row[5] if len(row) > 5 else 'Unknown',
                        'music': row[6] if len(row) > 6 else 'Unknown'
                    }
                    self.users.append(user)
                    self.hash_map[user_id] = user
                    
                    if user['age'] is not None:
                        self.avl_index.add(user['age'], user_id)
                    
                    self.graph[user_id] = set()
                except Exception:
                    continue

    def load_relationships(self):
        with open(self.relationships_path, mode='r', encoding='utf-8') as file:
            for line in file:
                try:
                    u1_str, u2_str = line.strip().split()
                    u1 = int(u1_str)
                    u2 = int(u2_str)
                    
                    if u1 in self.graph and u2 in self.graph:
                        self.graph[u1].add(u2)
                        self.graph[u2].add(u1)
                except Exception:
                    continue

    def initialize(self):
        if self.is_initialized:
            return

        self.load_user_data()
        self.load_relationships()
        self.is_initialized = True

    def get_user_by_id(self, user_id):
        return self.hash_map.get(user_id)

    def search_by_age_range(self, min_age, max_age):
        results = []
        self.avl_index.range_search(self.avl_index.root, min_age, max_age, results)
        
        users = []
        for user_id in results:
            user = self.get_user_by_id(user_id)
            if user:
                users.append(user)
        return users

    def find_shortest_path(self, start_id, end_id):
        if start_id not in self.graph or end_id not in self.graph:
            return None

        queue = [(start_id, [start_id])]
        visited = {start_id}

        while queue:
            current_id, path = queue.pop(0)

            if current_id == end_id:
                return path

            for neighbor_id in self.graph.get(current_id, set()):
                if neighbor_id not in visited:
                    visited.add(neighbor_id)
                    new_path = path + [neighbor_id]
                    queue.append((neighbor_id, new_path))
        
        return None

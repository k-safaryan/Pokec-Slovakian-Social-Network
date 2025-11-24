import csv
from indexing import AVLTree

class Storage:
    def __init__(self, data_path):
        self.data_path = data_path
        self.hash_map = {}
        self.age_index = AVLTree()

    def initialize(self):
        self._load_user_data()

    def _load_user_data(self):
        with open(self.data_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    user_id = int(float(row['user_id']))
                    age = int(float(row['age'])) if row['age'] and float(row['age']) > 0 else None
                    
                    user_data = {
                        'user_id': user_id,
                        'gender': row.get('gender'),
                        'age': age,
                        'eye_color': row.get('eye_color'),
                        'education': row.get('education'),
                        'languages': row.get('languages'),
                        'music': row.get('music')
                    }
                    
                    self.hash_map[user_id] = user_data
                    
                    if age is not None:
                        self.age_index.add(age, user_data)
                
                except (ValueError, TypeError) as e:
                    pass

    def get_user_by_id(self, user_id):
        return self.hash_map.get(user_id)

    def search_by_age_range(self, min_age, max_age):
        if min_age > max_age:
            min_age, max_age = max_age, min_age
        return self.age_index.range_search(min_age, max_age)

    def add_user(self, user_data):
        user_id = user_data['user_id']
        age = user_data['age']
        
        if user_id in self.hash_map:
            raise ValueError(f"User ID {user_id} already exists.")
        
        self.hash_map[user_id] = user_data
        
        if age is not None:
            self.age_index.add(age, user_data)

    def delete_user(self, user_id):
        if user_id not in self.hash_map:
            return False

        user_data = self.hash_map.pop(user_id)
        age = user_data.get('age')

        if age is not None:
            self.age_index.delete(age, user_data)
        
        return True

    def modify_user(self, user_id, updates):
        if user_id not in self.hash_map:
            return False

        current_data = self.hash_map[user_id]
        old_age = current_data.get('age')
        new_age = updates.get('age')

        if new_age is not None and new_age != old_age:
            if old_age is not None:
                self.age_index.delete(old_age, current_data)
            
            current_data['age'] = new_age
            self.age_index.add(new_age, current_data)
        
        for key, value in updates.items():
            if key != 'age':
                current_data[key] = value
        
        return True

import time
from storage import Storage

class QueryEngine:
    def __init__(self, data_path):
        self.data_path = data_path
        self.storage = Storage(data_path)

    def initialize_data(self):
        print("Starting data initialization...")
        start_time = time.time()
        self.storage.initialize()
        end_time = time.time()
        print(f"Data initialization complete. Time taken: {end_time - start_time:.4f} seconds.")

    def run_age_range_query(self, min_age, max_age):
        print(f"\n--- Running Age Range Query: {min_age}-{max_age} ---")
        start_time = time.time()
        results = self.storage.search_by_age_range(min_age, max_age)
        end_time = time.time()
        time_taken = end_time - start_time
        
        print(f"Found {len(results)} users in age range {min_age}-{max_age}.")
        print(f"Time taken for AVL Search: {time_taken:.6f} seconds.")
        
        print("\nFirst 5 results:")
        for user in results[:5]:
            print(f"  ID: {user['user_id']}, Age: {user['age']}, Gender: {user['gender']}")
            
        return results, time_taken

    def run_dynamic_operations(self):
        print("\n" + "="*50)
        print("DYNAMIC OPERATIONS (Insertion, Modification, Deletion)")
        print("="*50)

        new_user_id = 9999999
        new_user_data = {'user_id': new_user_id, 'gender': 'Female', 'age': 25, 'eye_color': 'blue', 'education': 'uni', 'languages': 'en', 'music': 'rock'}
        print(f"\nAttempting to insert new user ID: {new_user_id} (Age 25)")
        self.storage.add_user(new_user_data)
        
        check_user = self.storage.get_user_by_id(new_user_id)
        print(f"Insertion successful. User data: {check_user}")
        
        print(f"\nAttempting to modify user ID: {new_user_id} (Change age from 25 to 28)")
        self.storage.modify_user(new_user_id, {'age': 28, 'music': 'pop'})
        
        check_user = self.storage.get_user_by_id(new_user_id)
        print(f"Modification successful. New Age: {check_user['age']}, New Music: {check_user['music']}")

        print(f"\nAttempting to delete user ID: {new_user_id}")
        self.storage.delete_user(new_user_id)
        
        check_user = self.storage.get_user_by_id(new_user_id)
        print(f"Deletion successful. User check in hash map: {check_user}")


    def run_all_queries(self):
        self.initialize_data()

        print("\n" + "="*50)
        print("AVL TREE INDEX QUERIES (Age Range Search)")
        print("="*50)
        
        self.run_age_range_query(20, 22)
        self.run_age_range_query(30, 40)
        
        self.run_dynamic_operations()

        print("\nAll predefined queries completed.")


engine = QueryEngine(DATA_FILE)
engine.run_all_queries()


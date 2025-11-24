import time
from storage import Storage
from graph import Graph

class QueryEngine:
    def __init__(self, data_path, relationships_path):
        self.data_path = data_path
        self.relationships_path = relationships_path
        self.storage = Storage(data_path)
        self.graph_manager = Graph(relationships_path)

    def initialize_data(self):
        print("Starting data initialization...")
        start_time = time.time()
        self.storage.initialize()
        self.graph_manager.initialize()
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

    def run_shortest_path_query(self, start_id, end_id):
        print(f"\n--- Running Shortest Path Query (BFS): {start_id} -> {end_id} ---")
        start_time = time.time()
        path = self.graph_manager.find_shortest_path(start_id, end_id)
        end_time = time.time()
        time_taken = end_time - start_time

        if path:
            path_str = " -> ".join(map(str, path))
            print(f"Shortest path found (Length: {len(path) - 1}):")
            print(f"  {path_str}")
        else:
            print(f"No path found between {start_id} and {end_id}.")

        print(f"Time taken for BFS Search: {time_taken:.6f} seconds.")

        return path, time_taken

    def run_dfs_traversal(self, start_id):
        print(f"\n--- Running DFS Traversal from User: {start_id} ---")
        start_time = time.time()
        traversal = self.graph_manager.depth_first_traversal(start_id)
        end_time = time.time()
        time_taken = end_time - start_time
        
        print(f"DFS Traversal Order (First 10 nodes): {traversal[:10]}...")
        print(f"Total nodes visited: {len(traversal)}")
        print(f"Time taken for DFS Traversal: {time_taken:.6f} seconds.")
        return traversal, time_taken

    def run_clustering_and_centrality(self, user_id):
        print(f"\n--- Running Network Analysis for User: {user_id} ---")
        start_time = time.time()
        
        degree = self.graph_manager.calculate_degree_centrality(user_id)
        clustering = self.graph_manager.calculate_local_clustering_coefficient(user_id)
        
        end_time = time.time()
        time_taken = end_time - start_time

        print(f"Degree Centrality (Connections): {degree}")
        print(f"Local Clustering Coefficient: {clustering:.4f}")
        print(f"Time taken for Centrality Calculation: {time_taken:.6f} seconds.")
        
        return degree, clustering, time_taken

    def run_dynamic_operations(self):
        print("\n" + "="*50)
        print("DYNAMIC OPERATIONS (Insertion, Modification, Deletion)")
        print("="*50)

        new_user_id = 9999999
        new_user_data = {'user_id': new_user_id, 'gender': 'Female', 'age': 25, 'eye_color': 'blue', 'education': 'uni', 'languages': 'en', 'music': 'rock'}
        print(f"\nAttempting to insert new user ID: {new_user_id} (Age 25)")
        self.storage.add_user(new_user_data)
        self.graph_manager.add_edge(new_user_id, 1) 
        self.graph_manager.add_edge(new_user_id, 2)
        
        check_user = self.storage.get_user_by_id(new_user_id)
        print(f"Insertion successful. User data: {check_user}")
        
        print(f"\nAttempting to modify user ID: {new_user_id} (Change age from 25 to 28)")
        self.storage.modify_user(new_user_id, {'age': 28, 'music': 'pop'})
        
        check_user = self.storage.get_user_by_id(new_user_id)
        print(f"Modification successful. New Age: {check_user['age']}, New Music: {check_user['music']}")

        print(f"\nAttempting to delete user ID: {new_user_id}")
        self.storage.delete_user(new_user_id)
        success = self.graph_manager.remove_user(new_user_id)
        
        check_user = self.storage.get_user_by_id(new_user_id)
        print(f"Deletion successful from graph: {success}. User check in hash map: {check_user}")


    def run_all_queries(self):
        self.initialize_data()

        print("\n" + "="*50)
        print("AVL TREE INDEX QUERIES (Age Range Search)")
        print("="*50)
        
        self.run_age_range_query(20, 22)
        self.run_age_range_query(30, 40)
        
        self.run_dynamic_operations()

        print("\n" + "="*50)
        print("ADVANCED GRAPH QUERIES (Pathfinding, Traversal, Analysis)")
        print("="*50)

        self.run_shortest_path_query(1, 4)
        self.run_shortest_path_query(1, 100)
        
        self.run_dfs_traversal(1)
        
        self.run_clustering_and_centrality(1)
        self.run_clustering_and_centrality(17)
        
        print("\nAll predefined queries completed.")

engine = QueryEngine(DATA_FILE, RELATIONSHIPS_FILE)
engine.run_all_queries()


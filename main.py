import os
import sys
from collections import deque
import subprocess

script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir) 

try:
    from core.storage import Storage
    from core.query_engine import QueryEngine
    from core.graph import Graph
except ImportError:
    print("FATAL: Could not import core modules. Check project structure.")
    sys.exit(1)

DATA_FILE = 'dataset.csv'
RELATIONSHIP_FILE = 'relationships.csv'
DATA_PATH = os.path.join(script_dir, 'data', DATA_FILE) 
RELATIONSHIP_PATH = os.path.join(script_dir, 'data', RELATIONSHIP_FILE) 
APP_FILE_PATH = os.path.join(script_dir, 'ui', 'app.py')

def find_valid_graph_ids(storage_instance: Storage):
    graph = storage_instance.social_graph
    
    if not graph.friends:
        print("[DEBUG] CRITICAL: Social graph is empty. Skipping all graph tests.")
        return 1, 2, 3 
        
    valid_users = [node for node, friends in graph.friends.items() if friends] 
    
    if not valid_users:
        print("[DEBUG] CRITICAL: No user in the dataset has any friends. Cannot test graph.")
        return 0, 0, 0
    
    user_A = valid_users[0]
    
    if not graph.friends.get(user_A):
        return 0, 0, 0
        
    friend_B = graph.friends[user_A][0]

    far_node = friend_B
    queue = deque([friend_B])
    visited = {user_A, friend_B}
    depth = 0
    
    while queue and depth < 3:
        level_size = len(queue)
        depth += 1
        for _ in range(level_size):
            current = queue.popleft()
            for neighbor in graph.friends.get(current, []): 
                if neighbor not in visited:
                    visited.add(neighbor)
                    far_node = neighbor
                    if depth >= 2:
                        return user_A, friend_B, far_node
                    queue.append(neighbor)
    
    return user_A, friend_B, far_node 

def run_system_check():
    print("=" * 60)
    print("--- 1. INITIALIZING DATA SYSTEM ---")
    print("=" * 60)
    
    storage = Storage(DATA_PATH, RELATIONSHIP_PATH) 
    storage.initialize() 
    engine = QueryEngine(storage) 
    
    if not engine.is_ready:
        print("CRITICAL LOGIC ERROR: Initialization failed.")
        return

    test_user, test_friend, test_far_node = find_valid_graph_ids(storage)
    
    print("\n" + "=" * 60)
    print("--- 2. INDEXING EFFICIENCY TEST---")
    print("=" * 60)
    
    engine.compare_linear_search_by_age_range(18, 30)

    print("\n" + "=" * 60)
    print("--- 3. CORE FUNCTIONALITY & PERFORMANCE CHECKS ---")
    print("=" * 60)
    
    test_user_id = 1 
    print(f"\n[Check 3A] O(1) Hash Map Lookup for User ID {test_user_id}:")
    engine.get_record_by_id(test_user_id)

    test_age = 22
    print(f"\n[Check 3B] O(log N) Indexed Search for Age {test_age}:")
    engine.search_by_index_score(test_age)

    print(f"\n[Check 3C] Graph Pathfinding (BFS) between {test_user} and {test_far_node}:")
    path_ids = storage.social_graph.shortest_path(test_user, test_far_node)
    if path_ids:
        print(f"Shortest path found (length {len(path_ids)-1}): {path_ids}")
    else:
        print(f"Shortest path not found between {test_user} and {test_far_node}.")

    print(f"\n[Check 3D] Get Friends for ID {test_user}:")
    friends = storage.get_friends(test_user)
    if friends:
        print(f"ID {test_user} has {len(friends)} friends: {friends[:5]}...")
    else:
        print(f"ID {test_user} has no friends.")
        
    print("\n" + "=" * 60)
    print("--- 4. DATA MUTATION AND CONSISTENCY CHECK ---")
    print("=" * 60)
    
    new_id = 9999999
    
    print(f"\n[Check 4A] Insertion of new user ID {new_id} (Testing Hash Map, AVL, Graph):")
    new_data = {
        'user_id': new_id,
        'gender': 'Male',
        'age': 42,
        'friends': str(test_user)
    }
    storage.add_user(new_data)
    print(f"Insertion verified: {storage.get_user_by_id(new_id) is not None}")
    
    print(f"[Check 4B] Deletion of user ID {new_id} (Testing Consistency):")
    storage.delete_user(new_id)
    
    hash_map_ok = storage.get_user_by_id(new_id) is None
    graph_ok = new_id not in storage.social_graph.nodes
    
    print(f"Removed from Hash Map: {hash_map_ok}")
    print(f"Removed from Graph Nodes: {graph_ok}")
    
    if hash_map_ok and graph_ok:
        print("\nSUCCESS: System passed consistency check.")
    else:
        print("\nFAILURE: Deletion failed or data inconsistency detected.")

run_system_check()
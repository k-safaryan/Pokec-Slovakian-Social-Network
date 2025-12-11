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
    print("FATAL: Could not import core modules. Check project structure and __init__.py files.")
    sys.exit(1)

DATA_FILE = 'dataset.csv'
DATA_PATH = os.path.join(script_dir, 'data', DATA_FILE) 
APP_FILE_PATH = os.path.join(script_dir, 'ui', 'app.py')

def find_valid_graph_ids(storage_instance: Storage):
    graph = storage_instance.hierarchy_graph
    
    valid_managers = [node for node, reports in graph.adj.items() if reports]
    
    if not valid_managers:
        print("[DEBUG] CRITICAL: No user in the dataset has any direct reports. Cannot test graph.")
        return 0, 0, 0
    
    manager_A = valid_managers[0]
    
    employee_B = graph.adj[manager_A][0]

    far_node = employee_B
    queue = deque([employee_B])
    visited = {manager_A, employee_B}
    depth = 0
    
    while queue and depth < 3:
        level_size = len(queue)
        depth += 1
        for _ in range(level_size):
            current = queue.popleft()
            for neighbor in graph.adj.get(current, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    far_node = neighbor
                    if depth >= 2:
                        return manager_A, employee_B, far_node
                    queue.append(neighbor)
    
    return manager_A, employee_B, employee_B 

def run_system_check():
    print("=" * 60)
    print("--- 1. INITIALIZING DATA SYSTEM ---")
    print("=" * 60)
    
    storage = Storage(DATA_PATH)
    
    storage.initialize() 

    engine = QueryEngine(storage) 
    
    if not engine.is_ready:
        print("CRITICAL LOGIC ERROR: Initialization failed.")
        return

    test_manager, test_direct_report, test_far_node = find_valid_graph_ids(storage)
    
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

    print(f"\n[Check 3C] Graph Pathfinding (BFS) between {test_manager} and {test_far_node}:")
    path_ids = storage.hierarchy_graph.shortest_path(test_manager, test_far_node)
    if path_ids:
        print(f"Shortest path found (length {len(path_ids)-1}): {path_ids}")
    else:
        print(f"Shortest path not found between {test_manager} and {test_far_node}.")

    print(f"\n[Check 3D] Direct Downstream Connections for ID {test_manager}:")
    reports = storage.get_direct_reports(test_manager)
    if reports:
        print(f"ID {test_manager} has {len(reports)} connections: {reports[:5]}...")
        
        print(f"\n[Check 3E] Path to Root/CEO for connected ID {test_direct_report}:")
        path_to_root = engine.find_shortest_path_to_ceo(test_direct_report)
        if path_to_root:
            path_ids_root = [record['user_id'] for record in path_to_root]
            print(f"Path (Root -> Employee): {path_ids_root}")
        else:
            print(f"Path to Root not found for employee {test_direct_report}.")

    else:
        print(f"ID {test_manager} has no direct connections.")
        
    print("\n" + "=" * 60)
    print("--- 4. DATA MUTATION AND CONSISTENCY CHECK ---")
    print("=" * 60)
    
    new_id = 9999999
    
    print(f"\n[Check 4A] Insertion of new user ID {new_id} (Testing Hash Map, AVL, Graph):")
    new_data = {
        'user_id': new_id,
        'gender': 'Male',
        'age': 42,
        'manager_id': test_manager if test_manager != 0 else 1 
    }
    storage.add_user(new_data)
    print(f"Insertion verified: {storage.get_user_by_id(new_id) is not None}")
    
    print(f"[Check 4B] Deletion of user ID {new_id} (Testing Consistency):")
    storage.delete_user(new_id)
    
    hash_map_ok = storage.get_user_by_id(new_id) is None
    graph_ok = new_id not in storage.hierarchy_graph.nodes
    
    print(f"Removed from Hash Map: {hash_map_ok}")
    print(f"Removed from Graph Nodes: {graph_ok}")
    
    if hash_map_ok and graph_ok:
        print("\nSUCCESS: System passed consistency check.")
    else:
        print("\nFAILURE: Deletion failed or data inconsistency detected.")
        
    print("\n" + "=" * 60)
    print(f"--- 5. LAUNCHING INTERACTIVE UI ---")
    print(f"Run 'streamlit run {APP_FILE_PATH}' to start the web application.")
    print("=" * 60)

def launch_ui():
    try:
        subprocess.run(["streamlit", "run", APP_FILE_PATH], check=True)
    except FileNotFoundError:
        print("ERROR: Streamlit command not found. Please install Streamlit.")
    except subprocess.CalledProcessError:
        print("ERROR: Streamlit application failed to run.")

run_system_check()
launch_ui()
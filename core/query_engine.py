import time
import pandas as pd
from collections import Counter
import sys
import os
from typing import List, Dict, Any, Optional

script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.append(script_dir)

try:
    from storage import Storage 
except ImportError:
    pass

class QueryEngine:
    def __init__(self, storage):
        self.storage = storage
        self.is_ready = storage.is_loaded

    def get_record_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        if not self.is_ready:
            return None
        
        start_time = time.perf_counter()
        record = self.storage.get_user_by_id(int(user_id))
        end_time = time.perf_counter()
        
        if record:
            print(f"Record {user_id} found in {(end_time - start_time) * 1000:.3f} ms (O(1) Hash Map lookup).")
        else:
            print(f"Record {user_id} not found.")
        return record

    def search_by_index_score(self, min_score: int, max_score: Optional[int] = None) -> List[Dict[str, Any]]:
        if not self.is_ready:
            return []
            
        if max_score is None:
            max_score = min_score
            
        start_time = time.perf_counter()
        results = self.storage.search_by_age_range(min_score, max_score)
        end_time = time.perf_counter()
        
        if min_score == max_score:
            print(f"Found {len(results)} record(s) with age={min_score} in {(end_time - start_time) * 1000:.3f} ms (O(log N) AVL Tree lookup).")
        
        return results

    def compare_linear_search_by_age_range(self, min_age: int, max_age: int) -> List[Dict[str, Any]]:
        if not self.is_ready:
            print("System not initialized.")
            return []

        print(f"--- Performance Comparison for Age Range [{min_age}, {max_age}] ---")

        start_linear = time.perf_counter()
        linear_results = self.storage.linear_search_by_age_range(min_age, max_age)
        end_linear = time.perf_counter()
        linear_time_ms = (end_linear - start_linear) * 1000

        start_indexed = time.perf_counter()
        indexed_results = self.storage.search_by_age_range(min_age, max_age)
        end_indexed = time.perf_counter()
        indexed_time_ms = (end_indexed - start_indexed) * 1000

        print(f"Linear Search: {len(linear_results)} records found in {linear_time_ms:.3f} ms (O(N) complexity).")
        print(f"AVL Tree Search: {len(indexed_results)} records found in {indexed_time_ms:.3f} ms (O(log N + K) complexity).")

        speedup = linear_time_ms / indexed_time_ms if indexed_time_ms > 0 else float('inf')
        print(f"Conclusion: AVL Tree is {speedup:.1f}x faster than Linear Search.")
        
        return indexed_results

    def find_shortest_path(self, user_a: int, user_b: int) -> List[Dict[str, Any]]:
        if not self.is_ready:
            print("System not initialized.")
            return []

        start_time = time.perf_counter()

        path_ids = self.storage.find_shortest_path(int(user_a), int(user_b))

        end_time = time.perf_counter()

        if path_ids:
            print(
                f"Shortest path found with {len(path_ids) - 1} hop(s) "
                f"in {(end_time - start_time) * 1000:.3f} ms (BFS: O(V + E))."
            )
            return self.storage.get_all_records(path_ids)
        else:
            print(
                f"No path between {user_a} and {user_b}. "
                f"Network is disconnected for these users."
            )
            return []

    def get_user_friends(self, user_id: int) -> List[Dict[str, Any]]:
        if not self.is_ready:
            return []
            
        start_time = time.perf_counter()
        friend_ids = self.storage.get_friends(int(user_id))
        records = self.storage.get_all_records(friend_ids)
        end_time = time.perf_counter()
        
        print(f"Found {len(records)} friends in {(end_time - start_time) * 1000:.3f} ms.")
        return records

    def get_distribution(self, attribute: str) -> Dict[Any, int]:
        if not self.is_ready:
            return {}
        
        data_values = [
            record.get(attribute) 
            for record in self.storage.hash_map.values() 
            if record.get(attribute) is not None
        ]

        if not data_values:
            return {}
        
        series = pd.Series(data_values)
        distribution = series.value_counts().to_dict()
        
        return distribution
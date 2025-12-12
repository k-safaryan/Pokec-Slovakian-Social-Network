import csv
import sys
import os
import time
import statistics
from typing import List, Dict, Any, Optional, Iterable

from indexing import AVLTree
from graph import Graph


class Storage:
    """
    Storage for user records with:
    - hash_map: user_id -> user_data dict
    - age_index: AVLTree index mapping ages -> user_ids (supports range_query)
    - hierarchy_graph: Graph holding social edges between users
    """

    def __init__(self, data_path: str):
        self.data_path = data_path
        self.hash_map: Dict[int, Dict[str, Any]] = {}
        self.age_index = AVLTree()
        self.hierarchy_graph = Graph()
        self.is_loaded = False

    def initialize(self) -> None:
        """Load data from CSV path and build indices/graph."""
        self._load_user_data()
        self.is_loaded = True

    def _load_user_data(self) -> None:
        data_file_path = self.data_path

        if not os.path.exists(data_file_path):
            print("=" * 80)
            print(f"CRITICAL ERROR: Data file not found at: {data_file_path}")
            print("=" * 80)
            sys.exit(1)

        row_count = 0
        update_interval = 100000

        print("Loading data and building graph...")
        start_time = time.time()

        with open(data_file_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                row_count += 1

                if row_count % update_interval == 0:
                    print(f"Loading data: {row_count:,} records processed...")

                try:
                    # Parse user_id robustly
                    raw_user_id = row.get("user_id")
                    if not raw_user_id:
                        continue
                    user_id = int(float(raw_user_id))

                    # Parse age (if present and positive)
                    raw_age = row.get("age")
                    age = None
                    if raw_age:
                        try:
                            age_val = float(raw_age)
                            if age_val > 0:
                                age = int(age_val)
                        except ValueError:
                            age = None

                    # Build user_data dict
                    user_data = {
                        "user_id": user_id,
                        "gender": row.get("gender"),
                        "age": age,
                        "eye_color": row.get("eye_color"),
                        "education": row.get("education"),
                        "languages": row.get("languages"),
                        "music": row.get("music"),
                        # store raw friends string (optional)
                        "friends_raw": row.get("friends", ""),
                    }

                    # Insert into hashmap
                    self.hash_map[user_id] = user_data

                    # Insert into age index
                    if age is not None:
                        # expecting AVLTree.insert(key, record_id)
                        self.age_index.insert(age, user_id)

                    # Parse friends: supports semicolon-separated friend IDs
                    friends_raw = row.get("friends", "")
                    if friends_raw:
                        friend_ids: List[int] = []
                        for fid_str in friends_raw.split(";"):
                            fid_str = fid_str.strip()
                            if not fid_str:
                                continue
                            # allow floats stored (e.g., "123.0")
                            if fid_str.replace(".", "", 1).isdigit():
                                try:
                                    fid = int(float(fid_str))
                                    friend_ids.append(fid)
                                except ValueError:
                                    # skip bad friend id
                                    continue
                        # Add edges to graph (user -> friend)
                        for fid in friend_ids:
                            # Graph.add_edge should accept nodes that are not yet present
                            self.hierarchy_graph.add_edge(user_id, fid)

                except (ValueError, TypeError, KeyError) as e:
                    print(f"Skipping bad row {row_count} due to error: {e}")
                    continue

        end_time = time.time()
        print(f"Finished processing {row_count:,} total records.")
        print(
            f"Data loaded and Graph built. Time taken: {end_time - start_time:.4f} seconds."
        )

    # ---------------------------
    # Basic accessors
    # ---------------------------
    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        return self.hash_map.get(user_id)

    def get_all_records(self, record_ids: Iterable[int]) -> List[Dict[str, Any]]:
        return [self.hash_map[uid] for uid in record_ids if uid in self.hash_map]

    # ---------------------------
    # Age-based searches
    # ---------------------------
    def linear_search_by_age_range(self, min_age: int, max_age: int) -> List[Dict[str, Any]]:
        if min_age > max_age:
            min_age, max_age = max_age, min_age

        results = []
        for user_data in self.hash_map.values():
            age = user_data.get("age")
            if age is not None and min_age <= age <= max_age:
                results.append(user_data)
        return results

    def search_by_age_range(self, min_age: int, max_age: int) -> List[Dict[str, Any]]:
        if min_age > max_age:
            min_age, max_age = max_age, min_age

        # age_index.range_query should return an iterable of user_ids
        user_ids = self.age_index.range_query(min_age, max_age)
        return self.get_all_records(user_ids)

    # ---------------------------
    # Graph helpers
    # ---------------------------
    def find_shortest_path(self, user_a_id: int, user_b_id: int) -> List[int]:
        return self.hierarchy_graph.shortest_path(user_a_id, user_b_id)

    def get_direct_reports(self, user_id: int) -> List[int]:
        """Return immediate neighbors / friends of a given user."""
        return self.hierarchy_graph.get_neighbors(user_id)

    def get_friends(self, user_id: int) -> List[int]:
        """Alias for getting friends (keeps naming consistent)."""
        nbrs = self.get_direct_reports(user_id)
        return nbrs if nbrs is not None else []

    # ---------------------------
    # CRUD operations
    # ---------------------------
    def add_user(self, user_data: Dict[str, Any]) -> None:
        user_id = user_data.get("user_id")
        if user_id is None or user_id in self.hash_map:
            raise ValueError(f"User ID {user_id} is invalid or already exists.")

        # normalize friend ids
        friend_ids = user_data.get("friend_ids") or user_data.get("friends") or []
        parsed_friend_ids: List[int] = []
        if isinstance(friend_ids, str):
            for fid_str in friend_ids.split(";"):
                fid_str = fid_str.strip()
                if not fid_str:
                    continue
                if fid_str.replace(".", "", 1).isdigit():
                    parsed_friend_ids.append(int(float(fid_str)))
        elif isinstance(friend_ids, Iterable):
            for fid in friend_ids:
                try:
                    parsed_friend_ids.append(int(fid))
                except Exception:
                    continue

        # store
        self.hash_map[user_id] = user_data

        # age index
        age = user_data.get("age")
        if age is not None:
            self.age_index.insert(age, user_id)

        # add edges for friends
        for fid in parsed_friend_ids:
            self.hierarchy_graph.add_edge(user_id, fid)

    def delete_user(self, user_id: int) -> bool:
        if user_id not in self.hash_map:
            return False

        user_data = self.hash_map.pop(user_id)
        age = user_data.get("age")

        if age is not None:
            # expects a method to remove a specific record id at that key
            try:
                self.age_index.delete_record_id(age, user_id)
            except AttributeError:
                # fallback: if AVLTree only supports delete(key), try that (risky)
                try:
                    self.age_index.delete(age)
                except Exception:
                    pass

        # remove from graph
        self.hierarchy_graph.remove_node(user_id)
        return True

    def modify_user(self, user_id: int, updates: Dict[str, Any]) -> bool:
        if user_id not in self.hash_map:
            return False

        current_data = self.hash_map[user_id]
        old_age = current_data.get("age")
        new_age = updates.get("age", old_age)

        if new_age is not None and new_age != old_age:
            # remove old index entry
            if old_age is not None:
                try:
                    self.age_index.delete_record_id(old_age, user_id)
                except AttributeError:
                    try:
                        self.age_index.delete(old_age)
                    except Exception:
                        pass
            # add new
            current_data["age"] = new_age
            self.age_index.insert(new_age, user_id)

        # update other fields
        for key, value in updates.items():
            if key == "age":
                continue
            current_data[key] = value

        # save back (not necessary because dict mutated in place, but explicit)
        self.hash_map[user_id] = current_data
        return True

    # ---------------------------
    # Aggregations / statistics
    # ---------------------------
    def count_by_gender(self) -> Dict[str, int]:
        """Count the number of users by gender."""
        gender_counts: Dict[str, int] = {}
        for user in self.hash_map.values():
            gender = user.get("gender") or "Unknown"
            gender_counts[gender] = gender_counts.get(gender, 0) + 1
        return gender_counts

    def average_age_by_gender(self) -> Dict[str, float]:
        """Calculate the average age for each gender group."""
        age_by_gender: Dict[str, int] = {}
        count_by_gender: Dict[str, int] = {}
        for user in self.hash_map.values():
            gender = user.get("gender") or "Unknown"
            age = user.get("age")
            if age is None:
                continue
            age_by_gender[gender] = age_by_gender.get(gender, 0) + age
            count_by_gender[gender] = count_by_gender.get(gender, 0) + 1

        result: Dict[str, float] = {}
        for gender, total_age in age_by_gender.items():
            cnt = count_by_gender.get(gender, 0)
            if cnt > 0:
                result[gender] = total_age / cnt
        return result

    def top_educations(self, top_k: int = 10) -> List[tuple]:
        """Get the top K most common education levels as (education, count)."""
        education_counts: Dict[str, int] = {}
        for user in self.hash_map.values():
            education = user.get("education")
            if education:
                education_counts[education] = education_counts.get(education, 0) + 1

        sorted_educations = sorted(
            education_counts.items(), key=lambda x: x[1], reverse=True
        )
        return sorted_educations[:top_k]

    def top_music_preferences(self, top_k: int = 10) -> List[tuple]:
        """Get the top K most common music preferences."""
        music_counts: Dict[str, int] = {}
        for user in self.hash_map.values():
            music_str = user.get("music")
            if music_str:
                musics = [m.strip() for m in music_str.split(",")]
                for music in musics:
                    if music:
                        music_counts[music] = music_counts.get(music, 0) + 1

        sorted_music = sorted(music_counts.items(), key=lambda x: x[1], reverse=True)
        return sorted_music[:top_k]

    def top_k_most_connected(self, k: int = 10) -> List[tuple]:
        """Return top k users with the most friends: list of (user_id, friend_count)."""
        users = []
        for user in self.hash_map.values():
            uid = user["user_id"]
            friends = self.get_friends(uid) or []
            users.append((uid, len(friends)))
        users.sort(key=lambda x: x[1], reverse=True)
        return users[:k]

    def top_k_least_connected(self, k: int = 10) -> List[tuple]:
        """Return top k users with the fewest friends: list of (user_id, friend_count)."""
        users = []
        for user in self.hash_map.values():
            uid = user["user_id"]
            friends = self.get_friends(uid) or []
            users.append((uid, len(friends)))
        users.sort(key=lambda x: x[1])
        return users[:k]

    def average_number_of_friends(self) -> float:
        """Return the average number of friends per user."""
        friend_counts = [len(self.get_friends(user["user_id"])) for user in self.hash_map.values()]
        if not friend_counts:
            return 0.0
        return sum(friend_counts) / len(friend_counts)

    def median_number_of_friends(self) -> float:
        """Return the median number of friends per user."""
        friend_counts = [len(self.get_friends(user["user_id"])) for user in self.hash_map.values()]
        if not friend_counts:
            return 0.0
        return statistics.median(friend_counts)

    def degree_distribution(self) -> Dict[int, int]:
        """Return a histogram of friend counts (degree distribution)."""
        friend_counts = [len(self.get_friends(user["user_id"])) for user in self.hash_map.values()]
        distribution: Dict[int, int] = {}
        for count in friend_counts:
            distribution[count] = distribution.get(count, 0) + 1
        return distribution

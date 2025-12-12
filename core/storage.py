import csv
import sys
import os
import time
from typing import Dict, Any, Optional, List, Iterable
import statistics

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from indexing import AVLTree
from graph import Graph

class Storage:
    def __init__(self, data_path: str, relationship_path: str):
        self.data_path = data_path
        self.relationship_path = relationship_path
        self.hash_map: Dict[int, Dict[str, Any]] = {}
        self.age_index = AVLTree()
        self.social_graph = Graph()
        self.is_loaded = False

    def initialize(self):
        self._load_user_data()
        self._load_relationships()
        self.is_loaded = True

    def _load_user_data(self):
        data_file_path = self.data_path

        if not os.path.exists(data_file_path):
            print("=" * 80)
            print(f"CRITICAL ERROR: User profile file not found at: {data_file_path}")
            print("=" * 80)
            sys.exit(1)

        row_count = 0
        update_interval = 100000

        print("Loading user profile data and building AVL index...")
        start_time = time.time()

        with open(data_file_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                row_count += 1

                if row_count % update_interval == 0:
                    print(f"Loading profiles: {row_count:,} records processed...")

                try:
                    raw_user_id = row.get("user_id")
                    if not raw_user_id:
                        continue
                    user_id = int(float(raw_user_id))

                    raw_age = row.get("age")
                    age = None
                    if raw_age:
                        try:
                            age_val = float(raw_age)
                            if age_val > 0:
                                age = int(age_val)
                        except ValueError:
                            pass

                    user_data = {
                        "user_id": user_id,
                        "gender": row.get("gender"),
                        "age": age,
                        "eye_color": row.get("eye_color"),
                        "education": row.get("education"),
                        "languages": row.get("languages"),
                        "music": row.get("music"),
                    }
                    
                    self.hash_map[user_id] = user_data

                    if age is not None:
                        self.age_index.insert(age, user_id)

                except (ValueError, TypeError, KeyError) as e:
                    print(f"Skipping bad profile row {row_count} due to error: {e}")
                    continue

        end_time = time.time()
        print(f"Finished processing {row_count:,} total user profiles.")
        print(f"User data loaded and AVL Index built. Time taken: {end_time - start_time:.4f} seconds.")

    def _load_relationships(self):
        relationship_file_path = self.relationship_path

        if not os.path.exists(relationship_file_path):
            print("=" * 80)
            print(f"CRITICAL ERROR: Relationship file not found at: {relationship_file_path}")
            print(f"Social Graph will be empty.")
            print("=" * 80)
            return

        edge_count = 0
        update_interval = 1000000

        print("\nLoading relationships and building Social Graph...")
        start_time = time.time()

        with open(relationship_file_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                edge_count += 1

                if edge_count % update_interval == 0:
                    print(f"Loading relationships: {edge_count:,} edges processed...")
                
                try:
                    source_id = int(float(row.get("source_user_id")))
                    target_id = int(float(row.get("target_user_id")))

                    self.social_graph.add_edge(source_id, target_id)

                except (ValueError, TypeError, KeyError) as e:
                    pass

        end_time = time.time()
        print(f"Finished processing {edge_count:,} total relationships.")
        print(f"Social Graph built. Time taken: {end_time - start_time:.4f} seconds.")

    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        return self.hash_map.get(user_id)

    def get_all_records(self, record_ids: Iterable[int]) -> List[Dict[str, Any]]:
        return [self.hash_map[uid] for uid in record_ids if uid in self.hash_map]

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

        user_ids = self.age_index.range_query(min_age, max_age)
        return self.get_all_records(user_ids)

    def find_shortest_path(self, user_a_id: int, user_b_id: int) -> List[int]:
        return self.social_graph.shortest_path(user_a_id, user_b_id)

    def get_friends(self, user_id: int) -> List[int]:
        return self.social_graph.get_neighbors(user_id)

    def add_user(self, user_data: Dict[str, Any]) -> None:
        user_id = user_data.get("user_id")
        if user_id is None or user_id in self.hash_map:
            raise ValueError(f"User ID {user_id} is invalid or already exists.")

        friend_ids = user_data.get("friend_ids") or user_data.get("friends") or []
        parsed_friend_ids: List[int] = []
        if isinstance(friend_ids, str):
            for fid_str in friend_ids.split(";"):
                fid_str = fid_str.strip()
                if fid_str and fid_str.replace(".", "", 1).isdigit():
                    parsed_friend_ids.append(int(float(fid_str)))
        elif isinstance(friend_ids, Iterable):
            for fid in friend_ids:
                try:
                    parsed_friend_ids.append(int(fid))
                except Exception:
                    continue

        self.hash_map[user_id] = user_data

        age = user_data.get("age")
        if age is not None:
            self.age_index.insert(age, user_id)

        for fid in parsed_friend_ids:
            self.social_graph.add_edge(user_id, fid)

    def delete_user(self, user_id: int) -> bool:
        if user_id not in self.hash_map:
            return False

        user_data = self.hash_map.pop(user_id)
        age = user_data.get("age")

        if age is not None:
            try:
                self.age_index.delete_record_id(age, user_id)
            except AttributeError:
                pass

        self.social_graph.remove_node(user_id)
        return True

    def modify_user(self, user_id: int, updates: Dict[str, Any]) -> bool:
        if user_id not in self.hash_map:
            return False

        current_data = self.hash_map[user_id]
        old_age = current_data.get("age")
        new_age = updates.get("age", old_age)

        if new_age is not None and new_age != old_age:
            if old_age is not None:
                try:
                    self.age_index.delete_record_id(old_age, user_id)
                except AttributeError:
                    pass
            current_data["age"] = new_age
            self.age_index.insert(new_age, user_id)

        for key, value in updates.items():
            if key != "age":
                current_data[key] = value

        self.hash_map[user_id] = current_data
        return True

    def count_by_gender(self) -> Dict[str, int]:
        gender_counts: Dict[str, int] = {}
        for user in self.hash_map.values():
            gender = user.get("gender") or "Unknown"
            gender_counts[gender] = gender_counts.get(gender, 0) + 1
        return gender_counts

    def average_age_by_gender(self) -> Dict[str, float]:
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
        education_counts: Dict[str, int] = {}
        for user in self.hash_map.values():
            education = user.get("education")
            if education:
                education_counts[education] = education_counts.get(education, 0) + 1

        sorted_educations = sorted(
            education_counts.items(), key=lambda x: x[1], reverse=True
        )
        return sorted_educations[:top_k]
    
    def top_languages(self, top_k: int = 10) -> List[tuple]:
        language_counts: Dict[str, int] = {}
        for user in self.hash_map.values():
            languages_str = user.get("languages")
            if languages_str:
                for lang in [l.strip() for l in languages_str.split(",")]:
                    if lang:
                        language_counts[lang] = language_counts.get(lang, 0) + 1

        sorted_languages = sorted(
            language_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )
        return sorted_languages[:top_k]

    def top_music_preferences(self, top_k: int = 10) -> List[tuple]:
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
        users = []
        for user in self.hash_map.values():
            uid = user["user_id"]
            friends = self.get_friends(uid) or []
            users.append((uid, len(friends)))
        users.sort(key=lambda x: x[1], reverse=True)
        return users[:k]

    def top_k_least_connected(self, k: int = 10) -> List[tuple]:
        users = []
        for user in self.hash_map.values():
            uid = user["user_id"]
            friends = self.get_friends(uid) or []
            users.append((uid, len(friends)))
        users.sort(key=lambda x: x[1])
        return users[:k]

    def average_number_of_friends(self) -> float:
        friend_counts = [len(self.get_friends(user["user_id"])) for user in self.hash_map.values()]
        if not friend_counts:
            return 0.0
        return sum(friend_counts) / len(friend_counts)

    def median_number_of_friends(self) -> float:
        friend_counts = [len(self.get_friends(user["user_id"])) for user in self.hash_map.values()]
        if not friend_counts:
            return 0.0
        return statistics.median(friend_counts)

    def degree_distribution(self) -> Dict[int, int]:
        friend_counts = [len(self.get_friends(user["user_id"])) for user in self.hash_map.values()]
        distribution: Dict[int, int] = {}
        for count in friend_counts:
            distribution[count] = distribution.get(count, 0) + 1
        return distribution
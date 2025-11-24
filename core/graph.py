import collections

class Graph:
    def __init__(self, relationships_path):
        self.relationships_path = relationships_path
        self.graph = collections.defaultdict(list)
        self.users = set()

    def initialize(self):
        self._load_relationships()

    def _load_relationships(self):
        with open(self.relationships_path, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    u1, u2 = map(int, line.strip().split())
                    self.graph[u1].append(u2)
                    self.graph[u2].append(u1)
                    self.users.add(u1)
                    self.users.add(u2)
                except ValueError:
                    pass

    def add_edge(self, u1, u2):
        if u2 not in self.graph[u1]:
            self.graph[u1].append(u2)
            self.users.add(u1)
        if u1 not in self.graph[u2]:
            self.graph[u2].append(u1)
            self.users.add(u2)

    def remove_user(self, user_id):
        if user_id in self.graph:
            for friend_id in list(self.graph[user_id]):
                if friend_id in self.graph and user_id in self.graph[friend_id]:
                    self.graph[friend_id].remove(user_id)
            
            del self.graph[user_id]
            self.users.discard(user_id)
            return True
        return False

    def find_shortest_path(self, start_id, end_id):
        if start_id == end_id:
            return [start_id]
        if start_id not in self.graph or end_id not in self.graph:
            return None

        queue = collections.deque([start_id])
        visited = {start_id}
        parent = {start_id: None}
        
        while queue:
            current_id = queue.popleft()

            if current_id == end_id:
                path = []
                while current_id is not None:
                    path.append(current_id)
                    current_id = parent[current_id]
                return path[::-1]

            for neighbor_id in self.graph[current_id]:
                if neighbor_id not in visited:
                    visited.add(neighbor_id)
                    parent[neighbor_id] = current_id
                    queue.append(neighbor_id)
        
        return None

    def depth_first_traversal(self, start_id):
        if start_id not in self.graph:
            return []
        
        visited = set()
        traversal_order = []
        stack = [start_id]
        [Image of Depth First Search (DFS) Traversal]
        while stack:
            current_id = stack.pop()
            if current_id not in visited:
                visited.add(current_id)
                traversal_order.append(current_id)
                for neighbor in sorted(self.graph[current_id], reverse=True):
                    if neighbor not in visited:
                        stack.append(neighbor)
        
        return traversal_order

    def calculate_local_clustering_coefficient(self, user_id):
        neighbors = self.graph.get(user_id, [])
        k = len(neighbors)
        if k < 2:
            return 0.0

        max_edges = k * (k - 1) / 2
        
        existing_edges = 0
        
        for i in range(k):
            for j in range(i + 1, k):
                neighbor_u = neighbors[i]
                neighbor_v = neighbors[j]
                
                if neighbor_v in self.graph.get(neighbor_u, []):
                    existing_edges += 1
        
        return existing_edges / max_edges if max_edges > 0 else 0.0

    def calculate_degree_centrality(self, user_id):
        return len(self.graph.get(user_id, []))

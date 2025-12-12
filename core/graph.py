import collections
from typing import List, Optional, Dict

class Graph:
    def __init__(self):
        self.friends = collections.defaultdict(list)
        self.followers = collections.defaultdict(list)
        self.nodes = set()

    def add_edge(self, user_a: int, user_b: int) -> None:
        self.friends[user_a].append(user_b)
        self.followers[user_b].append(user_a)
        self.nodes.add(user_a)
        self.nodes.add(user_b)

    def remove_node(self, user_id: int) -> None:
        if user_id not in self.nodes:
            return

        if user_id in self.friends:
            for target in self.friends[user_id]:
                if user_id in self.followers[target]:
                    self.followers[target].remove(user_id)
            del self.friends[user_id]

        if user_id in self.followers:
            for src in self.followers[user_id]:
                if user_id in self.friends[src]:
                    self.friends[src].remove(user_id)
            del self.followers[user_id]

        self.nodes.remove(user_id)

    def get_neighbors(self, user_id: int) -> List[int]:
        return self.friends.get(user_id, [])

    def followers_of(self, user_id: int) -> List[int]:
        return self.followers.get(user_id, [])

    def shortest_path(self, start_user: int, end_user: int) -> Optional[List[int]]:
        if start_user == end_user:
            return [start_user]

        if start_user not in self.nodes or end_user not in self.nodes:
            return None

        queue = collections.deque([(start_user, [start_user])])
        visited = {start_user}

        while queue:
            node, path = queue.popleft()
            for neighbor in self.friends.get(node, []):
                if neighbor == end_user:
                    return path + [end_user]
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))

        return None

    def bfs_traversal(self, start_user: int) -> List[int]:
        if start_user not in self.nodes:
            return []

        queue = collections.deque([start_user])
        visited = {start_user}
        order = []

        while queue:
            node = queue.popleft()
            order.append(node)

            for neighbor in self.friends.get(node, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)

        return order

    def common_friends(self, user1: int, user2: int) -> List[int]:
        set1 = set(self.friends.get(user1, []))
        set2 = set(self.friends.get(user2, []))
        return list(set1 & set2)

    def is_mutual_friendship(self, user1: int, user2: int) -> bool:
        return (user2 in self.friends.get(user1, [])) and \
               (user1 in self.friends.get(user2, []))

    def _dfs_order(self, node: int, visited: set, stack: List[int]) -> None:
        visited.add(node)
        for nxt in self.friends.get(node, []):
            if nxt not in visited:
                self._dfs_order(nxt, visited, stack)
        stack.append(node)

    def _dfs_collect(self, node: int, visited: set, comp: List[int], reverse_graph: Dict) -> None:
        visited.add(node)
        comp.append(node)
        for nxt in reverse_graph.get(node, []):
            if nxt not in visited:
                self._dfs_collect(nxt, visited, comp, reverse_graph)

    def strongly_connected_components(self) -> List[List[int]]:
        visited = set()
        order_stack = []

        for n in self.nodes:
            if n not in visited:
                self._dfs_order(n, visited, order_stack)

        reverse_graph = self.followers

        visited.clear()
        scc_list = []

        while order_stack:
            node = order_stack.pop()
            if node not in visited:
                comp = []
                self._dfs_collect(node, visited, comp, reverse_graph)
                scc_list.append(comp)

        return scc_list
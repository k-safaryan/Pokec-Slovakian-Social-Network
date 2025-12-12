import collections

class Graph:
    def __init__(self):
        self.adj = collections.defaultdict(list)
        self.parents = {} 
        self.nodes = set()

    def add_edge(self, manager_id, employee_id):
        self.adj[manager_id].append(employee_id)
        self.parents[employee_id] = manager_id 
        self.nodes.add(manager_id)
        self.nodes.add(employee_id)

    def remove_node(self, node_id):
        if node_id in self.parents:
            del self.parents[node_id]

        if node_id in self.nodes:
            self.nodes.remove(node_id)

        if node_id in self.adj:
            del self.adj[node_id]

        for manager_id, employees in list(self.adj.items()):
            if node_id in employees:
                employees.remove(node_id)

    def get_neighbors(self, node_id):
        return self.adj.get(node_id, [])

    def find_path_up_to_root(self, start_node):
        if start_node not in self.nodes:
            return []
            
        path = [start_node]
        current = start_node
        
        while current in self.parents:
            manager = self.parents[current]
            path.append(manager)
            current = manager

        return path[::-1]

    def bfs_traversal(self, start_node):
        if start_node not in self.nodes:
            return []

        queue = collections.deque([start_node])
        visited = {start_node}
        traversal_order = []

        while queue:
            node = queue.popleft()
            traversal_order.append(node)

            for neighbor in self.adj.get(node, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
        
        return traversal_order

    def shortest_path(self, start_node, end_node):
        if start_node == end_node:
            return [start_node]
        if start_node not in self.nodes or end_node not in self.nodes:
            return None

        queue = collections.deque([(start_node, [start_node])])
        visited = {start_node}

        while queue:
            current_node, path = queue.popleft()

            for neighbor in self.adj.get(current_node, []):
                if neighbor == end_node:
                    return path + [end_node]
                
                if neighbor not in visited:
                    visited.add(neighbor)
                    new_path = path + [neighbor]
                    queue.append((neighbor, new_path))
                    
        return None

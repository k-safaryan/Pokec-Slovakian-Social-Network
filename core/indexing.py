class AVLNode:
    def __init__(self, key, record_id):
        self.key = key
        self.record_ids = [record_id]
        self.left = None
        self.right = None
        self.height = 1
        self.balance = 0

class AVLTree:
    def __init__(self):
        self.root = None

    def _get_height(self, node):
        return node.height if node else 0

    def _update_height(self, node):
        node.height = 1 + max(self._get_height(node.left), self._get_height(node.right))
        node.balance = self._get_height(node.left) - self._get_height(node.right)

    def _rotate_left(self, z):
        y = z.right
        T2 = y.left
        z.right = T2
        y.left = z
        self._update_height(z)
        self._update_height(y)
        return y

    def _rotate_right(self, z):
        y = z.left
        T3 = y.right
        z.left = T3
        y.right = z
        self._update_height(z)
        self._update_height(y)
        return y

    def insert(self, key, record_id):
        self.root = self._insert_recursive(self.root, key, record_id)

    def _insert_recursive(self, node, key, record_id):
        if not node:
            return AVLNode(key, record_id)

        if key < node.key:
            node.left = self._insert_recursive(node.left, key, record_id)
        elif key > node.key:
            node.right = self._insert_recursive(node.right, key, record_id)
        else:
            if record_id not in node.record_ids:
                node.record_ids.append(record_id)
            return node

        self._update_height(node)

        balance = node.balance

        if balance > 1 and key < node.left.key:
            return self._rotate_right(node)
        if balance < -1 and key > node.right.key:
            return self._rotate_left(node)
        if balance > 1 and key > node.left.key:
            node.left = self._rotate_left(node.left)
            return self._rotate_right(node)
        if balance < -1 and key < node.right.key:
            node.right = self._rotate_right(node.right)
            return self._rotate_left(node)

        return node

    def search(self, key):
        node = self._search_recursive(self.root, key)
        return node.record_ids if node else None

    def _search_recursive(self, node, key):
        if not node or node.key == key:
            return node
        if key < node.key:
            return self._search_recursive(node.left, key)
        return self._search_recursive(node.right, key)

    def range_query(self, min_key, max_key):
        results = []
        self._range_query_recursive(self.root, min_key, max_key, results)
        return results

    def _range_query_recursive(self, node, min_key, max_key, results):
        if not node:
            return

        if min_key < node.key:
            self._range_query_recursive(node.left, min_key, max_key, results)

        if min_key <= node.key <= max_key:
            results.extend(node.record_ids)

        if max_key > node.key:
            self._range_query_recursive(node.right, min_key, max_key, results)

    def delete_record_id(self, key, record_id):
        node = self._search_recursive(self.root, key)
        if node:
            try:
                node.record_ids.remove(record_id)
                return True
            except ValueError:
                return False
        return False
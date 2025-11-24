class AVLNode:
    def __init__(self, key, value):
        self.key = key
        self.values = [value]
        self.height = 1
        self.left = None
        self.right = None

class AVLTree:
    def __init__(self):
        self.root = None

    def get_height(self, node):
        return node.height if node else 0

    def get_balance(self, node):
        return self.get_height(node.left) - self.get_height(node.right) if node else 0

    def update_height(self, node):
        node.height = 1 + max(self.get_height(node.left), self.get_height(node.right))

    def rotate_left(self, z):
        y = z.right
        T2 = y.left
        y.left = z
        z.right = T2
        self.update_height(z)
        self.update_height(y)
        return y

    def rotate_right(self, z):
        y = z.left
        T3 = y.right
        y.right = z
        z.left = T3
        self.update_height(z)
        self.update_height(y)
        return y

    def rebalance(self, node, key, value):
        self.update_height(node)
        balance = self.get_balance(node)

        if balance > 1:
            if key < node.left.key:
                return self.rotate_right(node)
            else:
                node.left = self.rotate_left(node.left)
                return self.rotate_right(node)

        if balance < -1:
            if key > node.right.key:
                return self.rotate_left(node)
            else:
                node.right = self.rotate_right(node.right)
                return self.rotate_left(node)

        return node

    def add(self, key, value):
        self.root = self._add(self.root, key, value)

    def _add(self, node, key, value):
        if not node:
            return AVLNode(key, value)
        
        if key < node.key:
            node.left = self._add(node.left, key, value)
        elif key > node.key:
            node.right = self._add(node.right, key, value)
        else:
            node.values.append(value)
            return node

        return self.rebalance(node, key, value)

    def range_search(self, node, min_key, max_key, results):
        if not node:
            return

        if min_key < node.key:
            self.range_search(node.left, min_key, max_key, results)

        if min_key <= node.key <= max_key:
            results.extend(node.values)

        if max_key > node.key:
            self.range_search(node.right, min_key, max_key, results)

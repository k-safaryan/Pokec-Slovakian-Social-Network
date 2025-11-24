import collections

class _Node:
    def __init__(self, key, value, height=1, left=None, right=None, parent=None):
        self.key = key
        self.value = [value]
        self.height = height
        self.left = left
        self.right = right
        self.parent = parent

class AVLTree:
    def __init__(self):
        self.root = None
        self.size = 0

    def _height(self, node):
        return node.height if node else 0

    def _balance_factor(self, node):
        if not node:
            return 0
        return self._height(node.left) - self._height(node.right)

    def _update_height(self, node):
        if node:
            node.height = 1 + max(self._height(node.left), self._height(node.right))

    def _rotate_left(self, z):
        y = z.right
        T2 = y.left

        y.left = z
        z.right = T2

        y.parent = z.parent
        if z.parent is None:
            self.root = y
        elif z == z.parent.left:
            z.parent.left = y
        else:
            z.parent.right = y
        
        z.parent = y
        if T2:
            T2.parent = z

        self._update_height(z)
        self._update_height(y)
        return y

    def _rotate_right(self, z):
        y = z.left
        T3 = y.right

        y.right = z
        z.left = T3

        y.parent = z.parent
        if z.parent is None:
            self.root = y
        elif z == z.parent.left:
            z.parent.left = y
        else:
            z.parent.right = y
        
        z.parent = y
        if T3:
            T3.parent = z

        self._update_height(z)
        self._update_height(y)
        return y

    def _rebalance(self, node):
        if node is None:
            return

        self._update_height(node)
        balance = self._balance_factor(node)

        if balance > 1:
            if self._balance_factor(node.left) < 0:
                node.left = self._rotate_left(node.left)
            return self._rotate_right(node)

        if balance < -1:
            if self._balance_factor(node.right) > 0:
                node.right = self._rotate_right(node.right)
            return self._rotate_left(node)

        return node

    def add(self, key, value):
        if self.root is None:
            self.root = _Node(key, value)
            self.size += 1
            return

        def _insert_recursive(node, key, value, parent):
            if node is None:
                self.size += 1
                return _Node(key, value, parent=parent)
            
            node.parent = parent

            if key < node.key:
                node.left = _insert_recursive(node.left, key, value, node)
            elif key > node.key:
                node.right = _insert_recursive(node.right, key, value, node)
            else:
                node.value.append(value)
                return node

            return self._rebalance(node)

        self.root = _insert_recursive(self.root, key, value, None)

    def _min_node(self, node):
        current = node
        while current.left is not None:
            current = current.left
        return current

    def delete(self, key, value_to_remove=None):
        if not self.root:
            return

        def _delete_recursive(node, key):
            if node is None:
                return node
            
            if key < node.key:
                node.left = _delete_recursive(node.left, key)
            elif key > node.key:
                node.right = _delete_recursive(node.right, key)
            else:
                if value_to_remove is not None and value_to_remove in node.value:
                    node.value.remove(value_to_remove)
                    if node.value:
                        return self._rebalance(node)

                if not node.left and not node.right:
                    self.size -= 1
                    return None
                
                elif not node.left:
                    self.size -= 1
                    child = node.right
                    child.parent = node.parent
                    return child
                
                elif not node.right:
                    self.size -= 1
                    child = node.left
                    child.parent = node.parent
                    return child
                
                else:
                    successor = self._min_node(node.right)
                    node.key = successor.key
                    node.value = successor.value
                    successor.value = []
                    node.right = _delete_recursive(node.right, successor.key)
            
            return self._rebalance(node)

        self.root = _delete_recursive(self.root, key)
        if self.root:
            self.root.parent = None

    def range_search(self, min_key, max_key):
        results = []

        def _traverse(node):
            if node is None:
                return

            if node.key > min_key:
                _traverse(node.left)

            if min_key <= node.key <= max_key:
                results.extend(node.value)

            if node.key < max_key:
                _traverse(node.right)

        _traverse(self.root)
        return results

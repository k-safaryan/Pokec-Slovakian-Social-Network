class AVLNode:
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.left = None
        self.right = None
        self.height = 1

class AVLTree:
    def __init__(self):
        self.root = None
        self.size = 0

    def get_height(self, node):
        if not node:
            return 0
        return node.height

    def get_balance(self, node):
        if not node:
            return 0
        return self.get_height(node.left) - self.get_height(node.right)

    def update_height(self, node):
        node.height = 1 + max(self.get_height(node.left), self.get_height(node.right))

    def rotate_right(self, y):
        x = y.left
        T2 = x.right

        x.right = y
        y.left = T2

        self.update_height(y)
        self.update_height(x)

        return x

    def rotate_left(self, x):
        y = x.right
        T2 = y.left

        y.left = x
        x.right = T2

        self.update_height(x)
        self.update_height(y)

        return y

    def insert(self, root, key, user_id):
        if not root:
            self.size += 1
            return AVLNode(key, [user_id])
        
        if key < root.key:
            root.left = self.insert(root.left, key, user_id)
        elif key > root.key:
            root.right = self.insert(root.right, key, user_id)
        else:
            root.value.append(user_id)
            return root

        self.update_height(root)

        balance = self.get_balance(root)

        if balance > 1 and key < root.left.key:
            return self.rotate_right(root)

        if balance < -1 and key > root.right.key:
            return self.rotate_left(root)

        if balance > 1 and key > root.left.key:
            root.left = self.rotate_left(root.left)
            return self.rotate_right(root)

        if balance < -1 and key < root.right.key:
            root.right = self.rotate_right(root.right)
            return self.rotate_left(root)

        return root
    
    def add(self, key, user_id):
        self.root = self.insert(self.root, key, user_id)

    def range_search(self, root, low, high, results):
        if root is None:
            return

        if root.key > low:
            self.range_search(root.left, low, high, results)

        if low <= root.key <= high:
            results.extend(root.value)

        if root.key < high:
            self.range_search(root.right, low, high, results)
            try:
                node.record_ids.remove(record_id)
                return True
            except ValueError:
                return False
        return False

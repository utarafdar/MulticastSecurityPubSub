import random


def generate_key():
    return random.randint(1000, 9999)


class TreeNode:
    def __init__(self, node_id, root_node=False):
        self.node_id = node_id
        self.node_key = generate_key()  # kept this for the rest of stuff to not break, later delete it
        self.node_keys = {}
        self.root_node = root_node

    def set_node_keys(self, node_keys):
        self.node_keys = node_keys.copy()

    def reset_key(self):
        self.node_key = generate_key()


class LeafNode(TreeNode):
    def __init__(self, node_id, participant=None):
        super().__init__(node_id)
        self.participant = participant


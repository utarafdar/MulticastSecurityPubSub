import random


def generate_key():
    return random.randint(1000, 9999)


class TreeNode:
    def __init__(self, node_id, root_node=False, depth=None, no_of_children=None,):
        self.node_id = node_id
        self.node_key = generate_key()  # kept this for the rest of stuff to not break, later delete it
        self.node_common_key = None
        self.node_publisher_keys = None  # empty or None checkout
        self.node_subscriber_keys = None
        self.root_node = root_node
        self.depth = depth
        self.no_of_children = no_of_children

    def set_node_common_key(self, common_key):
        self.node_common_key = common_key

    def set_node_publisher_keys(self, publisher_keys):
        self.node_publisher_keys = publisher_keys.copy()

    def set_node_subscriber_keys(self, subscriber_keys):
        self.node_subscriber_keys = subscriber_keys.copy()

    def reset_key(self):
        self.node_key = generate_key()


class LeafNode(TreeNode):
    def __init__(self, node_id, participant=None):
        super().__init__(node_id)
        self.participant = participant


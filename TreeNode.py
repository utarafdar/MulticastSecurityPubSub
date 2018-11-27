import random


def generate_key():
    return random.randint(1000, 9999)


class TreeNode:
    def __init__(self, node_id):
        self.node_id = node_id
        self.node_key = generate_key()


class LeafNode(TreeNode):
    def __init__(self, node_id, participant):
        super().__init__(node_id)
        self.participant = participant


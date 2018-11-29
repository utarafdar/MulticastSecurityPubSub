from anytree import Node

from TreeNode import TreeNode


class Topic:

    def __init__(self, topic_name, depth=None, no_of_children=None, root_node=None):
        self.topicName = topic_name
        if root_node is None:
            root_node = TreeNode('0')
        self.root_tree = Node(topic_name, tree_node=root_node)
        self.depth = depth
        self.no_of_children = no_of_children

    # @property
    # def email(self):
    #     return '{}.{}@email.com'.format(self.first, self.last)
    #
    # @property
    # def fullname(self):
    #     return '{} {}'.format(self.first, self.last)



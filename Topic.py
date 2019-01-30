from anytree import Node
import uuid
from TreeNode import TreeNode
from CustomEnums import TypeOfPubSubGroupEnum

class Topic:

    def __init__(self, topic_name, depth=None, no_of_children=None, root_node=None, type_of_pub_sub_group=TypeOfPubSubGroupEnum.ALL_PUBSUB):
        self.topicName = topic_name
        if root_node is None:
            root_node = TreeNode('0') # keeo it so that other stuff does not break, delete later after testing
        self.root_tree = Node(topic_name, tree_node=root_node)
        self.depth = depth
        self.no_of_children = no_of_children
        # change this when permissions change
        self.type_of_pub_sub_group = type_of_pub_sub_group
        self.id = uuid.uuid4()
        self.root_tree_common = None
        self.root_tree_publishers = None
        self.root_tree_subscribers = None

    def set_root_tree_common(self, root_node_common):
        self.root_tree_common = root_node_common

    def set_root_tree_publishers(self, root_node_publishers):
        self.root_tree_publishers = root_node_publishers

    def set_root_tree_subscribers(self, root_node_subscribers):
        self.root_tree_publishers = root_node_subscribers
    # @property
    # def email(self):
    #     return '{}.{}@email.com'.format(self.first, self.last)
    #
    # @property
    # def fullname(self):
    #     return '{} {}'.format(self.first, self.last)



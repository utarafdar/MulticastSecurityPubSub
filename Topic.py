from anytree import Node
import uuid
from TreeNode import TreeNode
from CustomEnums import TypeOfPubSubGroupEnum

class Topic:

    def __init__(self, topic_name, depth=None, no_of_children=None, root_node=None, type_of_pub_sub_group=TypeOfPubSubGroupEnum.ALL_PUBSUB):
        self.topicName = topic_name
        if root_node is None:
            root_node = TreeNode('0')
        self.root_tree = Node(topic_name, tree_node=root_node)
        self.depth = depth
        self.no_of_children = no_of_children
        # change this when permissions change
        self.type_of_pub_sub_group = type_of_pub_sub_group
        self.id = uuid.uuid4()
    # @property
    # def email(self):
    #     return '{}.{}@email.com'.format(self.first, self.last)
    #
    # @property
    # def fullname(self):
    #     return '{} {}'.format(self.first, self.last)



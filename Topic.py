from anytree import Node
import uuid
from TreeNode import TreeNode
from CustomEnums import TypeOfPubSubGroupEnum


class Topic:

    # todo -- switch depth and number of children to tree class, makes more sense there
    def __init__(self, topic_name, depth=None, no_of_children=None, root_node=None, type_of_pub_sub_group=TypeOfPubSubGroupEnum.ALL_PUBSUB):
        self.topicName = topic_name
        if root_node is None:
            root_node = TreeNode('0')  # keep it so that other stuff does not break, delete later after testing
        self.root_tree = Node(topic_name, tree_node=root_node)
        self.depth = depth
        self.no_of_children = no_of_children
        # change this when permissions change
        self.type_of_pub_sub_group = type_of_pub_sub_group
        self.id = uuid.uuid4()
        self.root_tree_common = None
        self.root_tree_publishers = None
        self.root_tree_subscribers = None
        self.root_tree_pub_sub = None
        # a way to set no of children and depth for individual groups
        self.no_of_children_common_tree = None
        self.depth_common_tree = None
        self.no_of_children_publisher_tree = None
        self.depth_publisher_tree = None
        self.no_of_children_subscriber_tree = None
        self.depth_subscriber_tree = None
        self.edge_case_one_publisher_keys = None
        self.edge_case_one_subscriber_keys = None

    def set_root_tree_common(self, root_node_common, no_of_children_common_tree=None, depth_common_tree=None):
        self.root_tree_common = Node(self.topicName, tree_node=root_node_common)
        #self.root_tree_common = root_node_common
        self.no_of_children_common_tree = no_of_children_common_tree
        self.depth_common_tree = depth_common_tree

    def set_root_tree_publishers(self, root_node_publishers, no_of_children_publisher_tree=None, depth_publisher_tree=None):
        self.root_tree_publishers = Node(self.topicName, tree_node=root_node_publishers)
        #self.root_tree_publishers = root_node_publishers
        self.no_of_children_publisher_tree = no_of_children_publisher_tree
        self.depth_publisher_tree = depth_publisher_tree

    def set_root_tree_subscribers(self, root_node_subscribers, no_of_children_subscriber_tree=None, depth_subscriber_tree=None):
        self.root_tree_subscribers = Node(self.topicName, tree_node=root_node_subscribers)
        #self.root_tree_subscribers = root_node_subscribers
        self.no_of_children_subscriber_tree = no_of_children_subscriber_tree
        self.depth_subscriber_tree = depth_subscriber_tree

    def set_root_tree_pub_sub(self, root_node_pub_sub, no_of_children_publisher_tree=None, depth_publisher_tree=None):
        self.root_tree_pub_sub = Node(self.topicName, tree_node=root_node_pub_sub)
        #self.root_tree_publishers = root_node_publishers
        self.no_of_children_publisher_tree = no_of_children_publisher_tree
        self.depth_publisher_tree = depth_publisher_tree
    # @property
    # def email(self):
    #     return '{}.{}@email.com'.format(self.first, self.last)
    #
    # @property
    # def fullname(self):
    #     return '{} {}'.format(self.first, self.last)



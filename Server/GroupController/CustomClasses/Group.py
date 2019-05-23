from anytree import Node
import uuid
from CustomEnums import TypeOfPubSubGroupEnum
from Topic import Topic
from Participant import Participant


class Group:

    def __init__(self, group_name, group_id=None, type_of_pub_sub_group=TypeOfPubSubGroupEnum.ALL_PUBSUB):
        self.group_name = group_name
        self.type_of_pub_sub_group = type_of_pub_sub_group
        if group_id is None:
            self.id = uuid.uuid4()
        else:
            self.id = group_id

        """  
        self.root_tree_common = None
        self.root_tree_publishers = None
        self.root_tree_subscribers = None
        self.root_tree_pub_sub = None"""
        # topics are part of the group
        self.topics = list()
        self.participants_permissions = dict()
        # a way to set no of children and depth for individual groups
        # remove these after resolving
        """ self.no_of_children_common_tree = None
        self.depth_common_tree = None
        self.no_of_children_publisher_tree = None
        self.depth_publisher_tree = None
        self.no_of_children_subscriber_tree = None
        self.depth_subscriber_tree = None
        self.edge_case_one_publisher_keys = None
        self.edge_case_one_subscriber_keys = None"""

    """ def set_root_tree_common(self, root_node_common, no_of_children_common_tree=None, depth_common_tree=None):
        self.root_tree_common = Node(self.group_name, tree_node=root_node_common)
        #self.root_tree_common = root_node_common
        self.no_of_children_common_tree = no_of_children_common_tree
        self.depth_common_tree = depth_common_tree

    def set_root_tree_publishers(self, root_node_publishers, no_of_children_publisher_tree=None, depth_publisher_tree=None):
        self.root_tree_publishers = Node(self.group_name, tree_node=root_node_publishers)
        #self.root_tree_publishers = root_node_publishers
        self.no_of_children_publisher_tree = no_of_children_publisher_tree
        self.depth_publisher_tree = depth_publisher_tree

    def set_root_tree_subscribers(self, root_node_subscribers, no_of_children_subscriber_tree=None, depth_subscriber_tree=None):
        self.root_tree_subscribers = Node(self.group_name, tree_node=root_node_subscribers)
        #self.root_tree_subscribers = root_node_subscribers
        self.no_of_children_subscriber_tree = no_of_children_subscriber_tree
        self.depth_subscriber_tree = depth_subscriber_tree

    def set_root_tree_pub_sub(self, root_node_pub_sub, no_of_children_publisher_tree=None, depth_publisher_tree=None):
        self.root_tree_pub_sub = Node(self.group_name, tree_node=root_node_pub_sub)
        #self.root_tree_publishers = root_node_publishers
        self.no_of_children_publisher_tree = no_of_children_publisher_tree
        self.depth_publisher_tree = depth_publisher_tree"""

    def add_topic(self, topic):
        self.topics.append(topic)

    def delete_topic(self, topic):
        self.topics.remove(topic)

    def add_participant(self, participant, permission):
        self.participants_permissions[participant] = permission

    def delete_participant(self, participant):
        del self.participants_permissions[participant]
    # @property
    # def email(self):
    #     return '{}.{}@email.com'.format(self.first, self.last)
    #
    # @property
    # def fullname(self):
    #     return '{} {}'.format(self.first, self.last)



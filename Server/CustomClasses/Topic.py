from anytree import Node
import uuid
from .TreeNode import TreeNode
from .CustomEnums import TypeOfPubSubGroupEnum


class Topic:

    # todo -- switch depth and number of children to tree class, makes more sense there
    def __init__(self, topic_name, topic_id=None):
        self.topicName = topic_name
        if topic_id is None:
            self.topic_id = str(uuid.uuid4())



from TreeNode import TreeNode, LeafNode
from Participant import Participant
from anytree import Node, findall_by_attr, PreOrderIter
from Topic import Topic
from CustomEnums import PermissionTypesEnum, TypeOfPubSubGroupEnum
from PublishSubscribeTreeKeys import PublishSubscribeTreeKeys

# todo -- figure out what data needs to be persisted and how


def generate_key():
    return 10


class LKH:
    @staticmethod
    def __generate_tree(topic, participants=None, common_tree=False, pub_tree=False, sub_tree=False):
        # todo -- check how to pass depth and no of children automatically and by arguments
        # height and depth not fitting number of a participants
        if not (participants is None):
            if len(participants) > topic.no_of_children ** (topic.depth - 1):
                return "error message"  # todo -- customize the error message
        current_parents = None
        if common_tree is True:
            current_parents = [topic.root_tree_common]
            print(current_parents[0].is_root)

        if pub_tree is True:
            current_parents = [topic.root_tree_publishers]

        if sub_tree is True:
            current_parents = [topic.root_tree_subscribers]

        node_count = 1
        temp_parent = []
        for d in range(topic.depth):
            for parent in current_parents:
                for k in range(topic.no_of_children):
                    children_node = TreeNode(node_count)
                    children_tree_node = Node(str(node_count), parent=parent, tree_node=children_node)
                    children_tree_node.is_root
                    temp_parent.append(children_tree_node)
                    node_count += 1
            current_parents.clear()
            current_parents = list(temp_parent)
            temp_parent.clear()

        if participants is None:
            return topic.root_tree, current_parents, node_count

        ################################################################

        leaf_nodes = current_parents
        participant_count = 0
        node_id = node_count
        for leaf in leaf_nodes:
            if not (participants is None):
                if participant_count < len(participants):
                    node_id += 1
                    # adding topic to the participant
                    # does it make sense to do this at key manager level?
                    # participants[participant_count].add_topic(topic) # topic commented
                    leaf_node = LeafNode(node_id, participants[participant_count])
                    Node(participants[participant_count].participant_id, parent=leaf.parent, leaf_node=leaf_node)
                    leaf.parent = None
                    leaf.tree_node = None
                    participant_count += 1
                else:
                    break
        for p in range(participant_count, len(leaf_nodes)):
            Node("empty", parent=leaf_nodes[p].parent, leaf_node=LeafNode(leaf_nodes[p].tree_node.node_id))
            leaf_nodes[p].parent = None
            leaf_nodes[p].tree_node = None
            # leaf_node = leaf[0].tree_node
        return topic

    @staticmethod
    def setup_topic_trees(topic, participants_permissions=None):
        # check for type of publish subscribe group  and proceed further
        if topic.type_of_pub_sub_group == TypeOfPubSubGroupEnum.ALL_PUBSUB:
            # call functions here
            # set publisher, subscriber and common trees based on the group
            LKH.__setup_pub_sub_group_trees(topic, participants_permissions, common_tree=True)

        elif topic.type_of_pub_sub_group == TypeOfPubSubGroupEnum.SOME_PUBSUB_SOME_PUB:
            pub_tree_keys = PublishSubscribeTreeKeys(common_key=True, publisher_public_key=False,
                                                     publisher_private_key=False, subscriber_public_key=True,
                                                     subscriber_private_key=False)
            sub_tree_keys = PublishSubscribeTreeKeys(common_key=True, publisher_public_key=False,
                                                     publisher_private_key=False, subscriber_public_key=True,
                                                     subscriber_private_key=True)
            LKH.__setup_pub_sub_group_trees(topic, participants_permissions, pub_tree=True, sub_tree=True,
                                            pub_tree_keys=pub_tree_keys, sub_tree_keys=sub_tree_keys)

        elif topic.type_of_pub_sub_group == TypeOfPubSubGroupEnum.SOME_PUBSUB_SOME_SUB:
            pub_tree_keys = PublishSubscribeTreeKeys(common_key=True, publisher_public_key=True,
                                                     publisher_private_key=True, subscriber_public_key=False,
                                                     subscriber_private_key=False)
            sub_tree_keys = PublishSubscribeTreeKeys(common_key=True, publisher_public_key=True,
                                                     publisher_private_key=False, subscriber_public_key=False,
                                                     subscriber_private_key=False)
            LKH.__setup_pub_sub_group_trees(topic, participants_permissions, pub_tree=True, sub_tree=True,
                                            pub_tree_keys=pub_tree_keys, sub_tree_keys=sub_tree_keys)

        elif topic.type_of_pub_sub_group == TypeOfPubSubGroupEnum.SOME_PUBSUB_SOME_PUB_SOME_SUB \
                or topic.type_of_pub_sub_group == TypeOfPubSubGroupEnum.SOME_PUB_SOME_SUB:
            pub_tree_keys = PublishSubscribeTreeKeys(common_key=False, publisher_public_key=True,
                                                     publisher_private_key=True, subscriber_public_key=True,
                                                     subscriber_private_key=False)
            sub_tree_keys = PublishSubscribeTreeKeys(common_key=False, publisher_public_key=True,
                                                     publisher_private_key=False, subscriber_public_key=True,
                                                     subscriber_private_key=True)
            LKH.__setup_pub_sub_group_trees(topic, participants_permissions, pub_tree=True, sub_tree=True,
                                            pub_tree_keys=pub_tree_keys, sub_tree_keys=sub_tree_keys)

        elif topic.type_of_pub_sub_group == TypeOfPubSubGroupEnum.MANY_PUB_1_SUB:
            # todo -- check this again
            pub_tree_keys = PublishSubscribeTreeKeys(common_key=True, publisher_public_key=False,
                                                     publisher_private_key=False, subscriber_public_key=True,
                                                     subscriber_private_key=False)
            sub_tree_keys = PublishSubscribeTreeKeys(common_key=True, publisher_public_key=False,
                                                     publisher_private_key=False, subscriber_public_key=True,
                                                     subscriber_private_key=True)
            LKH.__setup_pub_sub_group_trees(topic, participants_permissions, pub_tree=True, sub_tree=True,
                                            pub_tree_keys=pub_tree_keys, sub_tree_keys=sub_tree_keys)

        elif topic.type_of_pub_sub_group == TypeOfPubSubGroupEnum.MANY_SUB_1_PUB:
            pub_tree_keys = PublishSubscribeTreeKeys(common_key=True, publisher_public_key=True,
                                                     publisher_private_key=True, subscriber_public_key=False,
                                                     subscriber_private_key=False)
            sub_tree_keys = PublishSubscribeTreeKeys(common_key=True, publisher_public_key=True,
                                                     publisher_private_key=False, subscriber_public_key=True,
                                                     subscriber_private_key=True)
            LKH.__setup_pub_sub_group_trees(topic, participants_permissions, pub_tree=True, sub_tree=True,
                                            pub_tree_keys=pub_tree_keys, sub_tree_keys=sub_tree_keys)

        else:
            pass  # return error

    # def get_ancestor_keys(self, participants, topic):
    #     participants_ancestors_dict = {}
    #     if type(participants) == list:
    #         for participant in participants:
    #             ancestors = participant.ancestors
    #             participants_ancestors_dict[participant] = ancestors
    #         return participants_ancestors_dict
    #
    #     else:
    #         return participants.ancestors

    # In this method trees are created based on the type publisher-
    # -subscriber group
    @staticmethod
    def __setup_pub_sub_group_trees(topic, participants_permissions=None, pub_tree=None, sub_tree=None, common_tree=None,
                                    pub_tree_keys=None, sub_tree_keys=None):
        # how to get permissions of individual participant?-receive a map of participant and permissions.
        # set keys in the tree node object
        # not sure below 2 needed yet

        group_key_common = None
        group_key_publishers = dict()  # can test for None instead here (quick check)
        group_key_subscribers = dict()
        publisher_public_key = None
        publisher_private_key = None
        subscriber_public_key = None
        subscriber_private_key = None
        if pub_tree is None and sub_tree is None and common_tree is None:
            return "error message"

        if common_tree is True:
            topic_root_node_common = TreeNode('0', root_node=True)
            group_key_common = generate_key()
            topic_root_node_common.set_node_common_key(group_key_common)
            topic.set_root_tree_common(topic_root_node_common)
            # call function next - not here, recheck

        # generate all the keys
        if pub_tree is True and sub_tree is True:
            # checking only public key will suffice, because if there is a public key, there will definitely be a
            # private key
            if pub_tree_keys.publisher_public_key is True:
                # generate public and private keys
                # todo -- find an appropriate method to generate ECC public and private keys
                publisher_public_key = generate_key()
                publisher_private_key = generate_key()

            if pub_tree_keys.subscriber_public_key is True:
                # generate public private keys
                subscriber_public_key = generate_key()
                subscriber_private_key = generate_key()

        if not (pub_tree is None):
            topic_root_node_publishers = TreeNode('0', root_node=True)
            if pub_tree_keys.publisher_public_key is True:
                group_key_publishers['publisher_public_key'] = publisher_public_key

            if pub_tree_keys.publisher_private_key is True:
                group_key_publishers['publisher_private_key'] = publisher_private_key

            if pub_tree_keys.subscriber_public_key is True:
                group_key_subscribers['subscriber_public_key'] = subscriber_public_key

            if pub_tree_keys.subscriber_private_key is True:
                group_key_subscribers['subscriber_private_key'] = subscriber_private_key

            if pub_tree_keys.common_key is True:
                group_key_subscribers['common_group_key'] = group_key_common

            topic_root_node_publishers.set_node_publisher_keys(group_key_publishers)
            topic.set_root_tree_publishers(topic_root_node_publishers)  # also try to set the depth and no. children

        if not (sub_tree is None):
            topic_root_node_subscribers = TreeNode('0', root_node=True)
            if sub_tree_keys.publisher_public_key is True:
                group_key_subscribers['publisher_public_key'] = publisher_public_key

            if sub_tree_keys.publisher_private_key is True:
                group_key_subscribers['publisher_private_key'] = publisher_private_key

            if sub_tree_keys.subscriber_public_key is True:
                group_key_subscribers['subscriber_public_key'] = subscriber_public_key

            if sub_tree_keys.subscriber_private_key is True:
                group_key_subscribers['subscriber_private_key'] = subscriber_private_key

            if sub_tree_keys.common_key is True:
                group_key_subscribers['common_group_key'] = group_key_common

            topic_root_node_subscribers.set_node_subscriber_keys(group_key_subscribers)
            topic.set_root_tree_subscribers(topic_root_node_subscribers)

        # todo -- handle tree sizes

        if topic.root_tree_common is not None:
            participants = []
            for participant in participants_permissions:
                # print (participant[0])
                participant[0].add_topic(topic, participant[1])
                participants.append(participant[0])
            LKH.__generate_tree(topic, participants, common_tree=True)

        else:
            # todo todo
            # participants segregation
            publish_tree_participants = []
            subscribe_tree_participants = []
            for participant in participants_permissions:
                if participant[1] is PermissionTypesEnum.PUBLISH:
                    participant[0].add_topic(topic, participant[1])
                    publish_tree_participants.append(participant[0])
                if participant[1] is PermissionTypesEnum.SUBSCRIBE:
                    participant[0].add_topic(topic, participant[1])
                    subscribe_tree_participants.append(participant[0])
                if participant[1] is PermissionTypesEnum.PUBLISH_AND_SUBSCRIBE:
                    participant[0].add_topic(topic, participant[1])
                    publish_tree_participants.append(participant[0])
                    subscribe_tree_participants.append(participant[0])

            if topic.root_tree_publishers is not None and topic.root_tree_subscribers is not None:
                LKH.__generate_tree(topic, publish_tree_participants, pub_tree=True)
                LKH.__generate_tree(topic, subscribe_tree_participants, sub_tree=True)

        # call function here to generate the tree
        # set topic and permissions for the participants (do not forget)
        # check participant permissions and create separate lists for all permission types
        # check if pub and sub trees are not none and add participants to the trees accordingly

    @staticmethod
    def get_ancestors_all_participants(topic):
        children_list = []
        ancestors_list = []
        # loop through children
        for node in PreOrderIter(topic.root_tree):
            # node = Node(node)
            # check if value not equal to empty
            if node.is_leaf and node.name != "empty":
                children_list.append(node)
                ancestors_list.append(list(node.ancestors))
        return children_list, ancestors_list

# add and delete participant also needs to be changed based on permissions and groups
    @staticmethod
    def add_participant(topic, participant):
        # get one empty node and add participant
        empty_node = findall_by_attr(topic.root_tree, "empty")[0]
        participant.add_topic(topic)  # include code for user-permissions  # or better move this to top
        new_leaf_node = LeafNode(empty_node.leaf_node.node_id, participant)
        added_participant = Node(participant.participant_id, parent=empty_node.parent, leaf_node=new_leaf_node)
        # dis-allocate the old empty node after attaching the new one to the tree
        empty_node.parent = None
        empty_node.leaf_node = None

        # find ancestors of the added participant and change their keys
        ancestor_list = added_participant.ancestors
        for ancestor in ancestor_list:
            ancestor.tree_node.reset_key()
        # code to add details about the messages to be sent
        # first construct messages for participant and its siblings
        message_details_dict_list = []
        message_detail = {"message_name": str(added_participant.parent.tree_node.node_id) + "/" + str(added_participant.leaf_node.node_id),
                          "encryption_key": added_participant.leaf_node.participant.pairwise_key,
                          "changed_parent_key": added_participant.parent.tree_node.node_key}
        message_details_dict_list.append(message_detail)
        siblings = added_participant.siblings
        for sibling in siblings:
            message_detail = {"message_name": str(sibling.parent.tree_node.node_id) + "/" + str(sibling.leaf_node.node_id),
                              "encryption_key": sibling.leaf_node.participant.pairwise_key,
                              "changed_parent_key": sibling.parent.tree_node.node_key}
            message_details_dict_list.append(message_detail)

        # construct messages for ancestors and their siblings
        for ancestor in range(len(ancestor_list)-2, -1, -1):
            children = ancestor_list[ancestor].children
            for child in children:
                message_detail = {
                    "message_name": str(child.parent.tree_node.node_id) + "/" + str(child.tree_node.node_id),
                    "encryption_key": child.tree_node.node_key,
                    "changed_parent_key": child.parent.tree_node.node_key}
                message_details_dict_list.append(message_detail)

        return topic.root_tree, added_participant, message_details_dict_list

    @staticmethod
    def delete_participant(topic, participant):
        # find the node
        participant_to_be_removed = findall_by_attr(topic.root_tree, participant.participant_id)[0]

        # find all ancestors of this participant and change keys
        ancestor_list = participant_to_be_removed.ancestors
        for ancestor in ancestor_list:
            ancestor.tree_node.reset_key()

        # code to add details about the messages to be sent
        # first construct messages for to-be-deleted participant's siblings
        message_details_dict_list = []
        siblings = participant_to_be_removed.siblings
        for sibling in siblings:
            message_detail = {
                "message_name": str(sibling.parent.tree_node.node_id) + "/" + str(sibling.leaf_node.node_id),
                "encryption_key": sibling.leaf_node.participant.pairwise_key,
                "changed_parent_key": sibling.parent.tree_node.node_key}
            message_details_dict_list.append(message_detail)
        # construct messages for ancestors and their siblings
        for ancestor in range(len(ancestor_list) - 2, -1, -1):
            children = ancestor_list[ancestor].children
            for child in children:
                message_detail = {
                    "message_name": str(child.parent.tree_node.node_id) + "/" + str(child.tree_node.node_id),
                    "encryption_key": child.tree_node.node_key,
                    "changed_parent_key": child.parent.tree_node.node_key}
                message_details_dict_list.append(message_detail)

        # delete the participant and add empty node there
        participant.delete_topic(topic)

        new_leaf_node = LeafNode(participant_to_be_removed.leaf_node.node_id)
        new_leaf_node.participant = None
        new_empty_node = Node("empty", parent=participant_to_be_removed.parent, leaf_node=new_leaf_node)

        # dis-allocate the participant node after attaching the new empty node to the tree
        participant_to_be_removed.parent = None
        participant_to_be_removed.leaf_node = None

        return topic.root_tree, new_empty_node, message_details_dict_list

    @staticmethod
    def convert_tree_to_json(topic):
        root_node = topic.root_tree
        json_string = {}
        json_string["topic"] = topic.topicName
        json_string["tree_depth"] = topic.depth
        json_string["tree_no_of_children"] = topic.no_of_children
        # copy all important tree details in a dictionary format
        # convert it to Json object, this can be used to persist

        # loop through the tree and collect data
        node_details_list = []
        for node in PreOrderIter(root_node):
            node_details ={}
            if node.parent is None:
                node_details ["parent"] = None
            else:
                node_details["parent"] = node.parent.tree_node.node_id
            if hasattr(node, "leaf_node"):
                node_details["node_id"] = node.leaf_node.node_id
                node_details["node_key"] = node.leaf_node.node_key
                node_details["leaf_node"] = "true"
                if node.leaf_node.participant is None:
                    node_details["participant"] = None
                else:
                    participant = {"participant_id": node.leaf_node.participant.participant_id,
                                   "pairwise_key": node.leaf_node.participant.pairwise_key}
                    participant_copy = participant.copy()
                    node_details["participant"] = participant_copy
                    participant.clear()
            else:
                node_details["node_id"] = node.tree_node.node_id
                node_details["node_key"] = node.tree_node.node_key
                node_details["leaf_node"] = "false"
                node_details["participant"] = None
            node_details_copy = node_details.copy()
            node_details_list.append(node_details_copy)
            node_details.clear()
        json_string["node_details"] = node_details_list
        return json_string

    @staticmethod
    def tree_from_json(json_tree):
        # write code to construct a tree from json data
        # create topic
        topic = None
        # first loop create all nodes and map ids to nodes
        id_to_node = {}
        for node in json_tree["node_details"]:
            if node["leaf_node"] == "false":
                if node["parent"] is None:
                    tree_node = TreeNode(node["node_id"])
                    children_tree_node = Node(json_tree["topic"], tree_node=tree_node)
                    id_to_node[node["node_id"]] = children_tree_node
                else:
                    tree_node = TreeNode(node["node_id"])
                    children_tree_node = Node(node["node_id"], tree_node=tree_node)
                    id_to_node[node["node_id"]] = children_tree_node
            else:
                if node["participant"] is None:
                    leaf_node = LeafNode(node["node_id"])
                    children_tree_node = Node("empty", leaf_node=leaf_node)
                    id_to_node[node["node_id"]] = children_tree_node
                else:
                    participant = Participant(node["participant"]["pairwise_key"], node["participant"]["participant_id"])
                    leaf_node = LeafNode(node["node_id"], participant=participant)
                    children_tree_node = Node(participant.participant_id, leaf_node=leaf_node)
                    id_to_node[node["node_id"]] = children_tree_node
                    participant.add_topic(json_tree["topic"])
        parent_node = None
        for node in json_tree["node_details"]:
            if node["parent"] is None:
                id_to_node[node["node_id"]].parent = None
                parent_node = id_to_node[node["node_id"]]
                topic = Topic(json_tree["topic"], json_tree["tree_depth"], json_tree["tree_no_of_children"],
                              root_node=parent_node)
            else:
                id_to_node[node["node_id"]].parent = id_to_node[node["parent"]]

        return parent_node, id_to_node

















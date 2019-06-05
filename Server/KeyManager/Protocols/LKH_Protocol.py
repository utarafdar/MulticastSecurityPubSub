from .CustomClasses.TreeNode import TreeNode, LeafNode
from Server.CustomClasses.Participant import Participant
from anytree import Node, findall_by_attr, PreOrderIter
from Server.CustomClasses.Topic import Topic
from Server.CustomClasses.CustomEnums import PermissionTypesEnum, TypeOfPubSubGroupEnum
import random
import math


def generate_key():
    random.randrange(1000, 99999)


class LKH:
    @staticmethod
    def generate_tree(tree_root, depth, no_of_children, participants=None):
        # height and depth not fitting number of a participants
        if not (participants is None):
            if len(participants) > no_of_children ** (depth - 1):
                return "error message"  # todo -- customize the error message
        # optimization to scale tree
        if depth is None and no_of_children is None and participants is None:
            depth = 1
            no_of_children = 2
        elif depth is None and no_of_children is None and participants is not None:
            # or set up tree size
            no_of_children = 2
            depth = math.ceil(math.log2(len(participants)))
        else:
            pass

        current_parents = [tree_root]
        node_count = 1
        temp_parent = []
        for d in range(depth):
            for parent in current_parents:
                for k in range(no_of_children):
                    children_node = TreeNode(node_count)
                    children_tree_node = Node(str(node_count), parent=parent, tree_node=children_node)
                    # children_tree_node.is_root
                    temp_parent.append(children_tree_node)
                    node_count += 1
            current_parents.clear()
            current_parents = list(temp_parent)
            temp_parent.clear()

        if participants is None:
            for leaf in current_parents:
                Node("empty", parent=leaf.parent, leaf_node=LeafNode(leaf.tree_node.node_id))
                leaf.parent = None
                leaf.tree_node = None
            return tree_root, current_parents, node_count

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
        return tree_root

    # changes needed -- todo--
    @staticmethod
    def get_ancestors_all_participants(group):
        children_list = []
        ancestors_list = []
        # loop through children
        for node in PreOrderIter(group.root_tree):
            # node = Node(node)
            # check if value not equal to empty
            if node.is_leaf and node.name != "empty":
                children_list.append(node)
                ancestors_list.append(list(node.ancestors))
        return children_list, ancestors_list

# add and delete participant also needs to be changed based on permissions and groups
    @staticmethod
    def add_participant(tree_root, participant, changed_root_keys=None):

        empty_nodes = findall_by_attr(tree_root, "empty")
        if len(empty_nodes) is 0:

            # change root node keys
            if changed_root_keys is not None:
                tree_root.tree_node.root_node_keys = changed_root_keys.copy()
            # tree structure change --
            # get all the leaf nodes and maximum node id
            leaf_nodes = tree_root.leaves
            last_node_id = int(leaf_nodes[len(leaf_nodes)-1].leaf_node.node_id)
            participant_counter = 0
            added_participant = None
            message_details_dict_list = []
            # change tree structure
            # children_node = TreeNode(node_count)
            # children_tree_node = Node(str(node_count), parent=parent, tree_node=children_node)
            for leaf in leaf_nodes:
                new_parent_tree_node = TreeNode(leaf.leaf_node.node_id)
                new_parent = Node(leaf.leaf_node.node_id, parent=leaf.parent, tree_node=new_parent_tree_node)
                # two children for this node
                # 1st child has the same participant and the second child is empty
                last_node_id += 1
                leaf.leaf_node.name = str(last_node_id)
                leaf.leaf_node.node_id = str(last_node_id)
                leaf.parent = new_parent
                # send the changed structure message only to the participants affected
                # newly added participant messages will be handled by registration protocol not here

                message_detail = {
                    "message_name": "change_tree_structure" + "/" + leaf.leaf_node.participant.participant_id,
                    "encryption_key": leaf.leaf_node.participant.pairwise_key,
                    "changed_parent_key": new_parent.tree_node.node_key}  # todo -- check issues
                message_details_dict_list.append(message_detail)

                # first check if the participant is already added
                if participant_counter is 0:
                    # add new participant here
                    last_node_id += 1
                    new_leaf_node = LeafNode(str(last_node_id), participant)
                    added_participant = Node(participant.participant_id, parent=new_parent, leaf_node=new_leaf_node)
                    participant_counter = 1

                else:  # add empty node else
                    # if participant is already added 2nd child empty
                    # Node("empty", parent=leaf_nodes[p].parent, leaf_node=LeafNode(leaf_nodes[p].tree_node.node_id))
                    last_node_id += 1
                    Node("empty", parent=new_parent, leaf_node=LeafNode(str(last_node_id)))

            return tree_root, added_participant, message_details_dict_list, True

        else:

            empty_node = empty_nodes[0]
            # participant.add_topic(topic)  # include code for user-permissions  # or better move this to top
            new_leaf_node = LeafNode(empty_node.leaf_node.node_id, participant)
            added_participant = Node(participant.participant_id, parent=empty_node.parent, leaf_node=new_leaf_node)
            # dis-allocate the old empty node after attaching the new one to the tree
            empty_node.parent = None
            empty_node.leaf_node = None

            # find ancestors of the added participant and change their keys
            ancestor_list = added_participant.ancestors
            for ancestor in ancestor_list:
                if ancestor.is_root and changed_root_keys is not None:
                    ancestor.tree_node.root_node_keys = changed_root_keys.copy()
                else:
                    ancestor.tree_node.reset_key()
                # change the keys of root node here

            # code to add details about the messages to be sent
            # first construct messages for participant and its siblings
            message_details_dict_list = []
            # adding message for the newly added participant to be decided based on other implementations
            # todo -- including group ids to  be done in group controller

            """message_detail = {"message_name": str(added_participant.parent.tree_node.node_id) + "/" + str(added_participant.leaf_node.node_id),
                              "encryption_key": added_participant.leaf_node.participant.pairwise_key,
                              "changed_parent_key": added_participant.parent.tree_node.node_key}
            message_details_dict_list.append(message_detail)"""
            siblings = added_participant.siblings
            for sibling in siblings:
                if sibling.leaf_node.participant is not None:
                    # if first parent is root
                    if sibling.parent.is_root:
                        changed_parent_key = sibling.parent.tree_node.root_node_keys
                    else:
                        changed_parent_key = sibling.parent.tree_node.node_key
                    message_detail = {# "message_name": str(sibling.parent.tree_node.node_id) + "/" + str(sibling.leaf_node.node_id),
                                      "message_name": str(sibling.parent.tree_node.node_id) + "/" +
                                                      str(sibling.leaf_node.participant.participant_id) + "__changeParent__" + str(sibling.parent.tree_node.node_id),
                                      "encryption_key": sibling.leaf_node.participant.pairwise_key,
                                      "changed_parent_key": changed_parent_key}
                    message_details_dict_list.append(message_detail)

            # construct messages for ancestors and their siblings
            for ancestor in range(len(ancestor_list)-2, -1, -1):
                children = ancestor_list[ancestor].children
                for child in children:
                    message_detail = {
                        "message_name": str(child.parent.tree_node.node_id) + "/" + str(child.tree_node.node_id) +
                                        "__changeParent__" + str(child.parent.tree_node.node_id),
                        "encryption_key": child.tree_node.node_key}
                    if child.parent.is_root and changed_root_keys is not None:
                        message_detail["changed_parent_key"] = child.parent.tree_node.root_node_keys
                    else:
                        message_detail["changed_parent_key"] = child.parent.tree_node.node_key
                    # "changed_parent_key": child.parent.tree_node.node_key}
                    # if last i.e. root node then encryption keys is the list of changed pub-sub keys
                    # add that condition for the last one. when ancestor = 0 basically.
                    message_details_dict_list.append(message_detail)

            return tree_root, added_participant, message_details_dict_list, False

    @staticmethod
    def delete_participant(tree_root, participant, changed_root_keys=None):
        # find the node
        participant_to_be_removed = findall_by_attr(tree_root, participant.participant_id)[0]

        # find all ancestors of this participant and change keys
        ancestor_list = participant_to_be_removed.ancestors
        for ancestor in ancestor_list:
            if ancestor.is_root and changed_root_keys is not None:
                ancestor.tree_node.root_node_keys = changed_root_keys.copy()
            else:
                ancestor.tree_node.reset_key()

        # code to add details about the messages to be sent
        # first construct messages for to-be-deleted participant's siblings
        message_details_dict_list = []
        siblings = participant_to_be_removed.siblings
        for sibling in siblings:
            if sibling.leaf_node.participant is not None:
                message_detail = {
                    # "message_name": str(sibling.parent.tree_node.node_id) + "/" + str(sibling.leaf_node.node_id),
                    "message_name": str(sibling.parent.tree_node.node_id) + "/" + str(
                        sibling.leaf_node.participant.participant_id) + "__changeParent__" + str(sibling.parent.tree_node.node_id),
                    "encryption_key": sibling.leaf_node.participant.pairwise_key,
                    "changed_parent_key": sibling.parent.tree_node.node_key}
                message_details_dict_list.append(message_detail)
        # construct messages for ancestors and their siblings
        for ancestor in range(len(ancestor_list) - 2, -1, -1):
            children = ancestor_list[ancestor].children
            for child in children:
                message_detail = {
                    "message_name": str(child.parent.tree_node.node_id) + "/" + str(child.tree_node.node_id)
                                    + "__changeParent__" + str(child.parent.tree_node.node_id),
                    "encryption_key": child.tree_node.node_key}
                if child.parent.is_root and changed_root_keys is not None:
                    message_detail["changed_parent_key"] = child.parent.tree_node.root_node_keys
                else:
                    message_detail["changed_parent_key"] = child.parent.tree_node.node_key
                    # "changed_parent_key": child.parent.tree_node.node_key}
                message_details_dict_list.append(message_detail)

        # delete the participant and add empty node there
        # moved this to manager class
        # participant.delete_topic(topic)

        new_leaf_node = LeafNode(participant_to_be_removed.leaf_node.node_id)
        new_leaf_node.participant = None
        new_empty_node = Node("empty", parent=participant_to_be_removed.parent, leaf_node=new_leaf_node)

        # dis-allocate the participant node after attaching the new empty node to the tree
        participant_to_be_removed.parent = None
        participant_to_be_removed.leaf_node = None

        return tree_root, new_empty_node, message_details_dict_list

    @staticmethod
    def update_tree_root_keys(tree_root, changed_root_keys=None):

        message_details_dict_list = []
        tree_root.tree_node.root_node_keys = changed_root_keys.copy()
        children = tree_root.children

        if tree_root.height is 1:
            for child in children:
                if child.name is not "empty":
                    message_detail = {
                        "message_name": str(child.parent.tree_node.node_id) + "/" +
                                        str(child.leaf_node.participant.participant_id)+"__changeParent__" +
                                        str(child.parent.tree_node.node_id),
                        # "message_name": str(child.parent.tree_node.node_id) + "/" + str(child.leaf_node.node_id),
                        "encryption_key": child.leaf_node.participant.pairwise_key,
                        "changed_parent_key": child.parent.tree_node.root_node_keys}
                    message_details_dict_list.append(message_detail)
        else:
            for child in children:
                message_detail = {
                    "message_name": str(child.parent.tree_node.node_id) + "/" + str(child.tree_node.node_id)+
                                    "__changeParent__" + str(child.parent.tree_node.node_id),
                    "encryption_key": child.tree_node.node_key,
                    "changed_parent_key": child.parent.tree_node.root_node_keys}
                message_details_dict_list.append(message_detail)

        return tree_root, message_details_dict_list

    @staticmethod
    def convert_tree_to_json(topic):
        root_node = topic.root_tree
        json_string = dict()
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

    # handle error conditions
    # this should not be here
    @staticmethod
    def __is_allowed_permission(group_pub_sub_group_type, participant_permission):

        if group_pub_sub_group_type is TypeOfPubSubGroupEnum.ALL_PUBSUB.value:
            if participant_permission is PermissionTypesEnum.SUBSCRIBE.value:
                return False
            elif participant_permission is PermissionTypesEnum.PUBLISH.value:
                return False
            else:
                return True

        elif group_pub_sub_group_type is TypeOfPubSubGroupEnum.SOME_PUBSUB_SOME_PUB:
            if participant_permission is PermissionTypesEnum.SUBSCRIBE.value:
                return False
            else:
                return True

        elif group_pub_sub_group_type is TypeOfPubSubGroupEnum.SOME_PUBSUB_SOME_SUB:
            if participant_permission is PermissionTypesEnum.PUBLISH.value:
                return False
            else:
                return True

        elif group_pub_sub_group_type is TypeOfPubSubGroupEnum.SOME_PUB_SOME_SUB or group_pub_sub_group_type is TypeOfPubSubGroupEnum.MANY_PUB_1_SUB or group_pub_sub_group_type is TypeOfPubSubGroupEnum.MANY_SUB_1_PUB:
            if participant_permission is PermissionTypesEnum.PUBLISH_AND_SUBSCRIBE.value:
                return False
            else:
                return True

        else:
            return True


















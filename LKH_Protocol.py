from TreeNode import TreeNode, LeafNode
from Participant import Participant
from anytree import Node, findall_by_attr, PreOrderIter


def generate_key():
    return 10


class LKH:
    @staticmethod
    def __setup_tree_no_participants(topic):
        node_count = 1
        current_parents = [topic.root_tree]
        temp_parent = []
        for d in range(topic.depth):
            for parent in current_parents:
                for k in range(topic.no_of_children):
                    children_node = TreeNode(node_count)
                    children_tree_node = Node(str(node_count), parent=parent, tree_node=children_node)
                    temp_parent.append(children_tree_node)
                    node_count += 1
            current_parents.clear()
            current_parents = list(temp_parent)
            temp_parent.clear()

        return topic.root_tree, current_parents

    @staticmethod
    def setup_tree_with_participants(topic, participants=None):
        # height and depth not fitting number of a participants
        if not (participants is None):
            if len(participants) > topic.no_of_children**(topic.depth-1):
                return "error message"
        tree = LKH.__setup_tree_no_participants(topic)
        leaf_nodes = tree[1]
        parent_node = tree[0]
        participant_count = 0
        node_id = topic.no_of_children ** (topic.depth - 1)
        for leaf in leaf_nodes:
            if not (participants is None):
                if participant_count < len(participants):
                    node_id += 1
                    # adding topic to the participant
                    # does it make sense to do this at key manager level?
                    participants[participant_count].add_topic(topic)
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
        return parent_node

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

    @staticmethod
    def add_participant(topic, participant):
        # get one empty node and add participant
        empty_node = findall_by_attr(topic.root_tree, "empty")[0]
        participant.add_topic(topic)
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



















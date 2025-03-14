from anytree import findall_by_attr


class Participant:
    def __init__(self, pairwise_key, participant_id):
        self.pairwise_key = pairwise_key
        self.participant_id = participant_id
        self.groups = []
        self.group_id_user_permissions_dict = {}
        self.nonce_prefix_value = None

    def add_group(self, group, participant_permissions):
        # need to include logic for tree arrays
        # also add message names to subscribe in case of participant leave/join
        self.groups.append(group)
        self.group_id_user_permissions_dict.update({group.id: participant_permissions})

    def delete_group(self, group):
        # need to include logic for tree arrays
        del self.group_id_user_permissions_dict[group.id]
        self.groups.remove(group)

    def get_message_names_topic(self, group):
        message_names_to_sub = []
        # add messages for ancestors
        participant_node = findall_by_attr(group.root_tree, str(self.participant_id))[0]
        message_name = str(participant_node.parent.tree_node.node_id) + "/" + str(participant_node.leaf_node.node_id)
        message_names_to_sub.append(message_name)
        ancestors = participant_node.ancestors
        for ancestor in range(len(ancestors)-1, 0, -1):
            message_name = str(ancestors[ancestor].parent.tree_node.node_id) + "/" + str(
                ancestors[ancestor].tree_node.node_id)
            message_names_to_sub.append(message_name)
        return message_names_to_sub

    def get_ancestor_list(self, topic):
        participant_node = findall_by_attr(topic.root_tree, str(self.participant_id))[0]
        return participant_node.ancestors
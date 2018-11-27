from TreeNode import TreeNode, LeafNode
from Participant import Participant
from anytree import Node, findall_by_attr, PreOrderIter


def generate_key():
    return 10


class LKH:
    @staticmethod
    def setup_tree_no_participants(topic):
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
    def setup_tree_with_participants(topic, participants):
        if len(participants) > topic.no_of_children**(topic.depth-1):
            return "error message"
        tree = LKH.setup_tree_no_participants(topic)
        leaf_nodes = tree[1]
        parent_node = tree[0]
        participant_count = 0
        node_id = topic.no_of_children ** (topic.depth - 1)
        for leaf in leaf_nodes:
            if participant_count < len(participants):
                node_id += 1
                #adding topic to the participant
                participants[participant_count].add_topic(topic)
                leaf_node = LeafNode(node_id, participants[participant_count])
                Node(participants[participant_count].participant_id, parent=leaf.parent, leaf_node=leaf_node)
                leaf.parent = None
                participant_count += 1
            else:
                break
        for p in range(participant_count, len(leaf_nodes)):
            Node("empty", parent=leaf_nodes[p].parent, leaf_node=leaf_nodes[p].tree_node)
            leaf_nodes[p].parent = None
           #leaf_node = leaf[0].tree_node
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
        #loop through children
        for node in PreOrderIter(topic.root_tree):
            #node = Node(node)
            #check if value not equal to empty
            if node.is_leaf and node.name != "empty":
                children_list.append(node)
                ancestors_list.append(list(node.ancestors))
        return children_list, ancestors_list





















from LKH_Protocol import LKH
from Participant import Participant
from Topic import Topic
from TreeNode import TreeNode
from anytree import Node, RenderTree, findall_by_attr, findall, Resolver

test_lkh = LKH()
#test_tree = test_lkh.setup_tree_no_participants(3, 2, "test")[0]
#print(findall_by_attr(test_tree, "3")[0].tree_node.node_key)
#print(RenderTree(test_tree))

participant1 = Participant("12345", "001")
participant2 = Participant("12345", "002")
participant3 = Participant("12345", "003")

participants = [participant1, participant2, participant3]
# print(type(participants))
# print(type(participant3))
# dict_test = {participant1: participants,
#         participant2: participants}
# print(dict_test)

topic = Topic("test", 3, 2)
result_tree = test_lkh.setup_tree_with_participants(topic, participants)
print(RenderTree(result_tree))
#
# print(findall_by_attr(result_tree, "001")[0].leaf_node.participant.pairwise_key)
# print(findall_by_attr(result_tree, "001")[0].name)
#
# print(findall_by_attr(result_tree, "empty"))
#node = Node(findall_by_attr(result_tree, "001"))
#print(node.is_leaf)
# node = Node("1", value = "this is it")
# node2 = Node("2", parent=node)
# node3 = Node("3", parent=node2)
# node4 = Node("4", parent=node3)
# node.is_leaf
# print(node.ancestors)

res = test_lkh.get_ancestors_all_participants(topic)
print(res[0])
print(res[1])


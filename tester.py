from LKH_Protocol import LKH
from Participant import Participant
from Topic import Topic
from anytree.exporter import JsonExporter
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
#result_tree = test_lkh.setup_tree_with_participants(topic)
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
# # node.is_leaf
# print(node.children)
# res = test_lkh.get_ancestors_all_participants(topic)
# print(findall_by_attr(result_tree, "empty"))
# print(res[1])
# print(res[0])

# empty_node = findall_by_attr(result_tree, "empty")[0]
# ancestor_list = empty_node.ancestors
# print(len(ancestor_list))
# for ancestor in ancestor_list:
#     print(ancestor.tree_node.node_id, ":", ancestor.tree_node.node_key)
#
# participant4 = Participant("12345", "004")
# added_value = test_lkh.add_participant(topic,participant4)
#
# print(RenderTree(added_value[0]))
#
# for ancestor in added_value[1].ancestors:
#     print(ancestor.tree_node.node_id, ":", ancestor.tree_node.node_key)
#
# print(added_value[2])
#
# res = test_lkh.delete_participant(topic, participant4)
# print(RenderTree(res[0]))
#
# for ancestor in res[1].ancestors:
#     print(ancestor.tree_node.node_id, ":", ancestor.tree_node.node_key)
# print(res[2])
#
# print(participant2.get_message_names_topic(topic))
#
# exporter = JsonExporter(indent=2, sort_keys=True)
# print(exporter.export(res))

json_res = test_lkh.convert_tree_to_json(topic)
print(json_res)
print(RenderTree(test_lkh.tree_from_json(json_res)[0]))
print(test_lkh.tree_from_json(json_res)[1])
# print(resl[""])
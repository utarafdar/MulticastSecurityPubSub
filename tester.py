from LKH_Protocol import LKH
from Participant import Participant
from Topic import Topic
from Group import Group
from anytree.exporter import JsonExporter
from TreeNode import TreeNode
from anytree import Node, RenderTree, findall_by_attr, findall, Resolver
from CustomEnums import TypeOfPubSubGroupEnum, PermissionTypesEnum
from PubSubKeyManagerTreeType import KeyManager
test_lkh = LKH()
from KeyManagerGKMP import KeyManagerGKMP
import math

#test_tree = test_lkh.setup_tree_no_participants(3, 2, "test")[0]
#print(findall_by_attr(test_tree, "3")[0].tree_node.node_key)
#print(RenderTree(test_tree))

participant1 = Participant("12345", "001")
participant2 = Participant("12345", "002")
participant3 = Participant("12345", "003")
#participant5 = Participant("12345", "003")

participants = [participant1, participant2, participant3]
# print(type(participants))
# print(type(participant3))
# dict_test = {participant1: participants,
#         participant2: participants}
# print(dict_test)

participants_permissions = [(participant1, 3), (participant2, 3), (participant3, 3)]

# tree sizes


topic = Topic("test")
# print(topic.type_of_pub_sub_group.value)

#result_tree = test_lkh.setup_topic_trees(topic, participants,TypeOfPubSubGroupEnum=1)
#result_tree = test_lkh.setup_tree_with_participants(topic)
#print(RenderTree(result_tree))
#test_lkh.setup_topic_trees(topic, participants_permissions)
#print(RenderTree(topic.root_tree_common))

topic2 = Topic("test")

# some method to calculate tree sizes
common_tree_size = {'no_of_children': 2,
                    'depth': 4,
                    'tree_type': 'common'}

pub_tree_size = {'no_of_children': 2,
                 'depth': 4,
                 'tree_type': 'pub'}

sub_tree_size = {'no_of_children': 2,
                 'depth': 4,
                 'tree_type': 'sub'}

pub_sub_tree_size = {'no_of_children': 2,
                     'depth': 4,
                     'tree_type': 'pub_sub'}
tree_sizes = [common_tree_size, pub_tree_size, sub_tree_size, pub_sub_tree_size]

participants_permissions2 = [(participant1, 1), (participant2, 2), (participant3, 3)]

# tree optimization testing
#KeyManager.setup_topic_trees(topic2)


#KeyManager.setup_topic_trees(topic2, participants_permissions2, tree_sizes)

participant4 = Participant("12345", "004")

# testing with groups
group1 = Group("group1", type_of_pub_sub_group=4)
group1.add_topic(topic)
group1.add_topic(topic2)
KeyManager.setup_group_trees(group1)

print(KeyManager.group_tree_mapping_list[0].root_tree_pub_sub.tree_node.root_node_keys['publisher_private_key'])
KeyManager.add_or_delete_participant(group1, Participant("12345", "001"), 3, add_participant=True)
KeyManager.add_or_delete_participant(group1, Participant("12345", "002"), 3, add_participant=True)
KeyManager.add_or_delete_participant(group1, Participant("12345", "003"), 3, add_participant=True)
KeyManager.add_or_delete_participant(group1, participant4, 3, add_participant=True)

res = KeyManager.group_tree_mapping_list[0]

print(KeyManager.group_tree_mapping_list[0].root_tree_pub_sub.tree_node.root_node_keys['publisher_private_key'])
print(KeyManager.group_tree_mapping_list[0].root_tree_publishers.tree_node.root_node_keys['publisher_private_key'])
print(KeyManager.group_tree_mapping_list[0].root_tree_subscribers.tree_node.root_node_keys['subscriber_private_key'])
# opyimiztion test
print(RenderTree(KeyManager.group_tree_mapping_list[0].root_tree_publishers))
#print(topic2.root_tree_publishers.leaves[0].leaf_node.participant.pairwise_key)
print(RenderTree(KeyManager.group_tree_mapping_list[0].root_tree_subscribers))
print(RenderTree(KeyManager.group_tree_mapping_list[0].root_tree_pub_sub))

KeyManager.add_or_delete_participant(group1, participant4, 3, delete_participant=True)
print(KeyManager.group_tree_mapping_list[0].root_tree_pub_sub.tree_node.root_node_keys['publisher_private_key'])
print(KeyManager.group_tree_mapping_list[0].root_tree_publishers.tree_node.root_node_keys['publisher_private_key'])
print(KeyManager.group_tree_mapping_list[0].root_tree_subscribers.tree_node.root_node_keys['subscriber_private_key'])
print(RenderTree(KeyManager.group_tree_mapping_list[0].root_tree_pub_sub))

# test gkmp

KeyManagerGKMP.set_up_gkmp_group(group1)
KeyManagerGKMP.add_or_delete_participant(group1, Participant("12345", "001"), 3, add_participant=True)
KeyManagerGKMP.add_or_delete_participant(group1, Participant("12345", "001"), 1, add_participant=True)
KeyManagerGKMP.add_or_delete_participant(group1, participant4, 3, add_participant=True)
KeyManagerGKMP.add_or_delete_participant(group1, Participant("12345", "001"), 2, add_participant=True)
KeyManagerGKMP.add_or_delete_participant(group1, participant4, 3, delete_participant=True)
res = KeyManagerGKMP.group_gkmp_mapping_list[0]
print(res.publishers_and_subscribers[0].pairwise_key)
print(res.group.group_name)
print()
# result1 = KeyManager.add_or_delete_participant(topic2, participant4, 3, delete_participant=True)

#print(RenderTree(topic2.root_tree_pub_sub))
#print(RenderTree(topic2.root_tree_publishers))
#print(RenderTree(topic2.root_tree_subscribers))
#print(result['add_participant'])
#print(result['delete_participant'])
#print(result['update_tree'])
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

#json_res = test_lkh.convert_tree_to_json(topic)
#print(json_res)
#print(RenderTree(test_lkh.tree_from_json(json_res)[0]))
#print(test_lkh.tree_from_json(json_res)[1])
# print(resl[""])

dicct = {'a':1,
         'b':2}
dict1 = {'ab':dicct,
         'ab1':dicct}
dict1['ab2'] = dicct
print(dict1['ab']['a'])

print(list(dict1.keys())[-1])

dicti = dict()
dicti['1'] = 2
print(dicti)

x =0

if x == 1 or x==0:
    print("pass")
else:
    print("fail")

node = Node("1", value = "this is it")
node2 = Node("2", parent=node)
node3 = Node("3", parent=node2)
node4 = Node("4", parent=node3)
node5 = Node("4", parent=node3)

print(len(node.leaves))
depth = math.ceil(math.log2(2))
print(depth)

test = list()
test.append(10)
value = test[0]
del test[0]
print(value)
print(len(test))

dict1 = dict()
dict1['1'] = 2
dict1['2'] = 3
dict1['3'] = 4

print(len(dict1))
print(list(dict1.keys())[0])
key = list(dict1.keys())[0]
del dict1[key]
print(dict1)

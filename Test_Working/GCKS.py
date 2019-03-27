from LKH_Protocol import LKH
from Participant import Participant
from Topic import Topic
from anytree.exporter import JsonExporter
from TreeNode import TreeNode
from anytree import Node, RenderTree, findall_by_attr, findall, Resolver
from CustomEnums import TypeOfPubSubGroupEnum, PermissionTypesEnum
from PubSubKeyManagerTreeType import KeyManager
import paho.mqtt.client as mqtt
import json

# assume registration is done
# while registration info transferred = pairwise key
# & what is the topic to subscribe to get direct messages from GCKS
# for simplicity lets assume its participant ID here
# example participant1 needs to subscribe to topic 001 - in order to receive direct messages from GCKS
# GCKS publishes to 001 encrypts payload with pairwise key (12345)
# on receiving message participant1 decrypts with pairwise key (12345)
# this is used to send data such as what topics to subscribe to get key updates
# also send key of the first parent

# setting up a tree with participants for testing, for a topic
lkh = LKH()

topic = Topic("test", type_of_pub_sub_group=TypeOfPubSubGroupEnum.SOME_PUBSUB_SOME_PUB_SOME_SUB.value)

participant1 = Participant("12345", "001")
participant1_sibling = Participant("12345s", "001s")
participant2 = Participant("123456", "002")
participant3 = Participant("123457", "003")

pub_tree_size = {'no_of_children': 2,
                 'depth': 3,
                 'tree_type': 'pub'}

sub_tree_size = {'no_of_children': 2,
                 'depth': 3,
                 'tree_type': 'sub'}

pub_sub_tree_size = {'no_of_children': 2,
                     'depth': 3,
                     'tree_type': 'pub_sub'}
tree_sizes = [pub_tree_size, sub_tree_size, pub_sub_tree_size]

participants_permissions2 = [(participant1, 1), (participant2, 2), (participant3, 3), (participant1_sibling, 1)]
KeyManager.setup_topic_trees(topic, participants_permissions2, tree_sizes)
# trees generated successfully here
# print(RenderTree(topic.root_tree_publishers))

# get all ancestors of participant1 and publish them encrypting with pairwise keys
ancestor_list = (findall_by_attr(topic.root_tree_publishers, "001"))[0].ancestors
# print(ancestor_list)

# make a dictionary/json of tree node names and key possessed by it
# since participant would need keys of all its ancestors
ancestor_keys = []
topic_to_sub_enc_keys = []
i = 0
while i < len(ancestor_list):

    ancestor_keys.append({'name': ancestor_list[i].name,
                          'key': ancestor_list[i].tree_node.node_key})
    if i != len(ancestor_list) - 1:
        topic_to_sub_enc_keys.append({'topic_to_sub': ancestor_list[i].name + '/' + ancestor_list[i+1].name,
                                      'enc_key': ancestor_list[i+1].tree_node.node_key})
    else:
        topic_to_sub_enc_keys.append({'topic_to_sub': ancestor_list[i].name + '/' + participant1.participant_id,
                                      'enc_key': participant1.pairwise_key})
    i = i+1

# for ancestor in ancestor_list:
#    initial_tree_related_data.append({'name': ancestor.name,
#                                      'key': ancestor.tree_node.node_key})
# print(topic_to_sub_enc_keys)
# print(ancestor_keys)

# now publish message to participant1 with these details
# encrypt the payload with the pairwise key
broker_address = "iot.eclipse.org"  # use external broker
publisher_GCKS = mqtt.Client("P3")  # create new instance
publisher_GCKS.connect(broker_address)
# need to implement encryption
mqtt_msg = json.dumps(ancestor_keys)  # todo -- encrypt with participant1.pairwise_key
publisher_GCKS.publish("GCKS/participant1001", mqtt_msg)

mqtt_msg = json.dumps(topic_to_sub_enc_keys) # todo -- encrypt with participant1.pairwise_key
publisher_GCKS.publish("GCKS/participant1001", mqtt_msg)



# print(ancestor_list[0].name, ancestor_list[0].tree_node.node_key)
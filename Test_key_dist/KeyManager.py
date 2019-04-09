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
import copy
import time
import cryptography
import os

class TestKeyManagerTopic:
    def __init__(self, topic):

        # setting up a tree with participants for testing, for a topic
        lkh = LKH()

        topic = Topic(topic, type_of_pub_sub_group=TypeOfPubSubGroupEnum.SOME_PUBSUB_SOME_PUB_SOME_SUB.value)

        participant1 = Participant(os.urandom(16), "001")
        participant1_sibling = Participant(os.urandom(16), "001s")
        participant2 = Participant(os.urandom(16), "002")
        participant3 = Participant(os.urandom(16), "003")

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

        self.topic = topic

    def add_client(self, client, permission, initial_topic, initial_topic_anc):
        # add the participant
        # then send updated keys to all others -- subscribe specific ancestors
        # later, send the initial message the participant
        # initial message = all ancestors and keys and what topics to subscribe to receive updated keys
        # this way all have updated keys

        result = KeyManager.add_or_delete_participant(self.topic, client, permission, add_participant=True)
        print(RenderTree(self.topic.root_tree_pub_sub))
        broker_address = "iot.eclipse.org"  # use external broker
        publisher_GCKS = mqtt.Client("P3")  # create new instance
        publisher_GCKS.connect(broker_address)

        print(result)
        # sending messages to participants affected by added participant
        for message in result['add_participant'][0]:
            update_msg_topic_name = self.topic.topicName + result['add_participant'][1]['tree_type'] + message['message_name']
            print(update_msg_topic_name)
            # todo -- encrypt here
            # msg_updated_key = str(message['changed_parent_key'])+" "+str(message['encryption_key'])
            # encrypting message
            # if key type is dictionary, then convert to byte-type for enryption
            if type(message['changed_parent_key']) is dict:
                message_to_bytes = json.dumps(message['changed_parent_key'])
            else:
                message_to_bytes = message['changed_parent_key']
            encrypted_message = cryptography.encrypt_aes(message['encryption_key'], message_to_bytes)
            publisher_GCKS.publish(update_msg_topic_name, encrypted_message)

        for tree in result['update_tree']:
            for message in tree[0]:
                update_msg_topic_name = self.topic.topicName + tree[1]['tree_type'] + message['message_name']
                # todo -- encrypt here
                print(update_msg_topic_name)
                msg_updated_key = str(message['changed_parent_key'])+" "+str(message['encryption_key'])
                # encrypting message
                # if key type is dictionary, then convert to byte-type for enryption
                if type(message['changed_parent_key']) is dict:
                    message_to_bytes = json.dumps(message['changed_parent_key'])
                else:
                    message_to_bytes = message['changed_parent_key']
                encrypted_message = cryptography.encrypt_aes(message['encryption_key'], message_to_bytes)
                publisher_GCKS.publish(update_msg_topic_name, encrypted_message)

        # initial subscribing topics for the client newly added

        # get all ancestors of participant1 and publish them encrypting with pairwise keys
        tree = Node(self.topic.topicName)
        tree_type_name = ''
        if permission is 1:
            tree = copy.deepcopy(self.topic.root_tree_publishers)
            tree_type_name = 'pub'
        if permission is 2:
            tree = copy.deepcopy(self.topic.root_tree_subscribers)
            tree_type_name = 'sub'
        if permission is 3:
            tree = copy.deepcopy(self.topic.root_tree_pub_sub)
            tree_type_name = 'pub_sub'

        # recheck
        ancestor_list = (findall_by_attr(tree, client.participant_id))[0].ancestors
        # print(ancestor_list)

        # make a dictionary/json of tree node names and key possessed by it
        # since participant would need keys of all its ancestors
        ancestor_keys = []
        topic_to_sub_enc_keys = []
        i = 0
        while i < len(ancestor_list):
            if ancestor_list[i].is_root is True:
                ancestor_keys.append({'name': str(ancestor_list[i].tree_node.node_id),
                                      # problem with json byte encoding
                                      #'key': ancestor_list[i].tree_node.root_node_keys})
                                      'key': ancestor_list[i].tree_node.root_node_keys})
            else:
                ancestor_keys.append({'name': str(ancestor_list[i].tree_node.node_id),
                                      'key': ancestor_list[i].tree_node.node_key.hex()})
            if i != len(ancestor_list) - 1:
                topic_to_sub_enc_keys.append({'topic_to_sub': self.topic.topicName + tree_type_name +
                                                              str(ancestor_list[i].tree_node.node_id) + '/' +
                                                              str(ancestor_list[i + 1].tree_node.node_id) +
                                                              "__changeParent__" + str(ancestor_list[i].tree_node.node_id ),
                                              # 'enc_key': ancestor_list[i + 1].tree_node.node_key})
                                              # problem with json byte encoding
                                              'enc_key': ancestor_list[i + 1].tree_node.node_key.hex()})
            else:
                topic_to_sub_enc_keys.append({'topic_to_sub': self.topic.topicName + tree_type_name +
                                                              str(ancestor_list[i].tree_node.node_id) + '/' +
                                                              client.participant_id + "__changeParent__" +
                                                              str(ancestor_list[i].tree_node.node_id),
                                               # 'enc_key': client.pairwise_key})
                                              # problem with json byte encoding
                                              'enc_key': client.pairwise_key.hex()})
            i = i + 1
        print ("topic to sub ")
        print (topic_to_sub_enc_keys)
        mqtt_msg = json.dumps(topic_to_sub_enc_keys)  # todo -- encrypt with participant1.pairwise_key
        # encrypt message
        encrypted_message = cryptography.encrypt_aes(client.pairwise_key, mqtt_msg)
        print(encrypted_message)
        publisher_GCKS.publish(initial_topic, encrypted_message)

        time.sleep(5)

        mqtt_msg = json.dumps(ancestor_keys)  # todo -- encrypt with participant1.pairwise_key
        encrypted_message = cryptography.encrypt_aes(client.pairwise_key, mqtt_msg)
        publisher_GCKS.publish(initial_topic_anc, encrypted_message)

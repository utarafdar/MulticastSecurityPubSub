from Server.KeyManager.PubSubKeyManagerTreeType import KeyManager
from Server.KeyManager.KeyManagerGKMP import KeyManagerGKMP
from Server.CustomClasses.CustomEnums import KeyManagementProtocols
import paho.mqtt.client as mqtt
import json
import copy
from anytree import Node, findall_by_attr
from nacl.encoding import HexEncoder
import time
import Server.CustomClasses.cryptography as crypto

class DataSA:
    # todo GCKS public and private keys
    GCKS_Verify_Key = None
    GCKS_Signing_Key = None

    def __init__(self, permissions, pairwise_key, key_management_type):
        self.key_management_type = key_management_type
        self.ancestor_keys = list()
        self.group_keys = dict()
        # type of enc publishing messages
        # type of dec sub messages
        # type of auth GCKS
        # topics, groupid, paiwise key and participant id
        self.group_id = None
        self.topics = list()
        self.pairwise_key = None
        self.participant_id = None
        self.nonce_prefix = None
        self.permissions = permissions
        self.subscriptions = list()
        self.pairwise_key = pairwise_key
        self.rekey_topics_keys = list()
        self.request_rekey_topic = None
        self.change_tree_structure_topic = None

    @staticmethod
    def set_gcks_verify_key(gcks_verify_key):
        DataSA.GCKS_Verify_Key = gcks_verify_key

    @staticmethod
    def set_gcks_signing_key(gcks_signing_key):
        DataSA.GCKS_Signing_Key = gcks_signing_key

    def set_ancestor_keys(self, ancestor_keys):
        self.ancestor_keys = ancestor_keys.copy()

    def set_subscriptions(self, subscriptions):
        self.subscriptions = subscriptions.copy()

    def set_group_keys(self, group_keys):
        self.group_keys = group_keys.copy()

    def set_nonce_prefix(self, nonce):
        self.nonce_prefix = nonce

    def set_rekey_topics(self, rekey_topics):
        self.rekey_topics_keys = rekey_topics.copy()

    def set_request_rekey_topic (self, rekey_topic):
        self.request_rekey_topic = rekey_topic

    def set_pairwise_key(self, pairwise_key):
        self.pairwise_key = pairwise_key

    def set_participant_id(self, participant_id):
        self.participant_id = participant_id

    def set_group_topics(self, group_topics):
        for topic in group_topics:
            self.topics.append({'topic_name': topic.topicName,
                                'topic_id': topic.topic_id})

    def set_group_id(self, group_id):
        self.group_id = str(group_id)

    def set_change_tree_structure_topic(self, group_id, participant_id):
        self.change_tree_structure_topic = "changeGroupStructure__"+str(group_id)+"__/"+str(participant_id)


class RekeySa:
    def __init__(self, nonce_range, changed_keys=None):
        self.changed_keys = changed_keys
        self.nonce_range = nonce_range


class MqttMesssageData:
    connected_mqtt = False
    publisher_GCKS = None

    @staticmethod
    def initiate_mqtt_connection():
        broker_address = "iot.eclipse.org"  # "broker.mqttdashboard.com"  # use external broker
        MqttMesssageData.publisher_GCKS = mqtt.Client("P3")  # create new instance
        MqttMesssageData.publisher_GCKS.connect(broker_address)
        MqttMesssageData.connected_mqtt = True


    def __init__(self, rekey_sa, topic, encryption_key):
        self.rekey_sa = copy.copy(rekey_sa)
        self.topic = topic
        self.encryption_key = encryption_key

    def send_message(self):
        # try something else here later
        #broker_address = "iot.eclipse.org"  # use external broker
        # publisher_GCKS = mqtt.Client("GCKS")  # create new instance
        # publisher_GCKS.connect(broker_address)
        # logic to send message
        pass

    @staticmethod
    def send_rekey_message(message, topic, encryption_key):
        if type(message) is dict:
            mqtt_message = dict()
            for key, value in message.items():
                if key is 'publisher_public_key' and value is not None:
                    mqtt_message['publisher_public_key'] = value.encode(HexEncoder).decode()
                if key is 'subscriber_public_key' and value is not None:
                    mqtt_message['subscriber_public_key'] = value.encode(HexEncoder).decode()
                if key is 'publisher_private_key' and value is not None:
                    mqtt_message['publisher_private_key'] = value.encode(HexEncoder).decode()
                if key is 'subscriber_private_key' and value is not None:
                    mqtt_message['subscriber_private_key'] = value.encode(HexEncoder).decode()
        else:
            mqtt_message = message.hex()

        message_to_bytes = json.dumps(mqtt_message).encode('utf-8')

        if MqttMesssageData.connected_mqtt:
                # digitally sign the encrypted message with GCKS signing key
                signed = crypto.digital_sign_message(DataSA.GCKS_Signing_Key, crypto.encrypt_secret_key(encryption_key, message_to_bytes))
                MqttMesssageData.publisher_GCKS.publish(topic, signed)
                # MqttMesssageData.publisher_GCKS.publish(topic,  message_to_bytes)
                print("sent message: " + json.dumps(mqtt_message))
                print("sent topic: " + topic)
                print("encryption key:")
                print(encryption_key)

        else:
                MqttMesssageData.initiate_mqtt_connection()
                signed = crypto.digital_sign_message(DataSA.GCKS_Signing_Key, crypto.encrypt_secret_key(encryption_key,
                                                                                                        message_to_bytes))
                #verified = crypto.digital_sign_verify(bytes.fromhex(DataSA.GCKS_Verify_Key.hex()), signed)
                print("signed message:")
                print(signed)
                MqttMesssageData.publisher_GCKS.publish(topic, signed)
                #MqttMesssageData.publisher_GCKS.publish(topic, message_to_bytes)
                print("sent message: " + json.dumps(mqtt_message))
                print("sent topic: " + topic)
                print("encryption key:")
                print(encryption_key)

    @staticmethod
    def change_structure_message(ancestor_keys, new_rekey_topics, encryption_key, participant_id, group_id):
        # set a common change structure type message topic
        publisher_public_key = None
        subscriber_public_key = None
        publisher_private_key = None
        subscriber_private_key = None
        for key, value in ancestor_keys[0]['key'].items():
            if key is 'publisher_public_key' and value is not None:
                publisher_public_key = value.encode(HexEncoder).decode()
            if key is 'subscriber_public_key' and value is not None:
                subscriber_public_key = value.encode(HexEncoder).decode()
            if key is 'publisher_private_key' and value is not None:
                publisher_private_key = value.encode(HexEncoder).decode()
            if key is 'subscriber_private_key' and value is not None:
                subscriber_private_key = value.encode(HexEncoder).decode()

        data_sa_json = {

            'ancestor_keys': ancestor_keys[1:],
            'group_keys': {'publisher_public_key': publisher_public_key,
                           'subscriber_public_key': subscriber_public_key,
                           'publisher_private_key': publisher_private_key,
                           'subscriber_private_key': subscriber_private_key},
            'rekey_topics': new_rekey_topics
        }

        if not MqttMesssageData.connected_mqtt:
            MqttMesssageData.initiate_mqtt_connection()

        # encrypt message and digitally sign it with GCKS signing key
        signed = crypto.digital_sign_message(DataSA.GCKS_Signing_Key, crypto.encrypt_secret_key(encryption_key,
                                                                                                json.dumps(data_sa_json).encode('utf-8')))

        MqttMesssageData.publisher_GCKS.publish("changeGroupStructure__" + str(group_id) + "__/" + str(participant_id),
                                                signed)
        # MqttMesssageData.publisher_GCKS.publish("changeGroupStructure__" + str(group_id) + "__/" + str(participant_id), json.dumps(data_sa_json))
        print("message and topic :")
        print(json.dumps(data_sa_json))
        print("changeGroupStructure__" + str(group_id) + "__/" + str(participant_id))



class GroupController:

    @staticmethod
    def set_up_group_lkh(group, participants_permissions=None, tree_sizes=None):
        KeyManager.setup_group_trees(group, participants_permissions, tree_sizes)

    @staticmethod
    def set_up_group_gkmp(group):
        KeyManagerGKMP.set_up_gkmp_group(group)

    @staticmethod
    def add_participant_lkh(group, participant, permissions):
        result = KeyManager.add_or_delete_participant(group, participant, permissions, True, False)
        # check again
        # to get the exact tree
        group_tree_map = [x for x in KeyManager.group_tree_mapping_list if x.group.id == group.id][0]
        tree = Node(group.group_name)
        tree_type_name = ''
        if permissions is 1:
            tree = copy.deepcopy(group_tree_map.root_tree_publishers)
            tree_type_name = 'pub'
        if permissions is 2:
            tree = copy.deepcopy(group_tree_map.root_tree_subscribers)
            tree_type_name = 'sub'
        if permissions is 3:
            tree = copy.deepcopy(group_tree_map.root_tree_pub_sub)
            tree_type_name = 'pub_sub'

        if result['tree_structure_change'] is False:
            for message in result['add_participant'][0]:
                update_msg_topic_name = str(group.id) + result['add_participant'][1]['tree_type'] + message[
                    'message_name']
                # todo - nonce range logic
                rekey_sa = RekeySa(3)
                '''if type(message['changed_parent_key']) is dict:
                    # major nacl changes
                    # message_to_bytes = json.dumps(message['changed_parent_key'])
                    # no bytes here encoding problem
                    # message_to_bytes = json.dumps(message['changed_parent_key']).encode('utf-8')
                    rekey_sa.changed_keys = message['changed_parent_key']
                else:
                    message_to_bytes = message['changed_parent_key']'''
                rekey_sa.changed_keys = ['changed_parent_key']
                MqttMesssageData.send_rekey_message(message['changed_parent_key'], update_msg_topic_name, message['encryption_key'])
                # time.sleep(2)
                # rekey_message = MqttMesssageData(rekey_sa, update_msg_topic_name, message['encryption_key'])
                # rekey_message.send_message()
        else:

            # send strucutre change message
            # check participants in the group
            # send all the new ancestors and changed keys, except for the participant
            # or just the new ancestor and all keys
            leaves = tree.leaves
            for leaf in leaves:
                if leaf.leaf_node.participant is not None and leaf.leaf_node.participant.participant_id is not participant.participant_id:

                    ancestor_list = (findall_by_attr(tree, leaf.leaf_node.participant.participant_id))[0].ancestors
                    ancestor_keys, topic_to_sub_enc_keys = GroupController.__get_ancestors_and_keys(ancestor_list,
                                                                                                    group,
                                                                                                    tree_type_name,
                                                                                                    leaf.leaf_node.participant)
                    MqttMesssageData.change_structure_message(ancestor_keys, topic_to_sub_enc_keys,
                                                              leaf.leaf_node.participant.pairwise_key,
                                                              leaf.leaf_node.participant.participant_id, group.id)

        # update other trees where group keys changed
        for trees in result['update_tree']:
            for message in trees[0]:
                update_msg_topic_name = group.group_id + trees[1]['tree_type'] + message['message_name']
                msg_updated_key = str(message['changed_parent_key'])+" "+str(message['encryption_key'])
                rekey_sa = RekeySa(3)
                # not here
                '''if type(message['changed_parent_key']) is dict:
                    # nacl change
                    # message_to_bytes = json.dumps(message['changed_parent_key'])
                    message_to_bytes = json.dumps(message['changed_parent_key']).encode('utf-8')
                    rekey_sa.changed_keys = message_to_bytes
                else:
                    message_to_bytes = message['changed_parent_key']'''
                rekey_sa.changed_keys = message['changed_parent_key']
                rekey_message = MqttMesssageData(rekey_sa, update_msg_topic_name, message['encryption_key'])
                rekey_message.send_message()

        # now return to registration DATA SA
        data_sa = DataSA(permissions, participant.pairwise_key, "LKH")
        # recheck
        ancestor_list = (findall_by_attr(tree, participant.participant_id))[0].ancestors
        # # print(ancestor_list)

        # make a dictionary/json of tree node names and key possessed by it
        # since participant would need keys of all its ancestors

        ancestor_keys, topic_to_sub_enc_keys = GroupController.__get_ancestors_and_keys(ancestor_list, group,
                                                                                        tree_type_name, participant)

        data_sa.key_management_type = KeyManagementProtocols.LKH.value
        data_sa.set_ancestor_keys(ancestor_keys)
        data_sa.set_group_keys(ancestor_keys[0]['key'])
        data_sa.set_nonce_prefix(3) #-- todo
        data_sa.set_rekey_topics(topic_to_sub_enc_keys)
        data_sa.set_subscriptions(group.topics)
        data_sa.set_request_rekey_topic("todo")
        data_sa.set_pairwise_key(participant.pairwise_key)
        data_sa.set_participant_id(participant.participant_id)
        data_sa.set_group_topics(group.topics)
        data_sa.set_group_id(group.id)
        data_sa.set_change_tree_structure_topic(group.id, participant.participant_id)
        return data_sa

    @staticmethod
    def add_participant_gkmp():
        pass

    @staticmethod
    def delete_participant_lkh():
        pass

    @staticmethod
    def delete_participant_gkmp():
        pass

    @staticmethod
    def rekey_lkh():
        pass

    @staticmethod
    def rekey_gkmp():
        pass

    def __send_message(self, mqtt_message_data_list):
        pass

    @staticmethod
    def __get_ancestors_and_keys(ancestor_list, group, tree_type_name, participant):
        ancestor_keys = []
        topic_to_sub_enc_keys = []
        # get all ancestor keys
        i = 0
        while i < len(ancestor_list):
            if ancestor_list[i].is_root is True:
                ancestor_keys.append({'name': str(ancestor_list[i].tree_node.node_id),
                                      # problem with json byte encoding
                                      # 'key': ancestor_list[i].tree_node.root_node_keys})
                                      'key': ancestor_list[i].tree_node.root_node_keys})
            else:
                ancestor_keys.append({'name': str(ancestor_list[i].tree_node.node_id),
                                      # nacl change
                                      'key': ancestor_list[i].tree_node.node_key.hex()})

            if i != len(ancestor_list) - 1:
                topic_to_sub_enc_keys.append({'topic_to_sub': group.id + tree_type_name +
                                                              str(ancestor_list[
                                                                      i].tree_node.node_id) + '/' +
                                                              str(ancestor_list[i + 1].tree_node.node_id) +
                                                              "__changeParent__" + str(
                    ancestor_list[i].tree_node.node_id),
                                              # 'enc_key': ancestor_list[i + 1].tree_node.node_key})
                                              # problem with json byte encoding
                                              # nacl change
                                              'enc_key': ancestor_list[i + 1].tree_node.node_key.hex()})

            else:
                topic_to_sub_enc_keys.append({'topic_to_sub': group.id + tree_type_name +
                                                              str(ancestor_list[
                                                                      i].tree_node.node_id) + '/' +
                                                              participant.participant_id + "__changeParent__" +
                                                              str(ancestor_list[i].tree_node.node_id),
                                              # 'enc_key': client.pairwise_key})
                                              # problem with json byte encoding
                                              # nacl change
                                              'enc_key': participant.pairwise_key.hex()})

            i = i + 1
        return ancestor_keys, topic_to_sub_enc_keys
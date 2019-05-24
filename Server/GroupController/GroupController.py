from Server.KeyManager.PubSubKeyManagerTreeType import KeyManager
from Server.KeyManager.KeyManagerGKMP import KeyManagerGKMP
from Server.CustomClasses.Group import Group
import paho.mqtt.client as mqtt
import json
import copy
from anytree import Node, RenderTree, findall_by_attr, findall, Resolver


class DataSA:
    # todo GCKS public and private keys
    GCKS_public_key = None

    def __init__(self, permissions, pairwise_key, key_management_type):
        self.key_management_type = key_management_type
        self.ancestor_keys = list()
        self.group_keys = dict()
        # type of enc publishing messages
        # type of dec sub messages
        # type of auth GCKS
        self.nonce_prefix = None
        self.permissions = permissions
        self.subscriptions = list()
        self.pairwise_key = pairwise_key
        self.rekey_topics_keys = list()
        self.request_rekey_topic = None

    @staticmethod
    def set_gcks_public_key(public_key=None):
        # DataSA.GCKS_public_key = generate_key() - todo
        pass

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

class RekeySa:
    def __init__(self, nonce_range, changed_keys=None):
        self.changed_keys = changed_keys
        self.nonce_range = nonce_range


class MqttMesssageData:

    def __init__(self, rekey_sa, topic, encryption_key):
        self.rekey_sa = copy.copy(rekey_sa)
        self.topic = topic
        self.encryption_key = encryption_key

    def send_message(self):
        # try something else here later
        broker_address = "iot.eclipse.org"  # use external broker
        publisher_GCKS = mqtt.Client("GCKS")  # create new instance
        publisher_GCKS.connect(broker_address)
        # logic to send message


class GroupController:

    @staticmethod
    def set_up_group_lkh(group, participants_permissions=None, tree_sizes=None):
        KeyManager.setup_group_trees(group, participants_permissions, tree_sizes)

    @staticmethod
    def set_up_group_gkmp(group):
        KeyManagerGKMP.set_up_gkmp_group(group)

    @staticmethod
    def add_participant_lkh(participant, permissions, group):
        result = KeyManager.add_or_delete_participant(group, participant, permissions, True, False)
        # check again
        for message in result['add_participant'][0]:
            update_msg_topic_name = group.group_id + result['add_participant'][1]['tree_type'] + message[
                'message_name']
            # todo - nonce range logic
            rekey_sa = RekeySa(3)
            if type(message['changed_parent_key']) is dict:
                # major nacl changes
                # message_to_bytes = json.dumps(message['changed_parent_key'])
                message_to_bytes = json.dumps(message['changed_parent_key']).encode('utf-8')
                rekey_sa.changed_keys = message_to_bytes
            else:
                message_to_bytes = message['changed_parent_key']
                rekey_sa.changed_keys = message_to_bytes

            rekey_message = MqttMesssageData(rekey_sa, update_msg_topic_name, message['encryption_key'])
            rekey_message.send_message()

        # update other trees where group keys changed
        for tree in result['update_tree']:
            for message in tree[0]:
                update_msg_topic_name = group.group_id + tree[1]['tree_type'] + message['message_name']
                msg_updated_key = str(message['changed_parent_key'])+" "+str(message['encryption_key'])
                rekey_sa = RekeySa(3)

                if type(message['changed_parent_key']) is dict:
                    # nacl change
                    # message_to_bytes = json.dumps(message['changed_parent_key'])
                    message_to_bytes = json.dumps(message['changed_parent_key']).encode('utf-8')
                    rekey_sa.changed_keys = message_to_bytes
                else:
                    message_to_bytes = message['changed_parent_key']
                    rekey_sa.changed_keys = message_to_bytes
                rekey_message = MqttMesssageData(rekey_sa, update_msg_topic_name, message['encryption_key'])
                rekey_message.send_message()

        # now return to registration DATA SA
        data_sa = DataSA(permissions, participant.pairwise_key, "LKH")
        group_tree_map = [x for x in KeyManager.group_tree_mapping_list if x.group.id == group.id][0]
        tree = Node(group.group_name)
        tree_type_name = ''
        if permissions is 1:
            tree = copy.deepcopy(group_tree_map.topic.root_tree_publishers)
            tree_type_name = 'pub'
        if permissions is 2:
            tree = copy.deepcopy(group_tree_map.topic.root_tree_subscribers)
            tree_type_name = 'sub'
        if permissions is 3:
            tree = copy.deepcopy(group_tree_map.topic.root_tree_pub_sub)
            tree_type_name = 'pub_sub'

        # recheck
        ancestor_list = (findall_by_attr(tree, participant.participant_id))[0].ancestors
        # # print(ancestor_list)

        # make a dictionary/json of tree node names and key possessed by it
        # since participant would need keys of all its ancestors
        ancestor_keys = []
        topic_to_sub_enc_keys = []
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
                topic_to_sub_enc_keys.append({'topic_to_sub': group.group_name + tree_type_name +
                                                              str(ancestor_list[i].tree_node.node_id) + '/' +
                                                              str(ancestor_list[i + 1].tree_node.node_id) +
                                                              "__changeParent__" + str(
                    ancestor_list[i].tree_node.node_id),
                                              # 'enc_key': ancestor_list[i + 1].tree_node.node_key})
                                              # problem with json byte encoding
                                              # nacl change
                                              'enc_key': ancestor_list[i + 1].tree_node.node_key.hex()})

            else:
                topic_to_sub_enc_keys.append({'topic_to_sub': group.group_name + tree_type_name +
                                                              str(ancestor_list[i].tree_node.node_id) + '/' +
                                                              participant.participant_id + "__changeParent__" +
                                                              str(ancestor_list[i].tree_node.node_id),
                                              # 'enc_key': client.pairwise_key})
                                              # problem with json byte encoding
                                              # nacl change
                                              'enc_key': participant.pairwise_key.hex()})

            i = i + 1
        # data_sa.request_rekey_topic("--todo ") # --todo
        data_sa.set_ancestor_keys(ancestor_keys)
        data_sa.set_gcks_public_key("key") # todo
        data_sa.set_group_keys(ancestor_keys[0])
        data_sa.set_nonce_prefix(3) #-- todo
        data_sa.set_rekey_topics(topic_to_sub_enc_keys)
        data_sa.set_subscriptions(group.topics)
        data_sa.set_request_rekey_topic("todo")

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
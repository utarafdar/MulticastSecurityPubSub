from Server.KeyManager.PubSubKeyManagerTreeType import KeyManager
from Server.KeyManager.KeyManagerGKMP import KeyManagerGKMP
from Server.CustomClasses.CustomEnums import KeyManagementProtocols, TypeOfPubSubGroupEnum, PermissionTypesEnum
from Server.Authorization.Authorization import Authorization
import paho.mqtt.client as mqtt
import json
import os
from anytree import Node, findall_by_attr
from nacl.encoding import HexEncoder
import timeit
import Server.CustomClasses.cryptography as crypto
import random
import math
import sys

class GroupControllerMqttTopicsListner:
    connected_mqtt = False
    publisher_GCKS = None

    @staticmethod
    def __on_subscribe(client, userdata, mid, granted_qos):
        # print("subcription called")
        pass

    @staticmethod
    def __on_message_rekey_request(client, userdata, msg):
        # 1. split topic based on '/'
        # 2. get group id and client id from that
        # 3. find the participant from the group id and participant id groups
        # 4. verify the message using participant pairwise key
        # 5. call the function to change the group keys

        group_id = msg.topic.split('/')[1]
        client_id = msg.topic.split('/')[2]
        participant = None

        group = [x for x in Authorization.groups if x.id == group_id][0]

        for key, value in group.participants_permissions.items():
            if key.participant_id == client_id:
                participant = key
                permissions = value
                break
        # verify topic
        dec_message = crypto.decrypt_secret_key(participant.pairwise_key, msg.payload).decode("utf-8", "ignore")

        if dec_message != msg.topic:
            return

        if group.type_of_key_management_protocol is KeyManagementProtocols.GKMP.value:
            GroupController.change_group_keys_gkmp(group)

        if group.type_of_key_management_protocol is KeyManagementProtocols.LKH.value:
            GroupController.change_group_keys_lkh(group)


    @staticmethod
    def __on_message_leave_client(client, userdata, msg):
        # 1. split topic based on '/'
        # 2. get group id and client id from that
        # 3. find the participant from the group id and participant id groups
        # 4. verify the message using participant pairwise key
        # 5. delete participant
        # 6. may be ====send confirmation over mqtt (encrypted with pairwise key)

        group_id = msg.topic.split('/')[1]
        client_id = msg.topic.split('/')[2]
        permissions = None
        participant = None

        group = [x for x in Authorization.groups if x.id == group_id][0]

        for key, value in group.participants_permissions.items():
            if key.participant_id == client_id:
                participant = key
                permissions = value
                break
        # verify topic
        dec_message = crypto.decrypt_secret_key(participant.pairwise_key, msg.payload).decode("utf-8", "ignore")

        if dec_message != msg.topic:
            return

        if group.type_of_key_management_protocol is KeyManagementProtocols.GKMP.value:
            GroupController.delete_participant_gkmp(group, participant, permissions)

        if group.type_of_key_management_protocol is KeyManagementProtocols.LKH.value:
            GroupController.delete_participant_lkh(group, participant, permissions)

    @staticmethod
    def initiate_mqtt_connection():
        broker_address = "iot.eclipse.org"#"broker.mqttdashboard.com" #  # "linksmart-dev.fit.fraunhofer.de"## "broker.mqttdashboard.com"  # use external broker
        GroupControllerMqttTopicsListner.publisher_GCKS = mqtt.Client("P3")  # create new instance
        GroupControllerMqttTopicsListner.publisher_GCKS.connect(broker_address)
        # print("done")
        GroupControllerMqttTopicsListner.connected_mqtt = True
        GroupControllerMqttTopicsListner.publisher_GCKS.on_subscribe = GroupControllerMqttTopicsListner.__on_subscribe
        GroupControllerMqttTopicsListner.listen_to_group_control_topics()


    @staticmethod
    def listen_to_group_control_topics():
        # subscribe to all group leave topics:

        # group leave topics
        GroupControllerMqttTopicsListner.publisher_GCKS.subscribe(topic="client_leave_group/#", qos=1)
        GroupControllerMqttTopicsListner.publisher_GCKS.message_callback_add("client_leave_group/#",
                                    GroupControllerMqttTopicsListner.__on_message_leave_client)

        # rekey request topics
        GroupControllerMqttTopicsListner.publisher_GCKS.subscribe(topic="request_group_keys_change/#", qos=1)
        GroupControllerMqttTopicsListner.publisher_GCKS.message_callback_add("request_group_keys_change/#",
                                                                             GroupControllerMqttTopicsListner.__on_message_rekey_request)

        # start listening to leave participant topics
        GroupControllerMqttTopicsListner.publisher_GCKS.loop_start()
        while True:
            pass


    @staticmethod
    def send_rekey_message(message, topic, encryption_key, random_sequence, nonce_prefix_size=None,
                           nonce_prefix_value=None, group_eval=None):
        # print(message)
        # print(topic)
        if type(message) is dict:
            mqtt_message = dict()
            mqtt_message['key_sequence_number'] = random_sequence
            #if nonce_prefix_value is not None:
            mqtt_message['nonce_prefix_value'] = nonce_prefix_value
            mqtt_message['nonce_prefix_size'] = nonce_prefix_size
            for key, value in message.items():
                if key is 'publisher_public_key' and value is not None:
                    mqtt_message['publisher_public_key'] = value.encode(HexEncoder).decode()
                if key is 'subscriber_public_key' and value is not None:
                    mqtt_message['subscriber_public_key'] = value.encode(HexEncoder).decode()
                if key is 'publisher_private_key' and value is not None:
                    mqtt_message['publisher_private_key'] = value.encode(HexEncoder).decode()
                if key is 'subscriber_private_key' and value is not None:
                    mqtt_message['subscriber_private_key'] = value.encode(HexEncoder).decode()
                if key is 'common_key' and value is not None:
                    mqtt_message['common_key'] = value.hex()
        else:
            mqtt_message = message.hex()
        # integrity of topic
        message_and_topic = {"message": mqtt_message,
                             "topic": topic}
        # message_to_bytes = json.dumps(mqtt_message).encode('utf-8')
        message_to_bytes = json.dumps(message_and_topic).encode('utf-8')

        if GroupControllerMqttTopicsListner.connected_mqtt:
            # digitally sign the encrypted message with GCKS signing key
            signed = crypto.digital_sign_message(DataSA.GCKS_Signing_Key,
                                                 crypto.encrypt_secret_key(encryption_key, message_to_bytes))
            GroupControllerMqttTopicsListner.publisher_GCKS.publish(topic, signed)
            # MqttMesssageData.publisher_GCKS.publish(topic,  message_to_bytes)



        else:
            GroupControllerMqttTopicsListner.initiate_mqtt_connection()
            signed = crypto.digital_sign_message(DataSA.GCKS_Signing_Key, crypto.encrypt_secret_key(encryption_key,
                                                                                                    message_to_bytes))
            # verified = crypto.digital_sign_verify(bytes.fromhex(DataSA.GCKS_Verify_Key.hex()), signed)

            GroupControllerMqttTopicsListner.publisher_GCKS.publish(topic, signed)
            # MqttMesssageData.publisher_GCKS.publish(topic, message_to_bytes)
            # evauation
        if GroupController.evaluation_flags['rekey_message_size'] == "True":
            absolute_path = os.path.dirname(__file__)
            file_name = os.path.join(absolute_path, '../Evaluation/logs/rekey_size_' +
                                     str(group_eval.type_of_key_management_protocol) + '_' + str(
                group_eval.type_of_pub_sub_group)
                                     + '.txt')
            f = open(file_name, "a+")
            f.write(str(sys.getsizeof(signed)) + "\n")
            f.close()

    @staticmethod
    def change_structure_message(ancestor_keys, new_rekey_topics, encryption_key, participant_id, group_id,
                                 random_sequence, nonce_prefix_size, nonce_prefix_value, group_eval=None):
        # print("structure change")
        # print(str(group_id) + "__" + "changeGroupStructure" + "/" + str(participant_id))


        # set a common change structure type message topic

        publisher_public_key = None
        subscriber_public_key = None
        publisher_private_key = None
        subscriber_private_key = None
        common_key = None
        for key, value in ancestor_keys[0]['key'].items():
            if key is 'publisher_public_key' and value is not None:
                publisher_public_key = value.encode(HexEncoder).decode()
            if key is 'subscriber_public_key' and value is not None:
                subscriber_public_key = value.encode(HexEncoder).decode()
            if key is 'publisher_private_key' and value is not None:
                publisher_private_key = value.encode(HexEncoder).decode()
            if key is 'subscriber_private_key' and value is not None:
                subscriber_private_key = value.encode(HexEncoder).decode()
            if key is 'common_key' and value is not None:
                common_key = value.hex()

        # topic integrity
        keys = {

            'ancestor_keys': ancestor_keys[1:],
            'group_keys': {'publisher_public_key': publisher_public_key,
                           'subscriber_public_key': subscriber_public_key,
                           'publisher_private_key': publisher_private_key,
                           'subscriber_private_key': subscriber_private_key,
                           'common_key': common_key,
                           'key_sequence_number': random_sequence},
            'rekey_topics': new_rekey_topics,
            'nonce_prefix_size': nonce_prefix_size,
            'nonce_prefix_value': nonce_prefix_value
        }
        data_sa_json = {"message": keys,
                        "topic": str(group_id) + "__" + "changeGroupStructure" + "/" + str(participant_id)}

        if not GroupControllerMqttTopicsListner.connected_mqtt:
            GroupControllerMqttTopicsListner.initiate_mqtt_connection()

        # encrypt message and digitally sign it with GCKS signing key
        signed = crypto.digital_sign_message(DataSA.GCKS_Signing_Key, crypto.encrypt_secret_key(encryption_key,
                                                                                                json.dumps(
                                                                                                    data_sa_json).encode(
                                                                                                    'utf-8')))

        GroupControllerMqttTopicsListner.publisher_GCKS.publish(
            str(group_id) + "__" + "changeGroupStructure" + "/" + str(participant_id),
            signed)

        #evauation
        if GroupController.evaluation_flags['rekey_message_size'] == "True":
            absolute_path = os.path.dirname(__file__)
            file_name = os.path.join(absolute_path, '../Evaluation/logs/rekey_size_' +
                                     str(group_eval.type_of_key_management_protocol) + '_' + str(
                group_eval.type_of_pub_sub_group)
                                     + '.txt')
            f = open(file_name, "a+")
            f.write(str(sys.getsizeof(signed)) + "\n")
            f.close()

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
        self.type_of_group = None
        self.rekey_gkmp_topic = None
        self.leave_group_topic = None
        self.leave_group_confirmation_topic = None
        self.key_sequence_number = None
        self.nonce_prefix_value = None
        self.nonce_prefix_size = None

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

    def set_type_of_group(self, type_of_group):
        self.type_of_group = type_of_group

    def set_participant_id(self, participant_id):
        self.participant_id = participant_id

    def set_group_topics(self, group_topics):
        for topic in group_topics:
            self.topics.append({'topic_name': topic.topicName,
                                'topic_id': topic.topic_id})

    def set_group_id(self, group_id):
        self.group_id = str(group_id)

    def set_change_tree_structure_topic(self, group_id, participant_id):
        self.change_tree_structure_topic = str(group_id)+"__" +"changeGroupStructure"+"/"+str(participant_id)


class RekeySa:
    def __init__(self, nonce_range, changed_keys=None):
        self.changed_keys = changed_keys
        self.nonce_range = nonce_range


class GroupController:

    evaluation_flags = dict()

    @staticmethod
    def set_up_group_lkh(group, participants_permissions=None, tree_sizes=None):
        KeyManager.setup_group_trees(group, participants_permissions, tree_sizes)

    @staticmethod
    def set_up_group_gkmp(group):
        KeyManagerGKMP.set_up_gkmp_group(group)

    @staticmethod
    def change_group_keys_gkmp(group):
        group.current_key_sequence_number = random.randint(1, 100000)

        result = KeyManagerGKMP.update_group_keys(group)

        for message_data in result:
            GroupControllerMqttTopicsListner.send_rekey_message(message_data['changed_parent_key'],
                                                                message_data['message_name'],
                                                                message_data['encryption_key'],
                                                                group.current_key_sequence_number, group_eval=group)

    @staticmethod
    def change_group_keys_lkh(group):
        group.current_key_sequence_number = random.randint(1, 100000)
        result = KeyManager.update_group_keys(group)
        for tree in result:
            for message in tree[0]:
                update_msg_topic_name = str(group.id) + "__" + tree[1]['tree_type'] + message[
                                        'message_name']
                rekey_sa = RekeySa(3)
                # print(update_msg_topic_name)
                rekey_sa.changed_keys = message['changed_parent_key']
                GroupControllerMqttTopicsListner.send_rekey_message(message['changed_parent_key'], update_msg_topic_name,
                                                    message['encryption_key'], group.current_key_sequence_number, group_eval=group)

    @staticmethod
    def add_participant_lkh(group, participant, permissions):
        group.current_key_sequence_number = random.randint(1, 100000)
        result = KeyManager.add_or_delete_participant(group, participant, permissions, True, False)

        group_tree_map = [x for x in KeyManager.group_tree_mapping_list if x.group.id == group.id][0]

        # keeping unique nonce -fix
        nonce_prefix_size = None
        nonce_prefix_value = None
        if group.type_of_pub_sub_group is TypeOfPubSubGroupEnum.ALL_PUBSUB.value:
            nonce_prefix_size = 0
            nonce_prefix_value = -1
            no_of_leaves = len(group_tree_map.root_tree_common.leaves)
            nonce_prefix_size = math.ceil(math.log2(no_of_leaves))

        tree = Node(group.group_name)
        tree_type_name = ''
        if permissions is 1:
            tree = group_tree_map.root_tree_publishers
            tree_type_name = 'pub'
        if permissions is 2:
            tree = group_tree_map.root_tree_subscribers
            tree_type_name = 'sub'
        if permissions is 3:
            if group.type_of_pub_sub_group is TypeOfPubSubGroupEnum.ALL_PUBSUB.value:
                tree = group_tree_map.root_tree_common
                tree_type_name = 'common'
            else:
                tree = group_tree_map.root_tree_pub_sub
                tree_type_name = 'pub_sub'

        if result['tree_structure_change'] is False:
            for message in result['add_participant'][0]:
                # for sequenctial nonce
                #if group.type_of_pub_sub_group is TypeOfPubSubGroupEnum.ALL_PUBSUB.value:
                    #nonce_prefix_value += 1
                update_msg_topic_name = str(group.id)+"__" + result['add_participant'][1]['tree_type'] + message[
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
                GroupControllerMqttTopicsListner.send_rekey_message(message['changed_parent_key'], update_msg_topic_name,
                                                                    message['encryption_key'],
                                                                    group.current_key_sequence_number, group_eval=group)
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
                    if group.type_of_pub_sub_group is TypeOfPubSubGroupEnum.ALL_PUBSUB.value:
                        nonce_prefix_value += 1
                    ancestor_list = (findall_by_attr(tree, leaf.leaf_node.participant.participant_id))[0].ancestors
                    ancestor_keys, topic_to_sub_enc_keys = GroupController.__get_ancestors_and_keys(ancestor_list,
                                                                                                    group,
                                                                                                    tree_type_name,
                                                                                                    leaf.leaf_node.participant)
                    GroupControllerMqttTopicsListner.change_structure_message(ancestor_keys, topic_to_sub_enc_keys,
                                                              leaf.leaf_node.participant.pairwise_key,
                                                              leaf.leaf_node.participant.participant_id, group.id,
                                                              group.current_key_sequence_number, nonce_prefix_size,
                                                                              nonce_prefix_value, group_eval=group)
                    # update the nonce prefix for the participant
                    leaf.leaf_node.participant.nonce_prefix_value = nonce_prefix_value

        # update other trees where group keys changed
        for trees in result['update_tree']:
            for message in trees[0]:
                # update_msg_topic_name = str(group.id)+"__" + trees[1]['tree_type'] + message['message_name']
                update_msg_topic_name = str(group.id) + "__" + trees[1]['tree_type'] + message[
                                        'message_name']
                # # print(str(group.id)+"__" + trees[1]['tree_type'] + message['message_name'])
                # msg_updated_key = str(message['changed_parent_key'])+" "+str(message['encryption_key'])
                rekey_sa = RekeySa(3)
                # print(update_msg_topic_name)
                rekey_sa.changed_keys = message['changed_parent_key']
                GroupControllerMqttTopicsListner.send_rekey_message(message['changed_parent_key'], update_msg_topic_name,
                                                    message['encryption_key'], group.current_key_sequence_number, group_eval=group)
                # time.sleep(2)
        if group.type_of_pub_sub_group is TypeOfPubSubGroupEnum.ALL_PUBSUB.value:
            if len(group.nonce_free_prefix_values) == 0:
                leaves = tree.leaves
                number_of_participants = -1
                for leaf in leaves:
                    if leaf.leaf_node.participant is not None:
                        number_of_participants += 1
                nonce_prefix_value = number_of_participants
            else:
                nonce_prefix_value = group.nonce_free_prefix_values[0]
                del group.nonce_free_prefix_values[0]
            participant.nonce_prefix_value = nonce_prefix_value
        # now return to registration DATA SA
        data_sa = DataSA(permissions, participant.pairwise_key, "LKH")
        # recheck
        ancestor_list = (findall_by_attr(tree, participant.participant_id))[0].ancestors
        # # # print(ancestor_list)

        # make a dictionary/json of tree node names and key possessed by it
        # since participant would need keys of all its ancestors

        ancestor_keys, topic_to_sub_enc_keys = GroupController.__get_ancestors_and_keys(ancestor_list, group,
                                                                                        tree_type_name, participant)

        data_sa.key_management_type = KeyManagementProtocols.LKH.value
        data_sa.set_ancestor_keys(ancestor_keys)
        data_sa.set_group_keys(ancestor_keys[0]['key'])
        data_sa.set_rekey_topics(topic_to_sub_enc_keys)
        data_sa.set_subscriptions(group.topics)
        data_sa.set_request_rekey_topic("request_group_keys_change/" + group.id + "/" + participant.participant_id)
        data_sa.set_pairwise_key(participant.pairwise_key)
        data_sa.set_participant_id(participant.participant_id)
        data_sa.set_group_topics(group.topics)
        data_sa.set_group_id(group.id)
        data_sa.set_type_of_group(group.type_of_pub_sub_group)
        data_sa.set_change_tree_structure_topic(group.id, participant.participant_id)
        data_sa.leave_group_topic = "client_leave_group/" + group.id + "/" + participant.participant_id
        data_sa.leave_group_confirmation_topic = "client_leave_group_confirmation/"+ group.id + "/" + participant.participant_id
        data_sa.key_sequence_number = group.current_key_sequence_number
        data_sa.nonce_prefix_value = nonce_prefix_value
        data_sa.nonce_prefix_size = nonce_prefix_size
        return data_sa

    @staticmethod
    def add_participant_gkmp(group, participant, permissions):
        group.current_key_sequence_number = random.randint(1, 100000)
        result = KeyManagerGKMP.add_or_delete_participant(group, participant, permissions, True, False)
        gkmp_list_group = [x for x in KeyManagerGKMP.group_gkmp_mapping_list if x.group.id == group.id][0]

        nonce_prefix_size = None
        nonce_prefix_value = None

        if group.type_of_pub_sub_group is TypeOfPubSubGroupEnum.ALL_PUBSUB.value:
            no_of_participants = len(gkmp_list_group.publishers_and_subscribers)
            nonce_prefix_size = math.ceil(math.log2(no_of_participants))
            #nonce_prefix_size = 0
            nonce_prefix_value = -1


        for message_data in result[0]:
            if group.type_of_pub_sub_group is TypeOfPubSubGroupEnum.ALL_PUBSUB.value:
                nonce_prefix_value += 1
            GroupControllerMqttTopicsListner.send_rekey_message(message_data['changed_parent_key'], message_data['message_name'],
                                                message_data['encryption_key'], group.current_key_sequence_number, nonce_prefix_size,
                                                                nonce_prefix_value, group_eval=group)
        participant_group_keys = result[1]
        # now return to registration DATA SA
        data_sa = DataSA(permissions, participant.pairwise_key, "GKMP")

        data_sa.key_management_type = KeyManagementProtocols.GKMP.value
        data_sa.set_nonce_prefix(3)  # -- todo
        if permissions is PermissionTypesEnum.PUBLISH_AND_SUBSCRIBE.value:
            pub_sub_grp_type = "pub_sub"
        elif permissions is PermissionTypesEnum.PUBLISH.value:
            pub_sub_grp_type = "pub"
        else:
            pub_sub_grp_type = "sub"

        nonce_prefix_value += 1

        data_sa.rekey_gkmp_topic = group.id + "__" + pub_sub_grp_type + "/gkmp_key_change/" + participant.participant_id
        data_sa.set_subscriptions(group.topics)
        data_sa.set_group_keys(participant_group_keys)
        data_sa.set_request_rekey_topic("request_group_keys_change/" + group.id + "/" + participant.participant_id)
        data_sa.set_pairwise_key(participant.pairwise_key)
        data_sa.set_participant_id(participant.participant_id)
        data_sa.set_group_topics(group.topics)
        data_sa.set_group_id(group.id)
        data_sa.set_type_of_group(group.type_of_pub_sub_group)
        data_sa.leave_group_topic = "client_leave_group/" + group.id + "/" + participant.participant_id
        data_sa.leave_group_confirmation_topic = "client_leave_group_confirmation/" + group.id + "/" + participant.participant_id
        data_sa.key_sequence_number = group.current_key_sequence_number
        data_sa.nonce_prefix_value = nonce_prefix_value
        data_sa.nonce_prefix_size = nonce_prefix_size
        return data_sa


    @staticmethod
    def delete_participant_lkh(group, participant, permissions):
        group.current_key_sequence_number = random.randint(1, 100000)
        result = KeyManager.add_or_delete_participant(group, participant, permissions, False, True)

        # for nonce value in lkh type
        if group.type_of_pub_sub_group is TypeOfPubSubGroupEnum.ALL_PUBSUB.value:
            group.nonce_free_prefix_values.append(participant.nonce_prefix_value)

        for message in result['delete_participant'][0]:
            update_msg_topic_name = str(group.id) + "__" + result['delete_participant'][1]['tree_type'] + message[
                'message_name']
            # todo - nonce range logic
            rekey_sa = RekeySa(3)

            rekey_sa.changed_keys = ['changed_parent_key']
            GroupControllerMqttTopicsListner.send_rekey_message(message['changed_parent_key'], update_msg_topic_name,
                                                message['encryption_key'], group.current_key_sequence_number, group_eval=group)
        for trees in result['update_tree']:
            for message in trees[0]:
                # update_msg_topic_name = str(group.id)+"__" + trees[1]['tree_type'] + message['message_name']
                update_msg_topic_name = str(group.id) + "__" + trees[1]['tree_type'] + message[
                                        'message_name']
                # # print(str(group.id)+"__" + trees[1]['tree_type'] + message['message_name'])
                # msg_updated_key = str(message['changed_parent_key'])+" "+str(message['encryption_key'])
                rekey_sa = RekeySa(3)
                # print(update_msg_topic_name)
                rekey_sa.changed_keys = message['changed_parent_key']
                GroupControllerMqttTopicsListner.send_rekey_message(message['changed_parent_key'], update_msg_topic_name,
                                                    message['encryption_key'], group.current_key_sequence_number, group_eval=group)


    @staticmethod
    def delete_participant_gkmp(group, participant, permissions):
        group.current_key_sequence_number = random.randint(1, 100000)
        result = KeyManagerGKMP.add_or_delete_participant(group, participant, permissions, False, True)

        for message_data in result[0]:
            GroupControllerMqttTopicsListner.send_rekey_message(message_data['changed_parent_key'], message_data['message_name'],
                                                message_data['encryption_key'], group.current_key_sequence_number, group_eval=group)

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
                                      #  nacl change
                                      'key': ancestor_list[i].tree_node.node_key.hex()})

            if i != len(ancestor_list) - 1:
                topic_to_sub_enc_keys.append({'topic_to_sub': group.id+"__"+tree_type_name +
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
                topic_to_sub_enc_keys.append({'topic_to_sub': group.id+"__" + tree_type_name +
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
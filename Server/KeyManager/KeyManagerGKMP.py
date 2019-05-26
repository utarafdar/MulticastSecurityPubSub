from TreeNode import TreeNode, LeafNode
from Participant import Participant
from anytree import Node, findall_by_attr, PreOrderIter
from Topic import Topic
from Group import Group
from Server.CustomClasses.CustomEnums import PermissionTypesEnum, TypeOfPubSubGroupEnum
from PublishSubscribeTreeKeys import PublishSubscribeTreeKeys
from LKH_Protocol import LKH
import random
import nacl.utils
import nacl.secret
from nacl.public import PrivateKey, Box


class GroupGKMPMapping:

    def __init__(self, group, common_key=None, publisher_public_key=None,publisher_private_key=None, subscriber_public_key=None, subscriber_private_key=None ):
        self.group = group
        self.common_key = common_key
        self.publisher_public_key = publisher_public_key
        self.publisher_private_key = publisher_private_key
        self.subscriber_public_key = subscriber_public_key
        self.subscriber_private_key = subscriber_private_key
        self.publishers = list()
        self.subscribers = list()
        self.publishers_and_subscribers = list()


class KeyManagerGKMP:
    group_gkmp_mapping_list = list()

    @staticmethod
    def set_up_gkmp_group(group):
        group_gkmp_map = GroupGKMPMapping(group)

        if group.type_of_pub_sub_group == TypeOfPubSubGroupEnum.ALL_PUBSUB.value:
            group_gkmp_map.common_key = KeyManagerGKMP.__generate_symmetric_key()

        elif group.type_of_pub_sub_group == TypeOfPubSubGroupEnum.SOME_PUBSUB_SOME_PUB.value:
            group_gkmp_map.common_key = KeyManagerGKMP.__generate_symmetric_key()

            asymmetric_keys = KeyManagerGKMP.__generate_asymmetric_keys()
            group_gkmp_map.subscriber_private_key = asymmetric_keys[0]
            group_gkmp_map.subscriber_public_key = asymmetric_keys[1]

        elif group.type_of_pub_sub_group == TypeOfPubSubGroupEnum.SOME_PUBSUB_SOME_SUB.value:
            group_gkmp_map.common_key = KeyManagerGKMP.__generate_symmetric_key()

            asymmetric_keys = KeyManagerGKMP.__generate_asymmetric_keys()
            group_gkmp_map.publisher_private_key = asymmetric_keys[0]
            group_gkmp_map.publisher_public_key = asymmetric_keys[1]

        elif group.type_of_pub_sub_group == TypeOfPubSubGroupEnum.SOME_PUB_SOME_SUB.value:
            asymmetric_keys_sub = KeyManagerGKMP.__generate_asymmetric_keys()
            group_gkmp_map.subscriber_private_key = asymmetric_keys_sub[0]
            group_gkmp_map.subscriber_public_key = asymmetric_keys_sub[1]

            asymmetric_pub = KeyManagerGKMP.__generate_asymmetric_keys()
            group_gkmp_map.publisher_private_key = asymmetric_pub[0]
            group_gkmp_map.publisher_public_key = asymmetric_pub[1]

        elif group.type_of_pub_sub_group == TypeOfPubSubGroupEnum.SOME_PUBSUB_SOME_PUB_SOME_SUB.value:
            asymmetric_keys_sub = KeyManagerGKMP.__generate_asymmetric_keys()
            group_gkmp_map.subscriber_private_key = asymmetric_keys_sub[0]
            group_gkmp_map.subscriber_public_key = asymmetric_keys_sub[1]

            asymmetric_pub = KeyManagerGKMP.__generate_asymmetric_keys()
            group_gkmp_map.publisher_private_key = asymmetric_pub[0]
            group_gkmp_map.publisher_public_key = asymmetric_pub[1]

        elif group.type_of_pub_sub_group == TypeOfPubSubGroupEnum.MANY_PUB_1_SUB.value:
            group_gkmp_map.common_key = KeyManagerGKMP.__generate_symmetric_key()

            asymmetric_keys = KeyManagerGKMP.__generate_asymmetric_keys()
            group_gkmp_map.subscriber_private_key = asymmetric_keys[0]
            group_gkmp_map.subscriber_public_key = asymmetric_keys[1]

        elif group.type_of_pub_sub_group == TypeOfPubSubGroupEnum.MANY_SUB_1_PUB.value:
            group_gkmp_map.common_key = KeyManagerGKMP.__generate_symmetric_key()

            asymmetric_keys = KeyManagerGKMP.__generate_asymmetric_keys()
            group_gkmp_map.publisher_private_key = asymmetric_keys[0]
            group_gkmp_map.publisher_public_key = asymmetric_keys[1]

        else:
            pass  # return error
        KeyManagerGKMP.group_gkmp_mapping_list.append(group_gkmp_map)

    @staticmethod
    def add_or_delete_participant(group, participant, participant_permission, add_participant=False,
                                  delete_participant=False):
        if add_participant is False and delete_participant is False:
            return "error"

        group_gkmp_map = [x for x in KeyManagerGKMP.group_gkmp_mapping_list if x.group.id == group.id][0]

        if group.type_of_pub_sub_group == TypeOfPubSubGroupEnum.ALL_PUBSUB.value:

            if delete_participant is True:
                deleted_participant = [x for x in group_gkmp_map.publishers_and_subscribers if x.particpaint_id == participant.participant_id][0]
                group_gkmp_map.publishers_and_subscribers.remove(deleted_participant)

            group_gkmp_map.common_key = KeyManagerGKMP.__generate_symmetric_key()
            changed_keys_participants = {'group_common_key': group_gkmp_map.common_key,
                                         'participant_list': group_gkmp_map.publishers_and_subscribers}

            KeyManagerGKMP.__send_messages(changed_keys_participants, group.group_name)

            if add_participant is True:
                group_gkmp_map.publishers_and_subscribers.append(participant)

        elif group.type_of_pub_sub_group == TypeOfPubSubGroupEnum.SOME_PUBSUB_SOME_PUB.value:
            # publishers - commonkey and sub public key

            group_gkmp_map.common_key = KeyManagerGKMP.__generate_symmetric_key()

            asymmetric_keys = KeyManagerGKMP.__generate_asymmetric_keys()
            group_gkmp_map.subscriber_private_key = asymmetric_keys[0]
            group_gkmp_map.subscriber_public_key = asymmetric_keys[1]

            if delete_participant is True:
                if participant_permission is PermissionTypesEnum.PUBLISH.value:
                    deleted_participant = [x for x in group_gkmp_map.publishers if
                                           x.participant_id == participant.participant_id][0]
                    group_gkmp_map.publishers.remove(deleted_participant)

                elif participant_permission is PermissionTypesEnum.PUBLISH_AND_SUBSCRIBE.value:
                    deleted_participant = [x for x in group_gkmp_map.publishers_and_subscribers if
                                           x.participant_id == participant.participant_id][0]
                    group_gkmp_map.publishers_and_subscribers.remove(deleted_participant)

                else:
                    return "error wrong permission"
            # for publishers
            changed_keys_participants = {'group_common_key': group_gkmp_map.common_key,
                                         'subscriber_public_key' : group_gkmp_map.subscriber_public_key,
                                         'participant_list': group_gkmp_map.publishers}
            KeyManagerGKMP.__send_messages(changed_keys_participants, group.group_name)
            # for publishers and subscribers
            changed_keys_participants = {'group_common_key': group_gkmp_map.common_key,
                                         'subscriber_public_key': group_gkmp_map.subscriber_public_key,
                                         'subscriber_private_key': group_gkmp_map.subscriber_private_key,
                                         'participant_list': group_gkmp_map.publishers_and_subscribers}
            KeyManagerGKMP.__send_messages(changed_keys_participants, group.group_name)

            if add_participant is True:
                if participant_permission is PermissionTypesEnum.PUBLISH.value:
                    group_gkmp_map.publishers.append(participant)
                elif participant_permission is PermissionTypesEnum.PUBLISH_AND_SUBSCRIBE.value:
                    group_gkmp_map.publishers_and_subscribers.append(participant)
                else:
                    return "error wrong permission"

        elif group.type_of_pub_sub_group == TypeOfPubSubGroupEnum.SOME_PUBSUB_SOME_SUB.value:
            group_gkmp_map.common_key = KeyManagerGKMP.__generate_symmetric_key()

            asymmetric_keys = KeyManagerGKMP.__generate_asymmetric_keys()
            group_gkmp_map.publisher_private_key = asymmetric_keys[0]
            group_gkmp_map.publisher_public_key = asymmetric_keys[1]

            if delete_participant is True:
                if participant_permission is PermissionTypesEnum.SUBSCRIBE.value:
                    deleted_participant = [x for x in group_gkmp_map.subscribers if
                                           x.participant_id == participant.participant_id][0]
                    group_gkmp_map.subscribers.remove(deleted_participant)

                elif participant_permission is PermissionTypesEnum.PUBLISH_AND_SUBSCRIBE.value:
                    deleted_participant = [x for x in group_gkmp_map.publishers_and_subscribers if
                                           x.participant_id == participant.participant_id][0]
                    group_gkmp_map.publishers_and_subscribers.remove(deleted_participant)

                else:
                    return "error wrong permission"

            changed_keys_participants = {'group_common_key': group_gkmp_map.common_key,
                                         'publisher_public_key': group_gkmp_map.publisher_public_key,
                                         'participant_list': group_gkmp_map.subscribers}
            KeyManagerGKMP.__send_messages(changed_keys_participants, group.group_name)
            # for publishers and subscribers
            changed_keys_participants = {'group_common_key': group_gkmp_map.common_key,
                                         'publisher_public_key': group_gkmp_map.publisher_public_key,
                                         'publisher_private_key': group_gkmp_map.publisher_private_key,
                                         'participant_list': group_gkmp_map.publishers_and_subscribers}
            KeyManagerGKMP.__send_messages(changed_keys_participants, group.group_name)

            if add_participant is True:
                if participant_permission is PermissionTypesEnum.SUBSCRIBE.value:
                    group_gkmp_map.subscribers.append(participant)
                elif participant_permission is PermissionTypesEnum.PUBLISH_AND_SUBSCRIBE.value:
                    group_gkmp_map.publishers_and_subscribers.append(participant)
                else:
                    return "error wrong permission"

        elif group.type_of_pub_sub_group == TypeOfPubSubGroupEnum.SOME_PUB_SOME_SUB.value:
            # publishers 3 keys, subscribers 3 keys
            asymmetric_keys_sub = KeyManagerGKMP.__generate_asymmetric_keys()
            group_gkmp_map.subscriber_private_key = asymmetric_keys_sub[0]
            group_gkmp_map.subscriber_public_key = asymmetric_keys_sub[1]

            asymmetric_pub = KeyManagerGKMP.__generate_asymmetric_keys()
            group_gkmp_map.publisher_private_key = asymmetric_pub[0]
            group_gkmp_map.publisher_public_key = asymmetric_pub[1]

            if delete_participant is True:
                if participant_permission is PermissionTypesEnum.SUBSCRIBE.value:
                    deleted_participant = [x for x in group_gkmp_map.subscribers if
                                           x.participant_id == participant.participant_id][0]
                    group_gkmp_map.subscribers.remove(deleted_participant)

                elif participant_permission is PermissionTypesEnum.PUBLISH.value:
                    deleted_participant = [x for x in group_gkmp_map.publishers if
                                           x.participant_id == participant.participant_id][0]
                    group_gkmp_map.publishers.remove(deleted_participant)

                else:
                    return "error wrong permission"

            changed_keys_participants = {'publisher_private_key': group_gkmp_map.publisher_private_key,
                                         'publisher_public_key': group_gkmp_map.publisher_public_key,
                                         'subscriber_public_key': group_gkmp_map.subscriber_public_key,
                                         'participant_list': group_gkmp_map.publishers}
            KeyManagerGKMP.__send_messages(changed_keys_participants, group.group_name)
            # for publishers and subscribers
            changed_keys_participants = {'subscriber_public_key': group_gkmp_map.subscriber_public_key,
                                         'subscriber_private_key': group_gkmp_map.subscriber_private_key,
                                         'publisher_public_key': group_gkmp_map.publisher_public_key,
                                         'participant_list': group_gkmp_map.subscribers}
            KeyManagerGKMP.__send_messages(changed_keys_participants, group.group_name)

            if add_participant is True:
                if participant_permission is PermissionTypesEnum.SUBSCRIBE.value:
                    group_gkmp_map.subscribers.append(participant)
                elif participant_permission is PermissionTypesEnum.PUBLISH.value:
                    group_gkmp_map.publishers.append(participant)
                else:
                    return "error wrong permission"

        elif group.type_of_pub_sub_group == TypeOfPubSubGroupEnum.SOME_PUBSUB_SOME_PUB_SOME_SUB.value:

            if delete_participant is True:
                if participant_permission is PermissionTypesEnum.SUBSCRIBE.value:
                    deleted_participant = [x for x in group_gkmp_map.subscribers if
                                           x.participant_id == participant.participant_id][0]
                    group_gkmp_map.subscribers.remove(deleted_participant)

                elif participant_permission is PermissionTypesEnum.PUBLISH.value:
                    deleted_participant = [x for x in group_gkmp_map.publishers if
                                           x.participant_id == participant.participant_id][0]
                    group_gkmp_map.publishers.remove(deleted_participant)

                elif participant_permission is PermissionTypesEnum.PUBLISH_AND_SUBSCRIBE.value:
                    deleted_participant = [x for x in group_gkmp_map.publishers_and_subscribers if
                                           x.participant_id == participant.participant_id][0]
                    group_gkmp_map.publishers_and_subscribers.remove(deleted_participant)

                else:
                    return "error wrong permission"

            asymmetric_keys_sub = KeyManagerGKMP.__generate_asymmetric_keys()
            group_gkmp_map.subscriber_private_key = asymmetric_keys_sub[0]
            group_gkmp_map.subscriber_public_key = asymmetric_keys_sub[1]

            asymmetric_pub = KeyManagerGKMP.__generate_asymmetric_keys()
            group_gkmp_map.publisher_private_key = asymmetric_pub[0]
            group_gkmp_map.publisher_public_key = asymmetric_pub[1]

            changed_keys_participants = {'publisher_private_key': group_gkmp_map.publisher_private_key,
                                         'publisher_public_key': group_gkmp_map.publisher_public_key,
                                         'subscriber_public_key': group_gkmp_map.subscriber_public_key,
                                         'participant_list': group_gkmp_map.publishers}
            KeyManagerGKMP.__send_messages(changed_keys_participants, group.group_name)

            changed_keys_participants = {'subscriber_public_key': group_gkmp_map.subscriber_public_key,
                                         'subscriber_private_key': group_gkmp_map.subscriber_private_key,
                                         'publisher_public_key': group_gkmp_map.publisher_public_key,
                                         'participant_list': group_gkmp_map.subscribers}
            KeyManagerGKMP.__send_messages(changed_keys_participants, group.group_name)

            changed_keys_participants = {'subscriber_public_key': group_gkmp_map.subscriber_public_key,
                                         'subscriber_private_key': group_gkmp_map.subscriber_private_key,
                                         'publisher_public_key': group_gkmp_map.publisher_public_key,
                                         'publisher_private_key': group_gkmp_map.publisher_private_key,
                                         'participant_list': group_gkmp_map.publishers_and_subscribers}
            KeyManagerGKMP.__send_messages(changed_keys_participants, group.group_name)

            if add_participant is True:
                if participant_permission is PermissionTypesEnum.SUBSCRIBE.value:
                    group_gkmp_map.subscribers.append(participant)
                elif participant_permission is PermissionTypesEnum.PUBLISH.value:
                    group_gkmp_map.publishers.append(participant)
                elif participant_permission is PermissionTypesEnum.PUBLISH_AND_SUBSCRIBE.value:
                    group_gkmp_map.publishers_and_subscribers.append(participant)
                else:
                    return "error wrong permission"


        # handle edge cases
        elif group.type_of_pub_sub_group == TypeOfPubSubGroupEnum.MANY_PUB_1_SUB.value:
            group_gkmp_map.common_key = KeyManagerGKMP.__generate_symmetric_key()

            asymmetric_keys = KeyManagerGKMP.__generate_asymmetric_keys()
            group_gkmp_map.subscriber_private_key = asymmetric_keys[0]
            group_gkmp_map.subscriber_public_key = asymmetric_keys[1]

        elif group.type_of_pub_sub_group == TypeOfPubSubGroupEnum.MANY_SUB_1_PUB.value:
            group_gkmp_map.common_key = KeyManagerGKMP.__generate_symmetric_key()

            asymmetric_keys = KeyManagerGKMP.__generate_asymmetric_keys()
            group_gkmp_map.publisher_private_key = asymmetric_keys[0]
            group_gkmp_map.publisher_public_key = asymmetric_keys[1]

        else:
            pass  # return error



    @staticmethod
    def __generate_symmetric_key():
        return nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE)

    @staticmethod
    def __generate_asymmetric_keys():
        private_key = PrivateKey.generate()
        public_key = private_key.public_key
        return private_key, public_key

    @staticmethod
    def __send_messages(changed_keys_participants, group_name):
        messages = list()
        changed_keys = dict()
        for key, value in changed_keys_participants.items():
            if key is not 'participant_list':
                changed_keys[key] = value

        for participant in changed_keys_participants['participant_list']:
            message_detail = {"message_name": group_name + "/gkmp change"+"/" + participant.participant_id,
                              "encryption_key": participant.pairwise_key,
                              "changed_parent_key": changed_keys}
            messages.append(message_detail)
        return messages


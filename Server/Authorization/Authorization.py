from Server.CustomClasses.Group import Group
from Server.CustomClasses.CustomEnums import TypeOfPubSubGroupEnum, KeyManagementProtocols
from Server.KeyManager.KeyManagerGKMP import KeyManagerGKMP
from Server.KeyManager.PubSubKeyManagerTreeType import KeyManager
import random


class Authorization:
    groups = list()

    @staticmethod
    def create_group(group_name, group_id, type_of_key_management_protocol,
                     type_of_pub_sub_group=TypeOfPubSubGroupEnum.ALL_PUBSUB):
        group = Group(group_name, group_id, type_of_pub_sub_group, type_of_key_management_protocol)
        Authorization.groups.append(group)
        if type_of_key_management_protocol is KeyManagementProtocols.GKMP.value:
            KeyManagerGKMP.set_up_gkmp_group(group)
        if type_of_key_management_protocol is KeyManagementProtocols.LKH.value:
            KeyManager.setup_group_trees(group)
        return group

    @staticmethod
    def authorization_permissions(participant, group_id):
        group = [x for x in KeyManagerGKMP.group_gkmp_mapping_list if x.group.id == group_id][0]
        permission = 3
        if group.type_of_pub_sub_group is TypeOfPubSubGroupEnum.SOME_PUBSUB_SOME_PUB_SOME_SUB:
            permission = random.randint(1, 3)
        return permission, participant
        pass
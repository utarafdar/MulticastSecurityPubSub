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
        # print(group.group_name)
        if type_of_key_management_protocol is KeyManagementProtocols.GKMP.value:
            KeyManagerGKMP.set_up_gkmp_group(group)
        if type_of_key_management_protocol is KeyManagementProtocols.LKH.value:
            KeyManager.setup_group_trees(group)

        Authorization.groups.append(group)
        return group

    @staticmethod
    def authorization_permissions(participant, group_id, permission):
        group = [x for x in Authorization.groups if x.id == group_id][0]
        # check if permissions possible, auth infrastructure
        return True, participant, group

    @staticmethod
    def initializer():
        from Server.CustomClasses.Topic import Topic
        topic = Topic("test123456789")
        topic2 = Topic("test6789")
        group1 = Authorization.create_group("testGroup", "123", type_of_key_management_protocol=2,
                                           type_of_pub_sub_group=4)
        group1.add_topic(topic)
        group1.add_topic(topic2)
        return group1



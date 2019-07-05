from Server.Authorization.Authorization import Authorization
from Server.CustomClasses.Topic import Topic
from Server.GroupController.GroupController import DataSA
from Server.CustomClasses.CustomEnums import TypeOfPubSubGroupEnum, KeyManagementProtocols
import Server.CustomClasses.cryptography as crypto
import nacl.secret
import nacl.utils
import nacl.encoding
import nacl.signing



class Initializer:
    @staticmethod
    def initialize_groups():
        topic = Topic("test123456789")
        topic2 = Topic("test12345")

        # testing initialising all possible types of groups
        for type_of_group in TypeOfPubSubGroupEnum:
            for type_of_key_management in KeyManagementProtocols:
                group_name = type_of_group.name + "_" + type_of_key_management.name
                topic_name = "topic_" + type_of_group.name + "_" + type_of_key_management.name
                group = Authorization.create_group(group_name, group_name, type_of_key_management.value,
                                                   type_of_pub_sub_group=type_of_group.value)
                topic = Topic(topic_name)
                group.add_topic(topic)
                print(group_name)

        '''group = Authorization.create_group("testGroup", "123", type_of_key_management_protocol=2, type_of_pub_sub_group=4)
        print(group)
        group.add_topic(topic)
        group.add_topic(topic2)'''

        # generate public and private key for gcks

        signing_key = nacl.signing.SigningKey.generate()
        verify_key = signing_key.verify_key

        # Serialize the verify key to send it to a third party
        verify_key_hex = verify_key.encode(encoder=nacl.encoding.HexEncoder)

        # set datasa global variable
        DataSA.set_gcks_signing_key(signing_key)
        DataSA.set_gcks_verify_key(verify_key_hex)

        while True:
            pass
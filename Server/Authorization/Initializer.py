from Server.Authorization.Authorization import Authorization
from Server.CustomClasses.Topic import Topic
from Server.GroupController.GroupController import DataSA
import Server.CustomClasses.cryptography as crypto
import nacl.secret
import nacl.utils
import nacl.encoding
import nacl.signing



class Initializer:
    @staticmethod
    def initialize_groups():
        topic = Topic("test")
        topic2 = Topic("test")
        group = Authorization.create_group("testGroup", "123", type_of_key_management_protocol=2, type_of_pub_sub_group=4)
        print(group)
        group.add_topic(topic)
        group.add_topic(topic2)

        # generate public and private key for gcks

        signing_key = nacl.signing.SigningKey.generate()
        verify_key = signing_key.verify_key

        # Serialize the verify key to send it to a third party
        verify_key_hex = verify_key.encode(encoder=nacl.encoding.HexEncoder)

        # set datasa global variable
        DataSA.set_gcks_signing_key(signing_key)
        DataSA.set_gcks_verify_key(verify_key_hex)
        print("verify key hex")
        print(verify_key_hex)

        while True:
            pass
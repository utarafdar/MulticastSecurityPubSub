# import socket programming library
import socket
from Server.Authorization.Authorization import Authorization
from Server.CustomClasses.Topic import Topic
from Server.GroupController.GroupController import GroupController
from Server.CustomClasses.Participant import Participant

# import thread module
from _thread import *
import threading
import pickle
import nacl.utils
import nacl.secret
import json
import uuid
import jsonpickle
from nacl.encoding import HexEncoder

print_lock = threading.Lock()

def generate_key():
    return nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE)


# thread fuction
def threaded(conn):
    while True:
        data = conn.recv(1024)
        if not data:
            break
        print(data.decode('utf-8'))
        # participant = pickle.loads(data)
        group_id = "123"
        # generate participant Id and pairwise key
        participant_id = str(uuid.uuid4())
        pairwise_key = generate_key()
        participant = Participant(pairwise_key, participant_id)

        results = Authorization.authorization_permissions(participant, group_id)
        permission = results[0]
        group = results[2]
        # cannot decide this here add lkh or gkmp-- todo
        data_sa = GroupController.add_participant_lkh(group, participant, permission)

        # send request to authentication
        # receive permissions group
        # send participant and permissions to add to group
        # receive data SA
        # send dataSA to the client

        # convert data sa to json
        # serialize it
        print("test")
        data = __convert_data_sa_to_json(data_sa)
        conn.sendall(json.dumps(data).encode())
        #conn.sendall(pickle.dumps(data_sa))
        # print_lock.release()
        conn.close()
        break

    # connection closed
def initializer():
    from Server.Authorization.Initializer import Initializer
    Initializer.initialize_groups()


def Main():
    host = '127.0.0.1'

    # reverse a port on your computer
    # in our case it is 12345 but it
    # can be anything
    port = 65432
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    print("socket binded to post", port)

    # put the socket into listening mode
    s.listen(5)
    print("socket is listening")
    # initialize
    start_new_thread(initializer, ())
    # a forever loop until client wants to exit
    while True:
        # establish connection with client
        c, addr = s.accept()

        # lock acquired by client

        # print_lock.acquire()
        print('Connected to :', addr[0], ':', addr[1])

        # Start a new thread and return its identifier
        start_new_thread(threaded, (c,))
    s.close()


def __convert_data_sa_to_json(data_sa):
    publisher_public_key = None
    subscriber_public_key = None
    publisher_private_key = None
    subscriber_private_key = None
    for key, value in data_sa.ancestor_keys[0]['key'].items():
        if key is 'publisher_public_key' and value is not None:
            publisher_public_key = value.encode(HexEncoder).decode()
        if key is 'subscriber_public_key' and value is not None:
            subscriber_public_key = value.encode(HexEncoder).decode()
        if key is 'publisher_private_key' and value is not None:
            publisher_private_key = value.encode(HexEncoder).decode()
        if key is 'subscriber_private_key' and value is not None:
            subscriber_private_key = value.encode(HexEncoder).decode()


    data_sa_json = {
                    'nonce_prefix': data_sa.nonce_prefix,
                    'permissions': data_sa.permissions,
                    'pairwise_key': data_sa.pairwise_key.hex(),
                    'ancestor_keys': data_sa.ancestor_keys[1:],
                    'group_keys': {'publisher_public_key': publisher_public_key,
                                   'subscriber_public_key': subscriber_public_key,
                                   'publisher_private_key': publisher_private_key,
                                   'subscriber_private_key': subscriber_private_key},
                    'rekey_topics': data_sa.rekey_topics_keys,
                    'subscriptions': data_sa.topics,
                    'group_id': data_sa.group_id,
                    'type_of_key_management': data_sa.key_management_type,
                    'change_tree_structure_topic': data_sa.change_tree_structure_topic,
                    'participant_id': data_sa.participant_id
    }
    return data_sa_json


if __name__ == '__main__':
    Main()


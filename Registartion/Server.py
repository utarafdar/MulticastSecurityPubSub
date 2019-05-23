import socket
from Participant import Participant
import pickle
import nacl.utils
import nacl.secret
# import thread module
from _thread import *
import threading


def generate_key():
    return nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE)


print_lock = threading.Lock()


def threaded(conn):
    while True:
        data = conn.recv(1024)
        if not data:
            break
    participant = pickle.loads(data)
    participant.pairwise_key = generate_key()
    conn.sendall(pickle.dumps(participant))
    print_lock.release()
    conn.close()


def Main():
    HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
    PORT = 65432        # Port to listen on (non-privileged ports are > 1023)

    while True:

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((HOST, PORT))
            s.listen()
            conn, addr = s.accept()
            print_lock.acquire()
            with conn:
                print('Connected by', addr)
                threaded(conn)

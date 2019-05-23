# import socket programming library
import socket

# import thread module
from _thread import *
import threading
import pickle
import nacl.utils
import nacl.secret

print_lock = threading.Lock()

def generate_key():
    return nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE)


# thread fuction
def threaded(conn):
    while True:
        data = conn.recv(1024)
        if not data:
            break
        participant = pickle.loads(data)
        participant.pairwise_key = generate_key()
        # send request to authentication
        # recieve permissions group
        # send participannt and permissions to add to group
        # recieve data SA
        # send dataSA to the client
        conn.sendall(pickle.dumps(participant))
        print_lock.release()
        conn.close()
        break

    # connection closed


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

    # a forever loop until client wants to exit
    while True:
        # establish connection with client
        c, addr = s.accept()

        # lock acquired by client
        print_lock.acquire()
        print('Connected to :', addr[0], ':', addr[1])

        # Start a new thread and return its identifier
        start_new_thread(threaded, (c,))
    s.close()


if __name__ == '__main__':
    Main()

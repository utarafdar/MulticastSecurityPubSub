import socket
from Participant import Participant
import pickle
from Server.GroupController.GroupController import GroupController

HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 65431        # The port used by the server

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    participant4 = Participant("12345", "004")
    s.sendall(pickle.dumps(participant4))
    data = b""
    while True:
        packet = s.recv(4096)
        if not packet: break
        data += packet

print('Received', pickle.loads(data).group_keys)
print('bye')
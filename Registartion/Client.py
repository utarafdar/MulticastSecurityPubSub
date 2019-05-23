import socket
from Participant import Participant
import pickle


HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 65432        # The port used by the server

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    participant4 = Participant("12345", "004")
    s.sendall(pickle.dumps(participant4))
    data = s.recv(1024)

print('Received', pickle.loads(data).pairwise_key)
import socket
from networking.settings import *

class Client:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self, ip, port):
        self.client.connect((ip, port))
        
    def disconnect(self):
        send(DISCONNECT_MESSAGE)
    
    def send(self, msg):
        message = msg.encode(FORMAT)
        msg_length = len(message)
        
        send_length = str(msg_length).encode(FORMAT)
        send_length += b" " * (HEADER - len(send_length))
        
        self.client.send(send_length)
        self.client.send(message)

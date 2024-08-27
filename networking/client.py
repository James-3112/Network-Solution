import socket
import logging
import networking.settings

class Client:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self, ip, port):
        try:
            self.client.connect((ip, port))
            logging.info(f"Connected to {(ip, port)}")
        except socket.error as e:
            logging.warning(f"Could not connect: {e}")
        
    def disconnect(self):
        self.send(DISCONNECT_MESSAGE)
        self.client.close()
    
    def send(self, msg):
        message = msg.encode(FORMAT)
        msg_length = len(message)
        
        send_length = str(msg_length).encode(FORMAT)
        send_length += b" " * (HEADER - len(send_length))
        
        self.client.send(send_length)
        self.client.send(message)

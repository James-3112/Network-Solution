import socket
import logging
from networking.settings import HEADER, FORMAT, DISCONNECT_MESSAGE

class Peer:
    def __init__(self, port):
        self.server = Server(port)
        self.client = Client()
        self.peers = {}

    def start(self):
        pass
    
    def stop(self):
        pass

    def connect_to_peer(self, ip, port):
        pass

    def send_message(self, message):
        pass

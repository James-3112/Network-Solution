import socket
import threading
import logging
from networking.settings import HEADER, FORMAT, DISCONNECT_MESSAGE

class Server:
    def __init__(self, port):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((socket.gethostbyname(socket.gethostname()), port))

    def start_thread(self):
        thread = threading.Thread(target=self.start)
        thread.start()
    
    def start(self):
        self.server.listen()
        logging.info("Server is listening")
        
        while True:
            connection, address = self.server.accept() # Blocking line (Code will wait here)
            thread = threading.Thread(target=self.handle_client, args=(connection, address))
            thread.start()
    
    def stop(self):
        self.server.close()
    
    def handle_client(self, connection, address):
        logging.info(f"{address} connected")
        
        while True:
            msg_length = connection.recv(HEADER).decode(FORMAT) # Blocking line (Code will wait here)
            
            if msg_length:
                msg_length = int(msg_length)
                msg = connection.recv(msg_length).decode(FORMAT) # Blocking line (Code will wait here)
            
                if msg == DISCONNECT_MESSAGE:
                    break
            
                print(f"[{address}] {msg}")
        
        logging.info(f"{address} disconnect")
        connection.close()

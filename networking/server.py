import socket
import threading
import logging
from networking.settings import HEADER, FORMAT, DISCONNECT_MESSAGE

class Server:
    clients = {}
    server_thread = None
    
    def __init__(self, port):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((socket.gethostbyname(socket.gethostname()), port))
    
    def start(self):
        server_thread = threading.Thread(target=self.start_thread)
        server_thread.start()
    
    def start_thread(self):
        self.running = True
        self.server.listen()
        logging.info("Server started")
        
        while self.running == True:
            try:
                connection, address = self.server.accept() # Blocking line
                self.clients[address] = connection
                
                logging.info(f"{address} connected")
                
                thread = threading.Thread(target=self.handle_client, args=(connection, address))
                thread.start()
            except socket.error as e:
                logging.error(f"Error client connecting: {e}")
    
    def stop(self):
        self.running = False
        self.server.close()
        
        for address, connection in self.clients.items():
            connection.close()
        self.clients.clear()
        
        if self.server_thread is not None:
            self.server_thread.join()
        
        logging.info("Server stopped")
    
    def handle_client(self, connection, address):
        while True:
            try:
                msg_length = connection.recv(HEADER).decode(FORMAT) # Blocking line
                
                if msg_length:
                    msg_length = int(msg_length)
                    msg = connection.recv(msg_length).decode(FORMAT) # Blocking line
                
                    if msg == DISCONNECT_MESSAGE:
                        break
                
                    logging.info(f"[{address}] {msg}")
            except socket.error as e:
                logging.error(f"Error handling client {address}: {e}")
        
        logging.info(f"{address} disconnect")
        self.disconnect_client(address)
        
    def disconnect_client(self, address):
        if address in self.clients:
            self.clients[address].close()
            self.clients.pop(address)
            
            logging.info(f"Disconnected client {address}")
        else: logging.info(f"Client {address} does not exist")

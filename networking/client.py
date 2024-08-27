import socket
import logging
from time import sleep
from networking.settings import DISCONNECT_MESSAGE

class Client:
    connected = False
    receiving_thread = None
    
    def __init__(self, header=64, encoding_format="utf-8", time_out=5):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.settimeout(_time_out)
        
        self.header = _header
        self.encoding_format = encoding_format

    def connect(self, ip, port, reconnect_attempts=3, reconnect_delay=5):
        attempts = 0
        while attempts < reconnect_attempts:
            try:
                self.client.connect((ip, port))
                self.connected = True
                
                logging.info(f"Connected to {(ip, port)}")
                
                # Start receiving thread
                self.receiving_thread = threading.Thread(target=self.receive_messages)
                self.receiving_thread.start()
                
                return True
            except socket.error as e:
                logging.warning(f"Failed to connect: {e}. Retrying in {reconnect_delay} seconds")
                attempts += 1
                
                sleep(reconnect_delay)
                
        logging.error("Failed to connect after {reconnect_attempts} attempts")
        return False
    
    def attempt_reconnect(self):
        logging.info("Attempting to reconnect...")
        
        if not self.connect(self.client.getpeername()[0], self.client.getpeername()[1]):
            logging.error("Reconnection failed. Closing client")
            self.disconnect()
    
    def disconnect(self):
        if self.connected:
            self.send(DISCONNECT_MESSAGE)
            
        if self.receiving_thread is not None:
            self.receiving_thread.join()
            
        self.client.close()
        self.connected = False
        logging.info("Client disconnect")
    
    def send(self, msg):
        if self.connected:
            try:
                message = msg.encode(self.encoding_format)
                msg_length = len(message)
                
                send_length = str(msg_length).encode(self.encoding_format)
                send_length += b" " * (self.header - len(send_length))
                
                self.client.send(send_length)
                self.client.send(message)
            except socket.error as e:
                logging.error(f"Error sending message: {e}")
        
    def receive_messages(self):
        while self.connected:
            try:
                msg_length = self.client.recv(self.header).decode(self.format)  # Blocking line
                
                if msg_length:
                    msg_length = int(msg_length)
                    msg = self.client.recv(msg_length).decode(self.format)  # Blocking line
                    
                    if msg == DISCONNECT_MESSAGE:
                        logging.info("Server requested disconnection")
                        self.disconnect()
                        break
                    
                    logging.info(f"Received: {msg}")
            except socket.timeout:
                logging.warning("Connection timed out")
                
                self.connected = False
                self.attempt_reconnect()
            except socket.error as e:
                logging.error(f"Error receiving message: {e}")
                
                self.connected = False
                self.attempt_reconnect()

import socket
import threading
import logging

class Client:
    is_connected = False
    receiving_thread = None
    
    
    def __init__(self, header_size=64, buffer_size=16, encoding_format="utf-8"):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        self.header_size = header_size
        self.buffer_size = buffer_size
        self.encoding_format = encoding_format


    # Connect client to the server
    def connect(self, ip, port):
        try:
            self.client.connect((ip, port))
            self.is_connected = True
            
            logging.info(f"Client connected to {(ip, port)}")
            
            # Start receiving thread
            self.receiving_thread = threading.Thread(target=self.receive_messages)
            self.receiving_thread.start()
        except Exception as e:
            logging.error(f"Error connecting to ({ip}, {port}): {e}")
    
    
    # Disconnect client from the server
    def disconnect(self):
        if self.is_connected == True:
            try:
                self.is_connected = False
                self.receiving_thread.join()
                    
                self.client.shutdown(socket.SHUT_RDWR)
                self.client.close()
                
                logging.info("Client disconnect")
            except Exception as e:
                logging.error(f"Error disconnecting client: {e}")
        else:
            logging.warning("Client is not connected")
    
    
    # Send message to server
    def send(self, message):
        # If client is connected
        if self.is_connected == True:
            try: # Try to send message
                message_header = f"{len(message):<{self.header_size}}" + message
                self.client.send(bytes(message_header, self.encoding_format))
                
                logging.info(f"Client sent message: {message}")
            except Exception as e:
                logging.error(f"Error sending message: {e}")
        else:
            logging.warning("Client is not connected")
    
    
    # Receiving messages from the server
    def receive_messages(self):
        full_message = ""
        new_message = True
        
        # While client is connected receive messages
        while self.is_connected == True:
            # Add the received message to the full message
            message = self.client.recv(self.buffer_size)
            full_message += message.decode(self.encoding_format)
            
            # If it is a new message calculate message length
            if new_message == True:
                message_length = int(message[:self.header_size])
                new_message = False
            
            # If the client has received the full message
            if len(full_message) - self.header_size == message_length:
                logging.info(f"Message received: {full_message[self.header_size:]}")
                
                new_message = True
                full_message = ""

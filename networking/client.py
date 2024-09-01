import socket
import threading
import logging

class Client:
    receiving_thread = None
    
    
    def __init__(self, header_size=10, buffer_size=16, encoding_format="utf-8"):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        self.header_size = header_size
        self.buffer_size = buffer_size
        self.encoding_format = encoding_format
        
        self.logger = logging.getLogger(__name__)
        self.logger.set_class_name(self.__class__.__name__)


    # Connect client to the server
    def connect(self, ip, port):
        try:
            self.client.connect((ip, port))
            self.logger.info(f"Connected to {(ip, port)}")
            
            # Start receiving thread
            self.receiving_thread = threading.Thread(target=self.receive_messages)
            self.receiving_thread.start()
        except Exception as e:
            self.logger.error(f"Error connecting to ({ip}, {port}): {e}")

    
    # Disconnect client from the server
    def disconnect(self):
        if self.is_connected() == True:
            try:    
                self.client.close()
                self.receiving_thread.join() 
            except Exception as e:
                self.logger.error(f"Error disconnecting: {e}")
        else:
            self.logger.warning("Attempted to disconnect when not connected")


    # Send message to server
    def send(self, message):
        # If client is connected
        if self.is_connected() == True:
            try: # Try to send message
                message_header = f"{len(message):<{self.header_size}}" + message
                self.client.send(bytes(message_header, self.encoding_format))
                
                self.logger.info(f"Sent message: {message}")
            except Exception as e:
                self.logger.error(f"Error sending message: {e}")
        else:
            self.logger.warning("Attempted to send a message when not connected")
    
    
    # Receiving messages from the server
    def receive_messages(self):
        full_message = ""
        new_message = True
        
        # While client is connected receive messages
        while self.is_connected() == True:
            try:
                # Add the received message to the full message
                message = self.client.recv(self.buffer_size)
                full_message += message.decode(self.encoding_format)
                
                # If it is a new message calculate message length
                if new_message == True:
                    try:
                        message_length = int(message[:self.header_size])
                        new_message = False
                    except:
                        self.logger.error(f"Invalid header received: {full_message[:self.header_size]}")
                        
                        new_message = True
                        full_message = ""
                        
                        continue
                
                # If the client has received the full message
                if len(full_message) - self.header_size == message_length:
                    self.logger.info(f"Received message: {full_message[self.header_size:]}")
                    
                    new_message = True
                    full_message = ""
                    
            # The client has disconnected
            except ConnectionResetError:
                self.logger.info("Disconnect")
                break
            except Exception as e:
                self.logger.error(f"Error when receiving message: {e}")
                break
    
    
    # Checks if the client is still connected 
    def is_connected(self):
        try:
            self.client.send(b"")
            return True
        except:
            return False

import socket
import threading
import logging

from multipledispatch import dispatch


class Server:
    is_running = False
    server_thread = None
    clients = {}
    
    
    def __init__(self, port, header_size=10, buffer_size=16, encoding_format="utf-8", max_clients=10):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((socket.gethostbyname(socket.gethostname()), port))
        
        self.header_size = header_size
        self.buffer_size = buffer_size
        self.encoding_format = encoding_format
        self.max_clients = max_clients
        
        self.logger = logging.getLogger(__name__)
        self.logger.set_class_name(self.__class__.__name__)
    
    
    # Starts the server thread
    def start(self):
        self.server_thread = threading.Thread(target=self.start_server_thread)
        self.server_thread.start()
    
    # Starts listening for clients
    def start_server_thread(self):
        self.is_running = True
        self.logger.info("Started")
        
        # Starts the server listening for clients
        self.server.listen()
        
        # While the server is running accept connections
        while self.is_running == True:
            try:
                # When the server accepts a connection
                connection, address = self.server.accept()
                
                # Starts a thread for that client
                thread = threading.Thread(target=self.receive_messages, args=(connection, address))
                thread.start()
                
                # Add the client to the dictionary
                self.clients[address] = {
                    "connection": connection,
                    "thread": thread
                }
                
                self.logger.info(f"{address} connected")
            except OSError:
                self.logger.info("Stoped")
            except Exception as e:
                self.logger.error(f"Error when accepting connection: {e}")
    
    
    # Stops the server
    def stop(self):
        if self.is_running == True:
            try:
                self.is_running = False
                        
                for client in self.clients:
                    self.disconnect(self.clients[client])
                
                self.server.close()
                self.server_thread.join()
            except socket.error as e:
                self.logger.error(f"Error stoping: {e}")
        else:
            self.logger.warning("Attempted to stop when not running")
    

    # Disconnecting clients
    @dispatch(dict)
    def disconnect(self, client):
        if self.is_running == True:
            try:
                self.clients.pop(client["connection"].getpeername())
                client["connection"].close()
                client["thread"].join()
            except socket.error as e:
                self.logger.error(f"Error disconnecting {client['connection'].getpeername()}: {e}")
        else:
            self.logger.warning("Attempted to disconnect when not running")

    @dispatch(tuple)
    def disconnect(self, address):
        self.disconnect(self.clients[address])
    
    
    # Sending messages
    @dispatch(socket.socket, str)
    def send(self, connection, message):
        if self.is_running == True:
            try:
                message_header = f"{len(message):<{self.header_size}}" + message
                connection.send(bytes(message_header, self.encoding_format))
                
                self.logger.info(f"Sent message: {message}")
            except socket.error as e:
                self.logger.error(f"Error sending message: {e}")
        else:
            self.logger.warning("Attempted to send a message when not running")
    
    @dispatch(tuple, str)
    def send(self, address, message):
        self.send(self.clients[address]["connection"], message)
    
    
    # Receive messages from clients
    def receive_messages(self, connection, address):
        full_message = ""
        new_message = True
        
        # While server is running receive messages
        try:
            while self.is_running == True:
                # Add the received message to the full message
                message = connection.recv(self.buffer_size)
                full_message += message.decode(self.encoding_format)
                
                # If it is a new message calculate message length
                if new_message == True:
                    message_length = int(message[:self.header_size])
                    new_message = False
                
                # If the server has received the full message
                if len(full_message) - self.header_size == message_length: 
                    self.logger.info(f"Received message from {address}: {full_message[self.header_size:]}")
                    
                    new_message = True
                    full_message = ""
        except ConnectionResetError:
            self.logger.info(f"{address} has disconnected from the server")
        except ConnectionAbortedError:
            self.logger.info(f"Disconnected: {address}")

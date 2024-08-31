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
    
    
    # Starts the server thread
    def start(self):
        self.server_thread = threading.Thread(target=self.start_server_thread)
        self.server_thread.start()
    
    # Starts listening for clients
    def start_server_thread(self):
        self.is_running = True
        logging.info("Server started")
        
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
                
                logging.info(f"{address} connected to server")
            except OSError:
                logging.info("Server stoped")
            except Exception as e:
                logging.error(f"Server error when accepting connection: {e}")
    
    
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
                logging.error(f"Error stoping server: {e}")
        else:
            logging.warning("Server is not running")
    

    # Disconnecting clients
    @dispatch(dict)
    def disconnect(self, client):
        if self.is_running == True:
            try:
                self.clients.pop(client["connection"].getpeername())
                client["connection"].close()
                client["thread"].join()
            except socket.error as e:
                logging.error(f"Error disconnecting client {client['connection'].getpeername()}: {e}")
        else:
            logging.warning("Server is not running")

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
                
                logging.info(f"Server sent message: {message}")
            except socket.error as e:
                logging.error(f"Error sending message: {e}")
        else:
            logging.warning("Server is not running")
    
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
                    logging.info(f"Server received message from {address}: {full_message[self.header_size:]}")
                    
                    new_message = True
                    full_message = ""
        except ConnectionResetError:
            logging.info(f"Client {address} has disconnected from the server")
        except ConnectionAbortedError:
            logging.info(f"Server disconnected client: {address}")

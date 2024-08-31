import socket
import threading
import logging

from networking.server import Server
from time import sleep


class Peer(Server):
    is_running = False
    
    announcing_thread = None
    listening_thread = None
    
    def __init__(self, port, discovery_port, header_size=10, buffer_size=16, encoding_format="utf-8", max_peers=10, announce_time=5):
        super().__init__(port, header_size, buffer_size, encoding_format, max_peers)
        self.discovery_port = discovery_port
        self.announce_time = announce_time
        
        # Create a UDP socket for broadcasting
        self.discovery_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.discovery_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.discovery_socket.bind(("", self.discovery_port))
    
    
    # Sends a message to all connected peers
    def broadcast(self, message):
        for client in self.clients:
            self.send(self.clients[client]["connection"], message)
    
    
    # Receive messages from peers
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
                    
                    # Broadcast the message to the rest of the clients
                    self.broadcast_message(full_message[self.header_size:])
                    
                    new_message = True
                    full_message = ""
        except ConnectionResetError:
            logging.info(f"Client {address} has disconnected from the server")
        except ConnectionAbortedError:
            logging.info(f"Server disconnected client: {address}")

    
    def connect(self, address):
        try:    
            peer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            peer.connect((ip, port))
            
            logging.info(f"Client connected to {(ip, port)}")
            
            # Start receiving thread
            self.receiving_thread = threading.Thread(target=self.receive_messages)
            self.receiving_thread.start()
        except Exception as e:
            logging.error(f"Error connecting to ({ip}, {port}): {e}")

    
    def start_discovery(self):
        # Announcing presence to the network
        self.announcing_thread = threading.Thread(target=self.announce_presence)
        self.announcing_thread.start()
        
        # Start listening for discovery messages
        self.listening_thread = threading.Thread(target=self.listen_for_peers)
        self.listening_thread.start()
    
    
    def announce_presence(self):
        try:
            while self.is_running == True:
                message = f"DISCOVER:{self.host}:{self.port}"
                self.discovery_socket.sendto(message.encode('utf-8'), ('<broadcast>', self.discovery_port))
                
                sleep(self.announce_time)
        except Exception as e:
            logging.error(f"Peer error announcing presence: {e}")


    def listen_for_peers(self):
        try:
            while self.running:
                data, address = self.discovery_socket.recvfrom(1024)
                message = data.decode('utf-8')
                
                if message.startswith("DISCOVER"):
                    peer_host, peer_port = message.split(":")[1], int(message.split(":")[2])
                    
                    if (peer_host, peer_port) != (self.host, self.port):
                        print(f"Discovered peer at {peer_host}:{peer_port}")
                        self.connect_to_peer(peer_host, peer_port)
        except Exception as e:
            logging.error(f"Peer error listening for peers: {e}")


    def stop(self):
        if self.is_running == True:
            try:
                self.is_running = False
                        
                for client in self.clients:
                    self.disconnect(self.clients[client])
                
                self.server.close()
                self.server_thread.join()
                
                self.discovery_socket.close()
                self.announcing_thread.join()
                self.listening_thread.join()
            except socket.error as e:
                logging.error(f"Error stoping peer: {e}")
        else:
            logging.warning("Peer is not running")
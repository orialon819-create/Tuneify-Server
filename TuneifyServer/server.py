"""
server.py

This is the main server module. It initializes the DatabaseManager,
creates Service objects, sets up the Dispatcher, and listens for client
connections. Each client is handled in a separate ClientHandler thread.
"""

import socket
import threading
from client_handler import ClientHandler
from dispatcher import Dispatcher
from database_manager import DatabaseManager
from Services.user_service import UserService
from Services.song_service import SongService
from Services.playlist_service import PlaylistService


# Server configuration
HOST = "0.0.0.0"
PORT = 5000


# INITIALIZATION

# Creates the database connection (single source of truth)
# Input: database file path (str)
# Output: DatabaseManager object
db = DatabaseManager("tuneify.db")


# SERVICE LAYER

# Initializes business logic services (all depend on DB)
# Input: DatabaseManager
# Output: service objects
user_service = UserService(db)
song_service = SongService(db)
playlist_service = PlaylistService(db)


# DISPATCHER

# Central router that connects commands to services
# Input: service objects
# Output: Dispatcher object
dispatcher = Dispatcher(user_service, song_service, playlist_service)


# NETWORK SETUP

# Creates TCP socket for server
# Input: None
# Output: socket object
server_socket = socket.socket()

# Binds server to host and port
# Input: HOST (str), PORT (int)
# Output: None
server_socket.bind((HOST, PORT))

# Starts listening for incoming connections
# Input: None
# Output: None
server_socket.listen()

print(f"Server listening on {HOST}:{PORT}")


# MAIN SERVER LOOP

# Continuously accepts new client connections
# Input: None
# Output: client threads

while True:

    # Accept new client connection
    # Input: incoming TCP connection
    # Output: client_socket, address
    client_socket, address = server_socket.accept()

    print(f"New connection from {address}")

    # Creates handler for this specific client
    # Input: client socket, dispatcher
    # Output: ClientHandler instance
    handler = ClientHandler(client_socket, dispatcher)

    # Runs client handler in a separate thread
    # Input: handler.run function
    # Output: running thread
    thread = threading.Thread(target=handler.run)
    thread.start()
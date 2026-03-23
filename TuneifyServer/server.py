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

HOST = "0.0.0.0"
PORT = 5000

# 1. INITIALIZATION: Create the single source of truth for data
db = DatabaseManager("tuneify.db")

# 2. SERVICE LAYER: Instantiate specialized logic handlers, passing them the DB reference
user_service = UserService(db)
song_service = SongService(db)
playlist_service = PlaylistService(db)

# 3. ROUTING: Create the central Dispatcher that knows about all services
dispatcher = Dispatcher(user_service, song_service, playlist_service)

# 4. NETWORKING: Initialize the main listener socket
server_socket = socket.socket()
server_socket.bind((HOST, PORT))
server_socket.listen()
print(f"Server listening on {HOST}:{PORT}")

while True:
    client_socket, address = server_socket.accept()
    print(f"New connection from {address}")

    # Each new user gets their own dedicated ClientHandler instance
    handler = ClientHandler(client_socket, dispatcher)

    thread = threading.Thread(target=handler.run)
    thread.start()
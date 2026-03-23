# test_client.py
import socket

HOST = "127.0.0.1"
PORT = 5000

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

# --- Test REGISTER ---
client.sendall("REGISTER|Ori|Alon|ori@example.com|orialon|password123".encode())
response = client.recv(4096).decode()
print("REGISTER response:", response)

# --- Test LOGIN ---
client.sendall("LOGIN|orialon|password123".encode())
response = client.recv(4096).decode()
print("LOGIN response:", response)

# --- Test GET_USER ---
client.sendall("GET_USER|orialon".encode())
response = client.recv(4096).decode()
print("GET_USER response:", response)

# --- Test GET_ALL_SONGS ---
client.sendall("GET_ALL_SONGS".encode())
response = client.recv(4096).decode()
print("ALL_SONGS response:", response)

client.close()

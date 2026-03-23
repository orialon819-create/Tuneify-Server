import socket

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))  # Google's DNS, no data is actually sent
local_ip = s.getsockname()[0]
s.close()

SERVER_IP = str(local_ip)  # explicitly a string
STREAM_PORT = 8000


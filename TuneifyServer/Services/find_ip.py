# find_ip

import socket

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
local_ip = s.getsockname()[0]
s.close()

SERVER_IP = str(local_ip)
STREAM_PORT = 8000


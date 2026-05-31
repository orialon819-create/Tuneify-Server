# run_servers.py
"""
Responsible for launching and managing all backend services for Tuneify.
"""

import subprocess
import time
import sys

def start_servers():

    # Starts both backend servers and keeps them running
    # Input: None
    # Output: None (runs infinite loop until interrupted)

    print("Starting both socket and streaming servers")

    # 1. Start Socket Server (handles core system logic: users, songs, playlists)
    # This runs server.py as a separate process
    socket_proc = subprocess.Popen([sys.executable, "server.py"])
    print("Socket Server worked!")

    # 2. Start Streaming Server (FastAPI music streaming service)
    # This runs stream_server.py as a separate process
    stream_proc = subprocess.Popen([sys.executable, "stream_server.py"])
    print("Stream Server worked!")

    try:
        # Keeps main process alive while both servers run in background
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nShutting down...")

        socket_proc.terminate()
        stream_proc.terminate()


if __name__ == "__main__":
    start_servers()
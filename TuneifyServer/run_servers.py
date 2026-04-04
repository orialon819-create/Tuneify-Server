import subprocess
import time
import sys

def start_servers():
    print("Starting both socket and streaming servers")

    # 1. Start your Socket Server (Metadata, Login, Playlists)
    # This uses your existing server.py
    socket_proc = subprocess.Popen([sys.executable, "server.py"])
    print("Socket Server worked!")

    # 2. Start the FastAPI Server (Music Streaming)
    # This uses the new stream_server.py
    stream_proc = subprocess.Popen([sys.executable, "stream_server.py"])
    print("Stream Server worked!")


    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down...")
        socket_proc.terminate()
        stream_proc.terminate()

if __name__ == "__main__":
    start_servers()
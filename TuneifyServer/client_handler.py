"""
client_handler.py

Handles communication with a single client.
Each client runs in its own thread.
Receives messages, parses them using Protocol,
dispatches them using Dispatcher, and sends responses back.
"""

from protocol import Protocol


class ClientHandler:
    def __init__(self, client_socket, dispatcher):
        self.client_socket = client_socket
        self.dispatcher = dispatcher
        self.protocol = Protocol()
        self.running = True

    # The main loop that listens for incoming messages from the Android app
    def run(self):
        print("ClientHandler started")

        while self.running:
            try:
                data = self.client_socket.recv(4096)

                # Detection: If the socket receives empty data, the user closed the app
                if not data:
                    print("Client disconnected")
                    break

                # Converts raw bytes from the network into a readable string
                message = data.decode().strip()
                print(f"Received: {message}")

                parsed = self.protocol.parse(message)

                # Validation: Ensures the message isn't empty before trying to process it
                if not parsed["command"]:
                    self.send_response("ERROR|Empty command")
                    continue

                # Dispatches the command to the right service and gets the result
                response = self.dispatcher.dispatch(parsed)
                self.send_response(response)

            except Exception as e:
                print(f"ClientHandler error: {e}")
                self.send_response("ERROR|Server error")
                break

        self.close()

    # Formats and sends the final answer back to the Android app
    def send_response(self, response: str):
        """
        Sends a response to the client.
        We add \n specifically so the Android BufferedReader.readLine() works.
        """
        try:
            full_response = response + "\n"
            self.client_socket.sendall(full_response.encode('utf-8'))
        except Exception as e:
            print(f"Error sending response: {e}")

    def close(self):
        self.running = False
        self.client_socket.close()
        print("ClientHandler closed connection")
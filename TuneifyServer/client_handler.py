# client_handler.py

"""
Handles a single client connection, including authentication,
secure handshake (RSA + Diffie-Hellman), session management,
and encrypted message processing.
"""

import json
import base64
from protocol import Protocol
from crypto_utils import (
    get_public_key_pem, load_rsa_private_key,
    generate_dh_keypair, compute_dh_shared_secret, derive_aes_key,
    rsa_sign, generate_session_token, DH_PARAMETERS
)
from cryptography.hazmat.primitives import serialization

VALID_TOKENS = set()


class ClientHandler:

    _rsa_private_key = None

    @classmethod
    def load_rsa_key(cls) -> None:
        # Input: None
        # Output: Loads RSA private key into class memory

        if cls._rsa_private_key is None:
            cls._rsa_private_key = load_rsa_private_key()

    def __init__(self, client_socket, dispatcher):

        # Input: client_socket (socket), dispatcher (object)
        # Output: Initializes ClientHandler instance

        self.client_socket  = client_socket
        self.dispatcher     = dispatcher
        self.protocol       = Protocol()
        self.running        = True
        self.aes_key        = None
        self.session_token  = None
        self.logged_in_user = None
        ClientHandler.load_rsa_key()

    def run(self) -> None:

        # Input: None
        # Output: Handles full client session lifecycle

        print("ClientHandler started")
        try:
            success = self._perform_handshake()
            if not success:
                print("Handshake failed — closing connection")
                self.close()
                return

            print("HANDSHAKE_OK sent successfully")

            reader = self.client_socket.makefile('r', encoding='utf-8')

            while self.running:
                try:
                    message = reader.readline()
                    if not message:
                        print("Client disconnected")
                        break

                    message = message.strip()

                    try:
                        parsed = self.protocol.parse_encrypted(message, self.aes_key)
                    except ValueError as e:
                        print(f"Security violation: {e}")
                        self._send_encrypted("ERROR|Invalid or tampered message")
                        break

                    command = parsed.get("command", "").upper()
                    print(f"Command received: {command}")

                    if command not in ("LOGIN", "REGISTER", "REQUEST_RESET", "VERIFY_RESET"):
                        token = parsed.get("parameters", {}).get("session_token")
                        if not self._validate_token(token):
                            self._send_encrypted("ERROR|Invalid or expired session token")
                            continue

                    response = self.dispatcher.dispatch(parsed)

                    if command == "LOGIN" and response.startswith("OK|"):
                        self.session_token = generate_session_token()
                        self.logged_in_user = parsed["parameters"].get("username")
                        VALID_TOKENS.add(self.session_token)
                        response = response + f"|TOKEN:{self.session_token}"

                    self._send_encrypted(response)

                except Exception as e:
                    print(f"ClientHandler error: {e}")
                    self._send_encrypted("ERROR|Server error")
                    break

        finally:
            self.close()

    def _perform_handshake(self) -> bool:

        # Input: None
        # Output: Returns True if handshake succeeds, else False

        try:
            dh_param_numbers = DH_PARAMETERS.parameter_numbers()
            p_hex = hex(dh_param_numbers.p)[2:]
            g_hex = hex(dh_param_numbers.g)[2:]

            handshake_msg = json.dumps({
                "type": "SERVER_HELLO",
                "public_key": get_public_key_pem()
            })
            self._send_raw(handshake_msg)

            client_data = self.client_socket.recv(8192).decode().strip()
            if not client_data:
                return False

            client_msg = json.loads(client_data)

            if client_msg.get("type") != "CLIENT_DH":
                return False

            client_dh_public_b64 = client_msg["dh_public"]

            server_dh_private, server_dh_public_b64 = generate_dh_keypair()

            signature = rsa_sign(
                server_dh_public_b64.encode("utf-8"),
                self._rsa_private_key
            )

            server_msg = json.dumps({
                "type": "SERVER_DH",
                "dh_public": server_dh_public_b64,
                "signature": signature
            })
            self._send_raw(server_msg)

            shared_secret = compute_dh_shared_secret(
                server_dh_private, client_dh_public_b64
            )
            self.aes_key = derive_aes_key(shared_secret)

            self._send_encrypted("HANDSHAKE_OK")
            return True

        except Exception as e:
            print(f"Handshake error: {e}")
            return False

    def _validate_token(self, token: str) -> bool:

        # Input: token (str)
        # Output: Returns True if token is valid

        if not token:
            return False
        import secrets
        return any(secrets.compare_digest(token, t) for t in VALID_TOKENS)

    def _send_raw(self, message: str) -> None:

        # Input: message (str)
        # Output: Sends raw message over socket

        try:
            self.client_socket.sendall((message + "\n").encode("utf-8"))
        except Exception as e:
            print(f"Send error: {e}")

    def _send_encrypted(self, response: str) -> None:

        # Input: response (str)
        # Output: Sends encrypted message over socket

        try:
            encrypted = self.protocol.build_encrypted(response, self.aes_key)
            self.client_socket.sendall((encrypted + "\n").encode("utf-8"))
        except Exception as e:
            print(f"Encrypted send error: {e}")

    def close(self) -> None:

        # Input: None
        # Output: Closes client connection safely

        self.running = False
        self.aes_key = None
        self.session_token = None
        try:
            self.client_socket.close()
        except Exception:
            pass
        print("ClientHandler closed connection")
"""
protocol.py

Handles message parsing and formatting for Tuneify's TCP protocol.
After the handshake, all messages are AES-256-GCM encrypted.

Message format (encrypted):
    JSON string: {
        "nonce":      "<base64>",
        "ciphertext": "<base64>",
        "tag":        "<base64>"
    }

After decryption, the inner payload is the same as before:
    {
        "command":    "LOGIN",
        "parameters": { ... }
    }
"""

import json
from crypto_utils import aes_encrypt, aes_decrypt


class Protocol:

    def parse(self, raw_message: str) -> dict:
        """
        Parses a raw plaintext (unencrypted) message.
        Used only during the handshake phase before AES is established.
        """
        try:
            data = json.loads(raw_message)
            return {
                "command":    data.get("command", ""),
                "parameters": data.get("parameters", {})
            }
        except (json.JSONDecodeError, Exception):
            return {"command": "", "parameters": {}}

    def parse_encrypted(self, raw_message: str, aes_key: bytes) -> dict:
        """
        Parses an AES-256-GCM encrypted message.
        Used for all messages AFTER the handshake.

        Raises ValueError if decryption or auth tag verification fails —
        caller should close the connection.
        """
        try:
            encrypted_dict = json.loads(raw_message)

            # Decrypt — raises exception if tag is invalid (tampered message)
            plaintext = aes_decrypt(encrypted_dict, aes_key)

            data = json.loads(plaintext)
            return {
                "command":    data.get("command", ""),
                "parameters": data.get("parameters", {})
            }
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON in message")
        except Exception as e:
            raise ValueError(f"Decryption failed: {e}")

    def build_encrypted(self, response: str, aes_key: bytes) -> str:
        """
        Encrypts a response string using AES-256-GCM.
        Returns a JSON string ready to send over the socket.
        """
        encrypted = aes_encrypt(response, aes_key)
        return json.dumps(encrypted)
# protocol.py
"""
Handles message parsing and formatting for Tuneify's TCP protocol.

This module is responsible for:
- Parsing client messages (both plaintext during handshake and encrypted after handshake)
- Encrypting server responses using AES-256-GCM
- Decrypting incoming messages securely
- Maintaining a consistent JSON-based communication format

Message format (encrypted):
    JSON string:
    {
        "nonce":      "<base64>",
        "ciphertext": "<base64>",
        "tag":        "<base64>"
    }

After decryption, the inner payload format is:
    {
        "command":    "LOGIN",
        "parameters": { ... }
    }
"""

import json
from crypto_utils import aes_encrypt, aes_decrypt


class Protocol:

    # Parses a plaintext (unencrypted) message
    # Used ONLY during handshake phase before AES encryption is established
    # Input: raw_message (str JSON string)
    # Output: dict with command and parameters
    def parse(self, raw_message: str) -> dict:
        try:
            data = json.loads(raw_message)
            return {
                "command":    data.get("command", ""),
                "parameters": data.get("parameters", {})
            }
        except (json.JSONDecodeError, Exception):
            return {"command": "", "parameters": {}}

    # Parses an encrypted AES-256-GCM message
    # Used for all communication AFTER handshake
    # Input: raw_message (str JSON encrypted payload), aes_key (bytes)
    # Output: dict with command and parameters
    # Raises: ValueError if JSON is invalid or decryption fails
    def parse_encrypted(self, raw_message: str, aes_key: bytes) -> dict:
        try:
            encrypted_dict = json.loads(raw_message)

            # Decrypts message (will fail if tampered or invalid tag)
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

    # Encrypts a server response using AES-256-GCM
    # Input: response (str), aes_key (bytes)
    # Output: encrypted JSON string ready to send via socket
    def build_encrypted(self, response: str, aes_key: bytes) -> str:
        encrypted = aes_encrypt(response, aes_key)
        return json.dumps(encrypted)
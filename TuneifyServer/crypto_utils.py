#crypto_utils.py

"""
Provides cryptographic utilities for secure client-server communication:
- Password hashing
- RSA key generation and signing
- Diffie-Hellman key exchange
- AES-GCM encryption/decryption
- Session token generation
"""

import os
import hashlib
import secrets
import base64
from cryptography.hazmat.primitives.asymmetric.dh import DHParameterNumbers

from cryptography.hazmat.primitives.asymmetric import rsa, padding, dh
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.serialization import load_der_public_key
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.backends import default_backend


PEPPER = "TuneifySecretPepper2024!@#"


_P = int(
    "FFFFFFFFFFFFFFFFC90FDAA22168C234C4C6628B80DC1CD1"
    "29024E088A67CC74020BBEA63B139B22514A08798E3404DD"
    "EF9519B3CD3A431B302B0A6DF25F14374FE1356D6D51C245"
    "E485B576625E7EC6F44C42E9A637ED6B0BFF5CB6F406B7ED"
    "EE386BFB5A899FA5AE9F24117C4B1FE649286651ECE45B3D"
    "C2007CB8A163BF0598DA48361C55D39A69163FA8FD24CF5F"
    "83655D23DCA3AD961C62F356208552BB9ED529077096966D"
    "670C354E4ABC9804F1746C08CA18217C32905E462E36CE3B"
    "E39E772C180E86039B2783A2EC07A28FB5C55DF06F4C52C9"
    "DE2BCBF6955817183995497CEA956AE515D2261898FA0510"
    "15728E5A8AACAA68FFFFFFFFFFFFFFFF",
    16
)

_G = 2

DH_PARAMETERS = DHParameterNumbers(_P, _G).parameters(default_backend())


# Input: password (str)
# Output: hashed password (str), salt (str) -> tuple[str, str]
# Uses PBKDF2 with SHA-256 + server pepper for secure password storage

def hash_password(password: str) -> tuple[str, str]:
    salt = secrets.token_bytes(16)
    salted = (password + PEPPER).encode()

    hashed = hashlib.pbkdf2_hmac(
        "sha256",
        salted,
        salt,
        100_000
    )

    return hashed.hex(), salt.hex()


# Input: password (str), stored_hash (str), stored_salt (str)
# Output: True if password matches stored hash -> bool

def verify_password(password: str, stored_hash: str, stored_salt: str) -> bool:
    salt = bytes.fromhex(stored_salt)
    salted = (password + PEPPER).encode()

    candidate = hashlib.pbkdf2_hmac(
        "sha256",
        salted,
        salt,
        100_000
    )

    return secrets.compare_digest(candidate.hex(), stored_hash)


# Input: None
# Output: creates RSA key pair files -> None

def generate_rsa_keys() -> None:
    os.makedirs("keys", exist_ok=True)

    key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )

    with open("keys/server_private.pem", "wb") as f:
        f.write(key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ))

    with open("keys/server_public.pem", "wb") as f:
        f.write(key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ))


# Input: None
# Output: RSA private key object

def load_rsa_private_key():
    with open("keys/server_private.pem", "rb") as f:
        return serialization.load_pem_private_key(
            f.read(),
            password=None,
            backend=default_backend()
        )


# Input: None
# Output: RSA public key PEM string -> str

def get_public_key_pem() -> str:
    with open("keys/server_public.pem", "rb") as f:
        return f.read().decode()


# Input: data (bytes), private_key
# Output: RSA signature (base64 string) -> str
# Signs data to prevent MITM attacks during DH exchange

def rsa_sign(data: bytes, private_key) -> str:
    signature = private_key.sign(
        data,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=32
        ),
        hashes.SHA256()
    )
    return base64.b64encode(signature).decode()


# Input: data (bytes), signature (str), public_key
# Output: True if signature is valid -> bool

def rsa_verify(data: bytes, signature_b64: str, public_key) -> bool:
    try:
        public_key.verify(
            base64.b64decode(signature_b64),
            data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return True
    except Exception:
        return False


# Input: None
# Output: (private_key, public_key_b64) -> tuple
# Generates ephemeral DH keypair per session for forward secrecy

def generate_dh_keypair():
    private_key = DH_PARAMETERS.generate_private_key()

    public_key = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    return private_key, base64.b64encode(public_key).decode()


# Input: private_key, peer_public_b64 (str)
# Output: shared secret (bytes) -> bytes
# Performs Diffie-Hellman key exchange

def compute_dh_shared_secret(private_key, peer_public_b64: str):
    peer_der = base64.b64decode(peer_public_b64)
    peer_key = load_der_public_key(peer_der)

    return private_key.exchange(peer_key)


# Input: shared_secret (bytes)
# Output: AES-256 key (bytes) -> bytes
# Hashes shared secret to fixed-length encryption key

def derive_aes_key(shared_secret: bytes) -> bytes:
    return hashlib.sha256(shared_secret).digest()


# Input: plaintext (str), key (bytes)
# Output: encrypted data dict -> dict
# Uses AES-GCM for authenticated encryption

def aes_encrypt(plaintext: str, key: bytes) -> dict:
    aesgcm = AESGCM(key)
    nonce = secrets.token_bytes(12)
    ciphertext_with_tag = aesgcm.encrypt(nonce, plaintext.encode("utf-8"), None)

    return {
        "nonce": base64.b64encode(nonce).decode(),
        "ciphertext": base64.b64encode(ciphertext_with_tag).decode()
    }


# Input: encrypted dict, key (bytes)
# Output: decrypted plaintext (str) -> str

def aes_decrypt(data: dict, key: bytes) -> str:
    aesgcm = AESGCM(key)
    nonce = base64.b64decode(data["nonce"])
    ciphertext = base64.b64decode(data["ciphertext"])
    return aesgcm.decrypt(nonce, ciphertext, None).decode("utf-8")


# Input: None
# Output: session token (str) -> str

def generate_session_token() -> str:
    return secrets.token_hex(32)


if __name__ == "__main__":
    print("Generating RSA keys...")
    generate_rsa_keys()
    print("DONE → keys created")
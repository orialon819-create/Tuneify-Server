"""
crypto_utils.py (STABLE WORKING VERSION)

Fixes:
✔ Stable Diffie-Hellman parameters (NO regeneration crash)
✔ Correct AES-GCM format (nonce + ciphertext + tag)
✔ Compatible with Android client
✔ Clean cryptographic flow for handshake system
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


# ─────────────────────────────────────────────
# PEPPER (server-only secret)
# ─────────────────────────────────────────────
PEPPER = "TuneifySecretPepper2024!@#"


# ─────────────────────────────────────────────
# FIXED DH PARAMETERS (IMPORTANT)
# Must be stable across server restarts
# ─────────────────────────────────────────────
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


# ════════════════════════════════════════
# PASSWORD SECURITY
# ════════════════════════════════════════

def hash_password(password: str):
    salt = secrets.token_bytes(16)
    salted = (password + PEPPER).encode()

    hashed = hashlib.pbkdf2_hmac(
        "sha256",
        salted,
        salt,
        100_000
    )

    return hashed.hex(), salt.hex()


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


# ════════════════════════════════════════
# RSA KEY MANAGEMENT
# ════════════════════════════════════════

def generate_rsa_keys():
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


def load_rsa_private_key():
    with open("keys/server_private.pem", "rb") as f:
        return serialization.load_pem_private_key(
            f.read(),
            password=None,
            backend=default_backend()
        )


def get_public_key_pem():
    with open("keys/server_public.pem", "rb") as f:
        return f.read().decode()


def rsa_sign(data: bytes, private_key) -> str:
    signature = private_key.sign(
        data,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=32  # match SHA-256 digest size, which Android expects by default
        ),
        hashes.SHA256()
    )
    return base64.b64encode(signature).decode()

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


# ════════════════════════════════════════
# DIFFIE-HELLMAN
# ════════════════════════════════════════

def generate_dh_keypair():
    private_key = DH_PARAMETERS.generate_private_key()

    public_key = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    return private_key, base64.b64encode(public_key).decode()


def compute_dh_shared_secret(private_key, peer_public_b64: str):
    peer_der = base64.b64decode(peer_public_b64)

    # Android sends DER-encoded public key (via keyPair.public.encoded)
    # NOT a PEM file — so use load_der_public_key, not load_pem_public_key
    peer_key = load_der_public_key(peer_der)

    return private_key.exchange(peer_key)

def derive_aes_key(shared_secret: bytes) -> bytes:
    return hashlib.sha256(shared_secret).digest()


# ════════════════════════════════════════
# AES-GCM (FIXED + COMPATIBLE WITH ANDROID)
# ════════════════════════════════════════

def aes_encrypt(plaintext: str, key: bytes) -> dict:
    aesgcm = AESGCM(key)
    nonce = secrets.token_bytes(12)
    ciphertext_with_tag = aesgcm.encrypt(nonce, plaintext.encode("utf-8"), None)

    return {
        "nonce":      base64.b64encode(nonce).decode(),
        "ciphertext": base64.b64encode(ciphertext_with_tag).decode()
        # NO "tag" field — tag is already appended inside ciphertext_with_tag
    }

def aes_decrypt(data: dict, key: bytes) -> str:
    aesgcm = AESGCM(key)
    nonce      = base64.b64decode(data["nonce"])
    ciphertext = base64.b64decode(data["ciphertext"])
    return aesgcm.decrypt(nonce, ciphertext, None).decode("utf-8")
# ════════════════════════════════════════
# SESSION TOKENS
# ════════════════════════════════════════

def generate_session_token():
    return secrets.token_hex(32)


# ════════════════════════════════════════
# AUTO-RUN KEY GENERATION
# ════════════════════════════════════════

if __name__ == "__main__":
    print("Generating RSA keys...")
    generate_rsa_keys()
    print("DONE → keys/server_private.pem created")
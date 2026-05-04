import os
import base64
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes


def _get_key() -> bytes:
    key_b64 = os.environ.get('TRANSACTION_AES_KEY')
    if not key_b64:
        raise RuntimeError('Missing TRANSACTION_AES_KEY environment variable')
    try:
        return base64.b64decode(key_b64)
    except Exception as e:
        raise RuntimeError('Invalid TRANSACTION_AES_KEY value') from e


def encrypt_bytes(plaintext: bytes) -> bytes:
    """Encrypt bytes using AES-GCM. Returns nonce + tag + ciphertext bytes."""
    key = _get_key()
    if not isinstance(plaintext, (bytes, bytearray)):
        raise TypeError('plaintext must be bytes')
    nonce = get_random_bytes(12)
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    ciphertext, tag = cipher.encrypt_and_digest(plaintext)
    return nonce + tag + ciphertext


def decrypt_bytes(payload: bytes) -> bytes:
    """Decrypt bytes produced by encrypt_bytes (nonce + tag + ciphertext)."""
    key = _get_key()
    if not payload:
        return b''
    if len(payload) < 28:
        raise ValueError('Invalid payload')
    nonce = payload[:12]
    tag = payload[12:28]
    ciphertext = payload[28:]
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    plaintext = cipher.decrypt_and_verify(ciphertext, tag)
    return plaintext

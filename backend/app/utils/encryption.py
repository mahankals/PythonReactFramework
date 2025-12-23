"""
Encryption utilities for sensitive data (VHI credentials, etc.)
Uses Fernet symmetric encryption with the app's secret key.
"""
import base64
import hashlib
from cryptography.fernet import Fernet
from app.config import settings


def _get_fernet_key() -> bytes:
    """
    Derive a valid Fernet key from the app's secret key.
    Fernet requires a 32-byte base64-encoded key.
    """
    # Use SHA256 to derive a 32-byte key from the secret
    key_bytes = hashlib.sha256(settings.secret_key.encode()).digest()
    # Fernet requires base64-encoded key
    return base64.urlsafe_b64encode(key_bytes)


def _get_fernet() -> Fernet:
    """Get Fernet instance for encryption/decryption"""
    return Fernet(_get_fernet_key())


def encrypt_string(plaintext: str) -> str:
    """
    Encrypt a string and return base64-encoded ciphertext.

    Args:
        plaintext: The string to encrypt

    Returns:
        Base64-encoded encrypted string
    """
    if not plaintext:
        return plaintext

    fernet = _get_fernet()
    encrypted = fernet.encrypt(plaintext.encode())
    return encrypted.decode()


def decrypt_string(ciphertext: str) -> str:
    """
    Decrypt a base64-encoded ciphertext string.

    Args:
        ciphertext: Base64-encoded encrypted string

    Returns:
        Decrypted plaintext string
    """
    if not ciphertext:
        return ciphertext

    try:
        fernet = _get_fernet()
        decrypted = fernet.decrypt(ciphertext.encode())
        return decrypted.decode()
    except Exception:
        # If decryption fails, assume it's already plaintext (migration case)
        return ciphertext


def is_encrypted(value: str) -> bool:
    """
    Check if a string appears to be Fernet-encrypted.
    Fernet tokens start with 'gAAAAA'.
    """
    if not value:
        return False
    return value.startswith("gAAAAA")

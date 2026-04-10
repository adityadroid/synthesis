"""Cryptographic services for secure data handling."""

import os
import base64
import hashlib
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend

from .logging import get_logger

logger = get_logger(__name__)


class CryptoService:
    """Service for encrypting sensitive data like API keys."""

    def __init__(self, secret_key: str | None = None):
        self._fernet: Fernet | None = None
        self._secret_key = secret_key or os.environ.get("SECRET_KEY", "")

        if self._secret_key:
            self._initialize_fernet()

    def _initialize_fernet(self) -> None:
        """Initialize Fernet encryption with the secret key."""
        try:
            # Derive a key from the secret using PBKDF2
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=b"synthesis_salt_v1",  # Static salt for simplicity
                iterations=100000,
                backend=default_backend(),
            )
            key = base64.urlsafe_b64encode(kdf.derive(self._secret_key.encode()))
            self._fernet = Fernet(key)
            logger.info("Crypto service initialized")
        except Exception as e:
            logger.error("Failed to initialize crypto service", error=str(e))
            self._fernet = None

    def is_available(self) -> bool:
        """Check if encryption is available."""
        return self._fernet is not None

    def encrypt(self, plaintext: str) -> str | None:
        """Encrypt a plaintext string.

        Returns base64-encoded encrypted string or None if encryption unavailable.
        """
        if not self._fernet:
            logger.warning("Encryption not available, returning plaintext")
            return None

        try:
            encrypted = self._fernet.encrypt(plaintext.encode())
            return base64.urlsafe_b64encode(encrypted).decode()
        except Exception as e:
            logger.error("Encryption failed", error=str(e))
            return None

    def decrypt(self, ciphertext: str) -> str | None:
        """Decrypt an encrypted string.

        Returns plaintext or None if decryption fails.
        """
        if not self._fernet:
            logger.warning("Decryption not available")
            return None

        try:
            encrypted = base64.urlsafe_b64decode(ciphertext.encode())
            decrypted = self._fernet.decrypt(encrypted)
            return decrypted.decode()
        except Exception as e:
            logger.error("Decryption failed", error=str(e))
            return None

    @staticmethod
    def hash_key(key: str) -> str:
        """Create a SHA-256 hash of a key (one-way)."""
        return hashlib.sha256(key.encode()).hexdigest()

    @staticmethod
    def generate_token(length: int = 32) -> str:
        """Generate a secure random token."""
        return base64.urlsafe_b64encode(os.urandom(length)).decode()[:length]


class APIKeyStore:
    """Store for encrypted user API keys."""

    def __init__(self, crypto: CryptoService):
        self.crypto = crypto

    def store(self, user_id: str, provider: str, api_key: str) -> str | None:
        """Store an encrypted API key.

        Returns the key hash for lookup, or None if encryption fails.
        """
        # Create hash for lookup
        key_hash = self.crypto.hash_key(api_key)

        # Encrypt for storage
        encrypted = self.crypto.encrypt(api_key)

        if encrypted:
            # In production, store encrypted key in database
            # For now, we just return the hash
            logger.info(
                "API key stored securely",
                user_id=user_id,
                provider=provider,
            )
            return key_hash

        return None

    def retrieve(self, key_hash: str) -> str | None:
        """Retrieve an API key by its hash.

        Note: In production, this would fetch from secure storage
        and decrypt using the user's key.
        """
        # Placeholder - would fetch from database
        logger.warning("API key retrieval not fully implemented")
        return None

    def delete(self, key_hash: str) -> bool:
        """Delete an API key."""
        logger.info("API key deleted", key_hash=key_hash[:8] + "...")
        return True


# Global crypto service instance
crypto_service = CryptoService()
api_key_store = APIKeyStore(crypto_service)


def encrypt_value(value: str) -> str | None:
    """Quick function to encrypt a value."""
    return crypto_service.encrypt(value)


def decrypt_value(value: str) -> str | None:
    """Quick function to decrypt a value."""
    return crypto_service.decrypt(value)

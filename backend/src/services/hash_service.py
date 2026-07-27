"""File hash calculation service."""

import hashlib

from src.logging_config import get_logger

logger = get_logger("hash_service")


class HashService:
    """Handles file hash calculations."""

    def calculate(self, content: bytes) -> dict[str, str]:
        """Calculate MD5, SHA1, and SHA256 hashes for file content."""
        hashes = {
            "md5": hashlib.md5(content).hexdigest(),
            "sha1": hashlib.sha1(content).hexdigest(),
            "sha256": hashlib.sha256(content).hexdigest(),
        }
        logger.info("Hash calculated", extra={"file_size": len(content)})
        return hashes

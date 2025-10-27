# utils.py
import hashlib

def hash_password(password: str) -> str:
    """Return SHA-256 hex digest of the password."""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

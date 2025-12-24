from __future__ import annotations

import base64
import os
import hashlib
from cryptography.fernet import Fernet

def derive_key(password: str, salt: bytes) -> bytes:
    # PBKDF2-HMAC-SHA256
    key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 200_000, dklen=32)
    return base64.urlsafe_b64encode(key)

def new_salt() -> bytes:
    return os.urandom(16)

def fernet_from_password(password: str, salt: bytes) -> Fernet:
    return Fernet(derive_key(password, salt))

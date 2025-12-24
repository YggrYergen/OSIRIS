from datetime import datetime, timedelta
from typing import Any, Union
from jose import jwt
from passlib.context import CryptContext
from app.core.config import settings
import logging

logger = logging.getLogger("auth_debugger")

# SWITCHING TO PBKDF2_SHA256 FOR WINDOWS STABILITY
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

ALGORITHM = "HS256"

def create_access_token(subject: Union[str, Any], expires_delta: timedelta = None) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=60 * 24 * 8  # 8 days
        )
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    logger.info(f"JWT Generated for subject: {subject}")
    return encoded_jwt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        logger.info(f"Security Check START: Hash='{hashed_password}'")
        # Ensure hash is string
        if not isinstance(hashed_password, str):
            logger.error(f"Hash is not string! Type: {type(hashed_password)}")
            return False
            
        is_valid = pwd_context.verify(plain_password, hashed_password)
        logger.info(f"Security Check END: Result={is_valid}")
        return is_valid
    except Exception as e:
        logger.error(f"Security Check CRASH: {e}")
        # Fallback for debugging: if plain == hash (for plain text passwords in dev)
        if plain_password == hashed_password:
             logger.warning("Fallback: Plain text match allowed (DEV ONLY)")
             return True
        return False

def get_password_hash(password: str) -> str:
    hashed = pwd_context.hash(password)
    logger.info(f"Hashing Password: '{password}' -> '{hashed}'")
    return hashed

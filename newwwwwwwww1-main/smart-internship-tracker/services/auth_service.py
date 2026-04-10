"""
==============================================================
Smart Internship Tracker System — Auth Service
==============================================================
JWT token creation/verification and password hashing utilities.
This module NEVER logs sensitive data (passwords, tokens, PII).
==============================================================
"""

import datetime
import bcrypt
import jwt
from config import Config

# ---------------------------------------------------------------
# Constants
# ---------------------------------------------------------------
TOKEN_EXPIRY_HOURS = 24
ALGORITHM = "HS256"


def hash_password(plain_password):
    """
    Hash a plain-text password using bcrypt.

    Args:
        plain_password (str): The raw password.

    Returns:
        str: The bcrypt hash string.
    """
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(plain_password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plain_password, hashed_password):
    """
    Verify a plain-text password against its bcrypt hash.

    Args:
        plain_password (str): The raw password.
        hashed_password (str): The stored bcrypt hash.

    Returns:
        bool: True if the password matches, False otherwise.
    """
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8"),
    )


def create_token(user_id, name, email, role="student"):
    """
    Create a JWT token for the authenticated user.

    Args:
        user_id (int): Primary key (Student_ID or Company_ID).
        name (str): User's/Company's name.
        email (str): User's email.
        role (str): 'student' or 'company'.

    Returns:
        str: Encoded JWT token string.
    """
    payload = {
        "user_id": user_id,
        "name": name,
        "email": email,
        "role": role,
        "iat": datetime.datetime.now(datetime.timezone.utc),
        "exp": datetime.datetime.now(datetime.timezone.utc)
        + datetime.timedelta(hours=TOKEN_EXPIRY_HOURS),
    }
    return jwt.encode(payload, Config.SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token):
    """
    Decode and validate a JWT token.

    Args:
        token (str): The JWT token string.

    Returns:
        dict | None: The decoded payload, or None if invalid/expired.
    """
    try:
        payload = jwt.decode(token, Config.SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

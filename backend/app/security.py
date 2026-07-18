"""
Password hashing + JWT helpers.

Replaces the old auth.py placeholder comment block — this is the real
implementation: bcrypt for password storage, python-jose for signed,
expiring JWTs. Nothing here talks to MongoDB; routers own the DB calls.
"""

from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import get_settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain_password: str) -> str:
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(user_id: str, tenant_id: str) -> str:
    settings = get_settings()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expire_minutes)
    payload = {"sub": user_id, "tenant_id": tenant_id, "exp": expire}
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")


def decode_access_token(token: str) -> dict | None:
    """Returns the decoded payload, or None if the token is invalid/expired.

    A `get_current_user` FastAPI dependency (Days 5-7 task — tenant-scoped
    auth middleware) will build on this to protect the other routers.
    """
    settings = get_settings()
    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
    except JWTError:
        return None

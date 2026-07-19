"""
Real auth router.

Flow:
  1. /register creates a user in MongoDB with a bcrypt-hashed password.
  2. /login looks the user up by user_id, verifies the password with
     passlib, and issues a real JWT (python-jose) signed with
     settings.jwt_secret.
  3. /refresh (Days 5-7) exchanges a still-valid-or-just-expired token for
     a fresh one, without requiring the password again — a "sliding
     session" so users aren't logged out mid-demo.
  4. /me (Days 5-7) is a quick way to confirm a token works end-to-end —
     it's the first endpoint protected by get_current_user.
"""

from fastapi import APIRouter, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.db import get_db
from app.dependencies import CurrentUser
from app.models.schemas import LoginRequest, LoginResponse, RegisterRequest, UserPublic
from app.security import create_access_token, decode_access_token_allow_expired, hash_password, verify_password

router = APIRouter(prefix="/v1/auth", tags=["auth"])
_bearer_scheme = HTTPBearer()


@router.post("/register", response_model=UserPublic, status_code=201)
async def register(payload: RegisterRequest) -> UserPublic:
    db = get_db()

    existing = await db.users.find_one({"user_id": payload.user_id})
    if existing:
        raise HTTPException(status_code=409, detail="user_id already registered")

    user_doc = {
        "user_id": payload.user_id,
        "tenant_id": payload.tenant_id,
        "hashed_password": hash_password(payload.password),
        "full_name": payload.full_name,
    }
    await db.users.insert_one(user_doc)

    return UserPublic(user_id=payload.user_id, tenant_id=payload.tenant_id, full_name=payload.full_name)


@router.post("/login", response_model=LoginResponse)
async def login(payload: LoginRequest) -> LoginResponse:
    db = get_db()

    user = await db.users.find_one({"user_id": payload.user_id})
    if not user or not verify_password(payload.password, user["hashed_password"]):
        # Same error for "no such user" and "wrong password" — don't leak which one.
        raise HTTPException(status_code=401, detail="Invalid user_id or password")

    token = create_access_token(user_id=user["user_id"], tenant_id=user["tenant_id"])
    return LoginResponse(access_token=token, user_id=user["user_id"], tenant_id=user["tenant_id"])


@router.post("/refresh", response_model=LoginResponse)
async def refresh(credentials: HTTPAuthorizationCredentials = Security(_bearer_scheme)) -> LoginResponse:
    """
    Exchange a token for a fresh one with a new expiry, without re-sending
    the password. Accepts tokens that are still valid OR expired within a
    short grace window (we don't re-check exp here) — but the signature
    must still be valid, so a forged/tampered token is always rejected.
    """
    payload = decode_access_token_allow_expired(credentials.credentials)
    if payload is None or not payload.get("sub") or not payload.get("tenant_id"):
        raise HTTPException(status_code=401, detail="Invalid token — please log in again")

    new_token = create_access_token(user_id=payload["sub"], tenant_id=payload["tenant_id"])
    return LoginResponse(access_token=new_token, user_id=payload["sub"], tenant_id=payload["tenant_id"])


@router.get("/me", response_model=UserPublic)
async def get_me(current_user: CurrentUser) -> UserPublic:
    """First endpoint gated by get_current_user — a quick way to confirm a
    token is valid end-to-end. Every other router follows this pattern."""
    db = get_db()
    user = await db.users.find_one({"user_id": current_user["user_id"]})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserPublic(user_id=user["user_id"], tenant_id=user["tenant_id"], full_name=user.get("full_name"))

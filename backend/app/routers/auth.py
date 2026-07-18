"""
Real auth router (Days 2-4 task — replaces the demo placeholder).

Flow:
  1. /register creates a user in MongoDB with a bcrypt-hashed password.
  2. /login looks the user up by user_id, verifies the password with
     passlib, and issues a real JWT (python-jose) signed with
     settings.jwt_secret.

Tenant-scoped middleware (a `get_current_user` dependency used by every
other router) is a Days 5-7 task and intentionally not built here yet.
"""

from fastapi import APIRouter, HTTPException

from app.db import get_db
from app.models.schemas import LoginRequest, LoginResponse, RegisterRequest, UserPublic
from app.security import create_access_token, hash_password, verify_password

router = APIRouter(prefix="/v1/auth", tags=["auth"])


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

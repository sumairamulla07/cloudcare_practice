"""
Demo auth router.

PLACEHOLDER: this accepts ANY user_id/password and returns a fake token —
exactly like the frontend's lib/auth.ts demo login. It exists so the
frontend has a real endpoint to call instead of only faking it client-side.

To make this real before you go further than the hackathon:
  1. Add a `users` collection in MongoDB (user_id, hashed_password, tenant_id).
  2. On login, look up the user, verify the password with passlib (bcrypt).
  3. Issue a real JWT (python-jose is already in requirements.txt) signed
     with settings.jwt_secret, and return it.
  4. Set it as an httpOnly cookie from the frontend's API route, or have the
     frontend store it in memory and send it as a Bearer token — not
     localStorage, which is vulnerable to XSS.
  5. Add a dependency (e.g. `get_current_user`) that other routers use to
     require auth, and enforce tenant_id scoping on every query.
"""

import uuid

from fastapi import APIRouter

from app.models.schemas import LoginRequest, LoginResponse

router = APIRouter(prefix="/v1/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
async def login(payload: LoginRequest) -> LoginResponse:
    # TODO: replace with real lookup + password verification against MongoDB
    fake_token = f"demo-{uuid.uuid4().hex[:24]}"
    return LoginResponse(
        access_token=fake_token,
        user_id=payload.user_id or "Demo User",
    )

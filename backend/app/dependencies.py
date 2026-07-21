"""
Tenant-scoped auth middleware (Days 5-7 task).

`get_current_user` is a FastAPI dependency every protected router now
requires. It reads the `Authorization: Bearer <token>` header, validates
the JWT, and returns {"user_id": ..., "tenant_id": ...} so route handlers
can scope every DB query to the caller's tenant.

Usage in a router:

    from app.dependencies import CurrentUser

    @router.get("")
    async def list_resources(current_user: CurrentUser) -> list[Resource]:
        docs = await collection.find({"tenant_id": current_user["tenant_id"]}) ...
"""

from typing import Annotated, TypedDict

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.security import decode_access_token

_bearer_scheme = HTTPBearer(auto_error=False)


class AuthenticatedUser(TypedDict):
    user_id: str
    tenant_id: str


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer_scheme)],
) -> AuthenticatedUser:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing bearer token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_access_token(credentials.credentials)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    tenant_id = payload.get("tenant_id")
    if not user_id or not tenant_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Malformed token")

    return {"user_id": user_id, "tenant_id": tenant_id}


# Shorthand type alias so routers can write `current_user: CurrentUser`
# instead of repeating the Annotated[...] every time.
CurrentUser = Annotated[AuthenticatedUser, Depends(get_current_user)]

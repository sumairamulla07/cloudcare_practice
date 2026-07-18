from fastapi import APIRouter, Depends

from app.mock_data import RESOURCES
from app.models.schemas import Resource
from app.routers.auth import get_current_user

router = APIRouter(prefix="/v1/resources", tags=["resources"])


@router.get("", response_model=list[Resource])
async def list_resources(
    environment: str | None = None,
    status: str | None = None,
    current_user: dict = Depends(get_current_user)
) -> list[Resource]:
    """
    List monitored resources, optionally filtered by environment or status.

    TODO: replace with a Mongo query against the `resources` collection,
    e.g. db.resources.find({"environment": environment, "status": status}),
    once the collector service (blueprint section 9.2/9.3) is writing real
    AWS inventory + CloudWatch data in.
    """
    results = RESOURCES
    if environment:
        results = [r for r in results if r.environment == environment]
    if status:
        results = [r for r in results if r.status == status]
    return results

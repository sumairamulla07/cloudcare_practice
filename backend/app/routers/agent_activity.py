from fastapi import APIRouter

from app.mock_data import AGENT_ACTIVITY
from app.models.schemas import AgentActivityEntry

router = APIRouter(prefix="/v1/agent-activity", tags=["agent-activity"])


@router.get("", response_model=list[AgentActivityEntry])
async def list_agent_activity(run_id: str | None = None) -> list[AgentActivityEntry]:
    """
    TODO: replace with a Mongo query against the `execution_log` / `trace`
    fields of the CloudCareState documents for the given run_id (blueprint
    3.2), or stream these live over the WebSocket event channel described
    in blueprint 11.3 instead of polling this endpoint.
    """
    return AGENT_ACTIVITY

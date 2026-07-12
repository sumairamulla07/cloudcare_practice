import uuid
from datetime import datetime, timezone

from fastapi import APIRouter

from app.models.schemas import CloudCareState

router = APIRouter(prefix="/v1", tags=["accounts-runs"])


@router.post("/cloud-accounts/validate")
async def validate_cloud_account(role_arn: str, external_id: str) -> dict:
    """
    PLACEHOLDER: this should call sts.assume_role() (blueprint 9.2,
    app/services/collector) using the given role_arn + external_id, then
    call ec2.describe_regions() to confirm the read role actually works —
    and never store the returned temporary credentials.

    For the hackathon demo this just echoes back a fake "validated" result
    so the frontend onboarding flow has something to call.
    """
    return {
        "validated": bool(role_arn and external_id),
        "role_arn": role_arn,
        "supported_regions": ["ap-south-1", "us-east-1"],
        "note": "This is a placeholder response — wire up app/services/collector/aws_session.py to make this real.",
    }


@router.post("/runs", response_model=CloudCareState)
async def start_run(tenant_id: str = "demo-tenant", account_id: str = "demo-account") -> CloudCareState:
    """
    PLACEHOLDER: this should call build_graph().invoke(...) from
    app/services/orchestrator/graph.py to actually kick off the
    Monitor -> Analyze -> Decide -> Supervise -> Execute -> Verify pipeline.

    Right now it just creates an empty run record so the frontend has a
    run_id to poll / subscribe to.
    """
    return CloudCareState(
        run_id=f"run_{uuid.uuid4().hex[:12]}",
        tenant_id=tenant_id,
        account_id=account_id,
        status="observing",
        trace=[{"event": "run.created", "at": datetime.now(timezone.utc).isoformat()}],
    )

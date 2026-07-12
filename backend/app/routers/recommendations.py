from decimal import Decimal
from uuid import UUID, uuid4

from fastapi import APIRouter, HTTPException

from app.models.schemas import ActionProposal

router = APIRouter(prefix="/v1/recommendations", tags=["recommendations"])

# In-memory demo store — resets on server restart.
# TODO: replace with the `proposals` collection in MongoDB (blueprint 4.2
# has the equivalent SQL schema; the Mongo document shape can mirror it 1:1).
_PROPOSALS: dict[UUID, ActionProposal] = {
    p.proposal_id: p
    for p in [
        ActionProposal(
            proposal_id=uuid4(),
            resource_arn="arn:aws:ec2:ap-south-1:demo:instance/i-0912ab3c4d5e6f701",
            action_type="stop_instance",
            template_id="ec2.stop.v1",
            parameters={"instance_id": "i-0912ab3c4d5e6f701", "region": "ap-south-1"},
            expected_monthly_savings=Decimal("14.20"),
            risk_level="low",
            confidence=0.92,
            requires_human_approval=False,
            status="executed",
        ),
        ActionProposal(
            proposal_id=uuid4(),
            resource_arn="arn:aws:ec2:ap-south-1:demo:instance/i-0455cd8e9f0a1b234",
            action_type="resize_instance",
            template_id="ec2.resize.v1",
            parameters={"instance_id": "i-0455cd8e9f0a1b234", "region": "ap-south-1", "target_type": "t3.medium"},
            expected_monthly_savings=Decimal("22.00"),
            risk_level="medium",
            confidence=0.74,
            requires_human_approval=True,
            status="proposed",
        ),
    ]
}


@router.get("", response_model=list[ActionProposal])
async def list_recommendations(status: str | None = None, risk_level: str | None = None) -> list[ActionProposal]:
    results = list(_PROPOSALS.values())
    if status:
        results = [p for p in results if p.status == status]
    if risk_level:
        results = [p for p in results if p.risk_level == risk_level]
    return results


@router.post("/{proposal_id}/approve", response_model=ActionProposal)
async def approve_recommendation(proposal_id: UUID) -> ActionProposal:
    """
    TODO: this should call the Supervisor policy engine (blueprint 6.1) to
    re-validate the proposal against current policy before flipping status,
    and write an `approvals` record with the actor + reason + timestamp.
    """
    proposal = _PROPOSALS.get(proposal_id)
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")
    proposal.status = "approved"
    return proposal


@router.post("/{proposal_id}/execute", response_model=ActionProposal)
async def execute_recommendation(proposal_id: UUID) -> ActionProposal:
    """
    TODO: this should call the Executor service (blueprint 10.2) with the
    approved template + parameters, using an idempotency key, then trigger
    the Verifier (blueprint 10.3) before marking status as verified.
    """
    proposal = _PROPOSALS.get(proposal_id)
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")
    if proposal.status != "approved" and proposal.requires_human_approval:
        raise HTTPException(status_code=400, detail="Proposal requires approval before execution")
    proposal.status = "executed"
    return proposal

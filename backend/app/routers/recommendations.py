from decimal import Decimal
from uuid import UUID, uuid4

from fastapi import APIRouter, HTTPException

from app.db import get_db
from app.dependencies import CurrentUser
from app.models.schemas import ActionProposal

router = APIRouter(prefix="/v1/recommendations", tags=["recommendations"])

# Seed data used to populate the `proposals` collection the first time it's
# empty, so the demo/dashboard has something to show immediately.
_SEED_PROPOSALS: list[ActionProposal] = [
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


def _to_doc(proposal: ActionProposal) -> dict:
    """Mongo/BSON has no native Decimal type, so store savings as float and
    proposal_id as str; both are converted back on the way out."""
    doc = proposal.model_dump()
    doc["proposal_id"] = str(doc["proposal_id"])
    doc["expected_monthly_savings"] = float(doc["expected_monthly_savings"])
    return doc


def _from_doc(doc: dict) -> ActionProposal:
    doc = dict(doc)
    doc.pop("_id", None)
    doc["expected_monthly_savings"] = Decimal(str(doc["expected_monthly_savings"]))
    return ActionProposal(**doc)


async def _proposals_collection():
    db = get_db()
    if await db.proposals.count_documents({}) == 0:
        await db.proposals.insert_many([_to_doc(p) for p in _SEED_PROPOSALS])
    return db.proposals


@router.get("", response_model=list[ActionProposal])
async def list_recommendations(
    current_user: CurrentUser,
    status: str | None = None,
    risk_level: str | None = None,
) -> list[ActionProposal]:
    collection = await _proposals_collection()

    query: dict = {"tenant_id": current_user["tenant_id"]}
    if status:
        query["status"] = status
    if risk_level:
        query["risk_level"] = risk_level

    docs = await collection.find(query).to_list(length=None)
    return [_from_doc(doc) for doc in docs]


@router.post("/{proposal_id}/approve", response_model=ActionProposal)
async def approve_recommendation(proposal_id: UUID, current_user: CurrentUser) -> ActionProposal:
    """
    TODO (Days 8-10, Sumaira): call the Supervisor policy engine (blueprint
    6.1) to re-validate the proposal against current policy before flipping
    status, and write an `approvals` record with the actor + reason +
    timestamp.
    """
    collection = await _proposals_collection()
    doc = await collection.find_one({"proposal_id": str(proposal_id), "tenant_id": current_user["tenant_id"]})
    if not doc:
        raise HTTPException(status_code=404, detail="Proposal not found")

    await collection.update_one({"proposal_id": str(proposal_id)}, {"$set": {"status": "approved"}})
    doc["status"] = "approved"
    return _from_doc(doc)


@router.post("/{proposal_id}/execute", response_model=ActionProposal)
async def execute_recommendation(proposal_id: UUID, current_user: CurrentUser) -> ActionProposal:
    """
    TODO (Days 8-10, Sumaira): call the Executor service (blueprint 10.2)
    with the approved template + parameters, using an idempotency key, then
    trigger the Verifier (blueprint 10.3) before marking status as verified.
    """
    collection = await _proposals_collection()
    doc = await collection.find_one({"proposal_id": str(proposal_id), "tenant_id": current_user["tenant_id"]})
    if not doc:
        raise HTTPException(status_code=404, detail="Proposal not found")

    if doc["status"] != "approved" and doc["requires_human_approval"]:
        raise HTTPException(status_code=400, detail="Proposal requires approval before execution")

    await collection.update_one({"proposal_id": str(proposal_id)}, {"$set": {"status": "executed"}})
    doc["status"] = "executed"
    return _from_doc(doc)

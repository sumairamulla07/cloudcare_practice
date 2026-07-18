import uuid
import pytest
from unittest.mock import MagicMock, AsyncMock

from fastapi.testclient import TestClient

from app.main import app
from app.db import get_db
from app.services.policy.engine import evaluate, PolicyResult
from app.routers.recommendations import _PROPOSALS
from app.models.schemas import ActionProposal

client = TestClient(app)


# ---------------------------------------------------------------------------
# Policy Engine Guardrails Tests
# ---------------------------------------------------------------------------

def test_production_resources_never_auto_execute():
    """env=prod must require human approval and never auto-execute."""
    res = evaluate(
        environment="prod",
        risk_level="low",
        template_id="ec2.stop.v1",
        has_owner_tag=True,
        is_protected=False,
    )
    assert res.approved is True
    assert res.auto_execute is False
    assert res.requires_human_approval is True
    assert "production" in res.reason.lower()


def test_unknown_action_templates_blocked():
    """Actions with template IDs not in registry must be blocked."""
    res = evaluate(
        environment="dev",
        risk_level="low",
        template_id="unregistered.template.v1",
        has_owner_tag=True,
        is_protected=False,
    )
    assert res.approved is False
    assert res.auto_execute is False
    assert "unknown" in res.reason.lower()


def test_protected_resources_blocked():
    """Resources tagged protected must be blocked from any execution."""
    res = evaluate(
        environment="dev",
        risk_level="low",
        template_id="ec2.stop.v1",
        has_owner_tag=True,
        is_protected=True,
    )
    assert res.approved is False
    assert res.auto_execute is False
    assert "protected" in res.reason.lower()


def test_missing_ownership_tag_requires_approval():
    """Resources missing owner tag must not auto-execute, require approval."""
    res = evaluate(
        environment="dev",
        risk_level="low",
        template_id="ec2.stop.v1",
        has_owner_tag=False,
        is_protected=False,
    )
    assert res.approved is True
    assert res.auto_execute is False
    assert res.requires_human_approval is True
    assert "ownership" in res.reason.lower() or "missing" in res.reason.lower()


def test_low_risk_dev_staging_auto_executes():
    """Low-risk action in dev/staging with owner tag auto-executes."""
    res = evaluate(
        environment="dev",
        risk_level="low",
        template_id="ec2.stop.v1",
        has_owner_tag=True,
        is_protected=False,
    )
    assert res.approved is True
    assert res.auto_execute is True
    assert res.requires_human_approval is False


# ---------------------------------------------------------------------------
# Idempotency Tests
# ---------------------------------------------------------------------------

def test_execute_recommendation_idempotency():
    """Calling execute twice on an already executed proposal should be idempotent."""
    proposal_id = uuid.uuid4()
    proposal = ActionProposal(
        id=proposal_id,
        tenant_id="demo-tenant",
        account_id="demo-account",
        template_id="ec2.stop.v1",
        parameters={},
        reason="Test proposal",
        status="approved", # Starts as approved
        risk_level="low",
        requires_human_approval=True,
    )
    
    # Store it in the mock/in-memory Proposals dictionary
    _PROPOSALS[proposal_id] = proposal
    
    # Bypass get_current_user dependency override
    app.dependency_overrides[get_db] = lambda: MagicMock()
    # Mock current user
    from app.routers.auth import get_current_user
    app.dependency_overrides[get_current_user] = lambda: {"user_id": "demo.user"}
    
    # First execution should succeed and change status to executed
    response1 = client.post(f"/v1/recommendations/{proposal_id}/execute")
    assert response1.status_code == 200
    data1 = response1.json()
    assert data1["status"] == "executed"
    
    # Second execution should also succeed, returning same proposal with executed status (idempotent)
    response2 = client.post(f"/v1/recommendations/{proposal_id}/execute")
    assert response2.status_code == 200
    data2 = response2.json()
    assert data2["status"] == "executed"
    
    # Clean up overrides
    app.dependency_overrides.clear()
    if proposal_id in _PROPOSALS:
        del _PROPOSALS[proposal_id]

"""
Node functions for the LangGraph pipeline (blueprint section 3.1).

Every function here is a PLACEHOLDER that returns/merges fake data so the
graph in graph.py can actually run end-to-end today. Replace the body of
each function with real logic in this order (matches the 48-hour roadmap in
blueprint section 12.1):

    1. monitor   -> app/services/collector  (real AWS calls)
    2. analyze   -> app/services/analyzer   (real rule engine)
    3. decide    -> call an LLM (OpenRouter) with constrained structured output
    4. supervise -> app/services/policy     (real policy matrix, blueprint 6.1)
    5. execute   -> app/services/executor   (real boto3 calls, template-mapped)
    6. verify    -> app/services/verifier   (real health + savings check)

Each node receives and returns a dict shaped like CloudCareState
(app/models/schemas.py) so LangGraph can merge partial updates.
"""

from datetime import datetime, timezone


def _trace_event(state: dict, agent: str, summary: dict) -> dict:
    trace = state.get("trace", [])
    trace.append(
        {
            "agent": agent,
            "at": datetime.now(timezone.utc).isoformat(),
            "summary": summary,
        }
    )
    return {"trace": trace}


def monitor(state: dict) -> dict:
    # TODO: call app.services.collector.ec2 / cloudwatch / cost_explorer
    observation = {"resources_scanned": 47, "source": "mock"}
    return {"observation": observation, "status": "analyzing", **_trace_event(state, "monitor", observation)}


def analyze(state: dict) -> dict:
    # TODO: call app.services.analyzer.rules.classify_idle and friends
    findings = [{"rule_id": "ec2.idle.v1", "resource_id": "i-0912ab3c4d5e6f701", "confidence": 0.92}]
    return {"findings": findings, "status": "review", **_trace_event(state, "analyzer", {"findings": len(findings)})}


def decide(state: dict) -> dict:
    # TODO: call an LLM here (OPENROUTER_API_KEY in .env) with a constrained
    # JSON schema — see blueprint 6.2 ActionProposal for the target shape.
    proposals = [
        {
            "resource_arn": "arn:aws:ec2:ap-south-1:demo:instance/i-0912ab3c4d5e6f701",
            "action_type": "stop_instance",
            "template_id": "ec2.stop.v1",
            "risk_level": "low",
            "requires_human_approval": False,
        }
    ]
    return {"proposals": proposals, **_trace_event(state, "decision", {"proposals": len(proposals)})}


def supervise(state: dict) -> dict:
    # TODO: call app.services.policy.engine.evaluate() using the real policy
    # matrix (blueprint 6.1) — this stub always approves low-risk proposals.
    approvals = [{"decision": "execute", "reason": "low risk, dev environment"}]
    return {
        "approvals": approvals,
        "supervisor_decision": "execute",
        **_trace_event(state, "supervisor", {"decision": "execute"}),
    }


def execute(state: dict) -> dict:
    # TODO: call app.services.executor.actions with an idempotency key —
    # see blueprint 10.2 for the reference implementation.
    execution_log = [{"template_id": "ec2.stop.v1", "result": "stopped", "rollback_template": "ec2.start.v1"}]
    return {"execution_log": execution_log, "status": "executing", **_trace_event(state, "executor", {"executed": 1})}


def verify(state: dict) -> dict:
    # TODO: call app.services.verifier.health / savings — see blueprint 10.3.
    feedback = [{"status": "verified", "realized_savings": 14.20}]
    return {"feedback": feedback, "status": "verified", **_trace_event(state, "verifier", {"status": "verified"})}

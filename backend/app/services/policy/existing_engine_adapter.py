from app.services.policy.engine import evaluate


def evaluate_existing_policy(
    proposal: dict,
) -> dict:
    parameters = proposal.get("parameters", {})
    tags = parameters.get("tags", {})

    result = evaluate(
        environment=str(proposal.get("environment", "unknown")),
        risk_level=str(proposal.get("risk_level", "high")),
        template_id=str(proposal.get("action_template", "")),
        has_owner_tag=bool(
            parameters.get("has_owner_tag")
            or tags.get("Owner")
            or tags.get("owner")
        ),
        is_protected=bool(
            parameters.get("is_protected")
            or str(tags.get("Protected", "")).lower() == "true"
            or str(tags.get("protected", "")).lower() == "true"
        ),
    )

    return {
        "allowed": result.approved,
        "requires_human_review": result.requires_human_approval,
        "reason_codes": [result.reason],
        "policy_version": "existing-policy-v1",
    }

"""
Post-action verification — PLACEHOLDER, per blueprint section 10.3.

TODO: implement collect_health() to pull a short post-action CloudWatch
window (e.g. 30 minutes) and estimate_realized_savings() to compare
baseline vs. post-action normalized cost. Trigger rollback (using the
rollback_template from the executor registry) if health.regression_detected.
"""


def verify_action(resource_id: str, rollback_plan: dict | None) -> dict:
    raise NotImplementedError(
        "Implement collect_health() and estimate_realized_savings() once "
        "real CloudWatch + Cost Explorer data is flowing — see blueprint "
        "section 10.3 for the reference implementation."
    )

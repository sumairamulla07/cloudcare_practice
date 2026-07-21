"""
Idempotent executor — lifted from blueprint section 10.2.

PLACEHOLDER: this needs a real boto3 session (from
app/services/collector/aws_session.py) and a real lock_store /
execution_repo backed by MongoDB + Redis. Until those exist, calling this
will raise NotImplementedError — that's intentional, so it fails loudly
instead of pretending to stop a real instance.
"""


def stop_instance(session, proposal_id: str, instance_id: str, region: str):
    raise NotImplementedError(
        "Connect a real boto3 session + a MongoDB-backed execution_repo "
        "and a distributed lock (e.g. Redis) before calling this. See the "
        "blueprint section 10.2 for the reference implementation this "
        "should follow: check idempotency, describe instance state, call "
        "ec2.stop_instances(), then record the result."
    )

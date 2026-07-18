"""AWS cross-account session factory for CloudCare collectors."""

from datetime import datetime, timedelta, timezone

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

from app.config import get_settings


class AWSAuthenticationError(Exception):
    """Raised when CloudCare cannot assume the configured AWS role."""


_assumed_session: boto3.Session | None = None
_expires_at: datetime | None = None

_BOTOCORE_CONFIG = Config(
    connect_timeout=5,
    read_timeout=20,
    retries={
        "max_attempts": 4,
        "mode": "standard",
    },
    user_agent_extra="CloudCare/1.0",
)


def base_session() -> boto3.Session:
    settings = get_settings()
    if settings.aws_profile:
        return boto3.Session(
            profile_name=settings.aws_profile,
            region_name=settings.aws_region,
        )

    return boto3.Session(region_name=settings.aws_region)


def _session_needs_refresh() -> bool:
    if _assumed_session is None or _expires_at is None:
        return True

    refresh_before = datetime.now(timezone.utc) + timedelta(minutes=5)

    return refresh_before >= _expires_at


def assumed_session(run_id: str = "local-collector") -> boto3.Session:
    global _assumed_session, _expires_at

    if not _session_needs_refresh():
        assert _assumed_session is not None
        return _assumed_session

    settings = get_settings()
    if not settings.aws_read_role_arn or not settings.aws_external_id:
        raise RuntimeError(
            "AWS_READ_ROLE_ARN / AWS_EXTERNAL_ID are not set - fill them in "
            "backend/.env before calling assumed_session()."
        )

    sts = base_session().client(
        "sts",
        region_name=settings.aws_region,
        config=_BOTOCORE_CONFIG,
    )

    try:
        response = sts.assume_role(
            RoleArn=settings.aws_read_role_arn,
            RoleSessionName=f"cloudcare-{run_id[:12]}",
            ExternalId=settings.aws_external_id,
            DurationSeconds=3600,
        )
    except ClientError as error:
        error_code = error.response.get("Error", {}).get(
            "Code",
            "UNKNOWN_AWS_ERROR",
        )
        raise AWSAuthenticationError(
            f"CloudCare could not assume the AWS role: {error_code}"
        ) from error

    creds = response["Credentials"]
    _expires_at = creds["Expiration"]
    _assumed_session = boto3.Session(
        aws_access_key_id=creds["AccessKeyId"],
        aws_secret_access_key=creds["SecretAccessKey"],
        aws_session_token=creds["SessionToken"],
        region_name=settings.aws_region,
    )

    return _assumed_session


def aws_client(service_name: str, region_name: str | None = None):
    settings = get_settings()
    target_region = region_name or settings.aws_region

    if service_name == "ce":
        target_region = "us-east-1"

    return assumed_session().client(
        service_name,
        region_name=target_region,
        config=_BOTOCORE_CONFIG,
    )

"""EC2 inventory collector."""

from datetime import datetime, timezone

from botocore.exceptions import ClientError

from app.config import get_settings
from app.services.collector.aws_session import aws_client


class EC2CollectionError(Exception):
    """Raised when EC2 inventory cannot be collected."""


def tags_to_dictionary(tags: list[dict] | None) -> dict[str, str]:
    result: dict[str, str] = {}

    for tag in tags or []:
        key = tag.get("Key")

        if not key:
            continue

        result[str(key)] = str(tag.get("Value", ""))

    return result


def find_tag(tags: dict[str, str], required_key: str) -> str | None:
    for key, value in tags.items():
        if key.lower() == required_key.lower():
            return value

    return None


def normalize_environment(tags: dict[str, str]) -> str:
    raw_environment = find_tag(tags, "Environment")

    if not raw_environment:
        return "unknown"

    normalized = raw_environment.strip().lower()
    aliases = {
        "dev": "development",
        "development": "development",
        "stage": "staging",
        "stg": "staging",
        "staging": "staging",
        "prod": "production",
        "production": "production",
    }

    return aliases.get(normalized, "unknown")


def normalize_instance(
    instance: dict,
    region: str,
    collected_at: datetime,
) -> dict:
    tags = tags_to_dictionary(instance.get("Tags"))
    resource_id = instance["InstanceId"]
    placement = instance.get("Placement") or {}
    state = instance.get("State") or {}
    environment = normalize_environment(tags)

    warnings: list[str] = []

    if not instance.get("Tags"):
        warnings.append("RESOURCE_HAS_NO_TAGS")

    if environment == "unknown":
        warnings.append("ENVIRONMENT_TAG_MISSING_OR_INVALID")

    return {
        "schema_version": "1.0",
        "provider": "aws",
        "resource_type": "ec2_instance",
        "region": region,
        "availability_zone": placement.get("AvailabilityZone"),
        "resource_id": resource_id,
        "name": find_tag(tags, "Name") or resource_id,
        "environment": environment,
        "instance_type": instance.get("InstanceType", "unknown"),
        "state": state.get("Name", "unknown"),
        "launched_at": instance.get("LaunchTime"),
        "collected_at": collected_at,
        "private_ip": instance.get("PrivateIpAddress"),
        "public_ip": instance.get("PublicIpAddress"),
        "vpc_id": instance.get("VpcId"),
        "subnet_id": instance.get("SubnetId"),
        "tags": tags,
        "warnings": warnings,
    }


def list_instances(session, region: str) -> list[dict]:
    ec2 = session.client("ec2", region_name=region)
    paginator = ec2.get_paginator("describe_instances")
    collected_at = datetime.now(timezone.utc)
    resources: list[dict] = []

    try:
        for page in paginator.paginate():
            for reservation in page.get("Reservations", []):
                for instance in reservation.get("Instances", []):
                    resources.append(
                        normalize_instance(
                            instance=instance,
                            region=region,
                            collected_at=collected_at,
                        )
                    )
    except ClientError as error:
        error_code = error.response.get("Error", {}).get(
            "Code",
            "UNKNOWN_AWS_ERROR",
        )
        raise EC2CollectionError(f"EC2 collection failed: {error_code}") from error

    return resources


def collect_ec2_inventory(region: str | None = None) -> dict:
    settings = get_settings()
    target_region = region or settings.aws_region
    ec2 = aws_client("ec2", region_name=target_region)
    paginator = ec2.get_paginator("describe_instances")
    collected_at = datetime.now(timezone.utc)
    resources: list[dict] = []

    try:
        for page in paginator.paginate():
            for reservation in page.get("Reservations", []):
                for instance in reservation.get("Instances", []):
                    resources.append(
                        normalize_instance(
                            instance=instance,
                            region=target_region,
                            collected_at=collected_at,
                        )
                    )
    except ClientError as error:
        error_code = error.response.get("Error", {}).get(
            "Code",
            "UNKNOWN_AWS_ERROR",
        )
        raise EC2CollectionError(f"EC2 collection failed: {error_code}") from error

    return {
        "status": "complete",
        "region": target_region,
        "resource_count": len(resources),
        "resources": resources,
    }

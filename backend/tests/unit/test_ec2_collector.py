from datetime import datetime, timezone

from app.services.collector.ec2 import (
    normalize_environment,
    normalize_instance,
    tags_to_dictionary,
)


def test_tags_to_dictionary():
    tags = [
        {
            "Key": "Name",
            "Value": "cloudcare-demo",
        },
        {
            "Key": "Environment",
            "Value": "dev",
        },
    ]

    result = tags_to_dictionary(tags)

    assert result == {
        "Name": "cloudcare-demo",
        "Environment": "dev",
    }


def test_environment_alias():
    tags = {
        "Environment": "DEV",
    }

    assert normalize_environment(tags) == "development"


def test_missing_environment_is_unknown():
    tags = {
        "Name": "cloudcare-demo",
    }

    assert normalize_environment(tags) == "unknown"


def test_normalize_instance():
    instance = {
        "InstanceId": "i-test123",
        "InstanceType": "t3.micro",
        "State": {
            "Name": "running",
        },
        "Placement": {
            "AvailabilityZone": "ap-south-1a",
        },
        "Tags": [
            {
                "Key": "Name",
                "Value": "cloudcare-demo",
            },
            {
                "Key": "Environment",
                "Value": "development",
            },
        ],
        "PrivateIpAddress": "10.0.0.10",
        "VpcId": "vpc-test",
        "SubnetId": "subnet-test",
    }

    result = normalize_instance(
        instance=instance,
        region="ap-south-1",
        collected_at=datetime.now(timezone.utc),
    )

    assert result["resource_id"] == "i-test123"
    assert result["name"] == "cloudcare-demo"
    assert result["environment"] == "development"
    assert result["state"] == "running"

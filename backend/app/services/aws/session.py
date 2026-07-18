from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

from app.core.config import Settings


class AWSAuthenticationError(Exception):
    """Raised when CloudCare cannot assume the configured AWS role."""


class AWSClientFactory:
    def __init__(self, settings: Settings):
        self.settings = settings

        self._assumed_session: boto3.Session | None = None
        self._expires_at: datetime | None = None

        self._botocore_config = Config(
            connect_timeout=5,
            read_timeout=20,
            retries={
                "max_attempts": 4,
                "mode": "standard",
            },
            user_agent_extra="CloudCare/1.0",
        )

    def _base_session(self) -> boto3.Session:
        if self.settings.aws_profile:
            return boto3.Session(
                profile_name=self.settings.aws_profile,
                region_name=self.settings.aws_region,
            )

        return boto3.Session(region_name=self.settings.aws_region)

    def _session_needs_refresh(self) -> bool:
        if self._assumed_session is None or self._expires_at is None:
            return True

        refresh_before = datetime.now(timezone.utc) + timedelta(minutes=5)

        return refresh_before >= self._expires_at

    def _assume_role(self) -> boto3.Session:
        base_session = self._base_session()

        sts = base_session.client(
            "sts",
            region_name=self.settings.aws_region,
            config=self._botocore_config,
        )

        try:
            response = sts.assume_role(
                RoleArn=self.settings.aws_role_arn,
                RoleSessionName="cloudcare-local-collector",
                ExternalId=self.settings.aws_external_id,
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

        credentials = response["Credentials"]

        self._expires_at = credentials["Expiration"]

        self._assumed_session = boto3.Session(
            aws_access_key_id=credentials["AccessKeyId"],
            aws_secret_access_key=credentials["SecretAccessKey"],
            aws_session_token=credentials["SessionToken"],
            region_name=self.settings.aws_region,
        )

        return self._assumed_session

    def session(self) -> boto3.Session:
        if self._session_needs_refresh():
            return self._assume_role()

        assert self._assumed_session is not None
        return self._assumed_session

    def client(
        self,
        service_name: str,
        region_name: str | None = None,
    ) -> Any:
        target_region = region_name or self.settings.aws_region

        if service_name == "ce":
            target_region = "us-east-1"

        return self.session().client(
            service_name,
            region_name=target_region,
            config=self._botocore_config,
        )

"""CloudWatch metrics collector."""

from datetime import datetime, timedelta, timezone
from typing import Any

from app.schemas.cloud_metrics import EC2CpuMetric


class CloudWatchCollector:
    def __init__(self, cloudwatch_client: Any, region: str) -> None:
        self.cloudwatch_client = cloudwatch_client
        self.region = region

    def collect_cpu_metrics(
        self,
        instance_ids: list[str],
        hours: int = 24,
    ) -> list[EC2CpuMetric]:
        if hours < 1:
            raise ValueError("hours must be at least 1")

        window_end = datetime.now(timezone.utc)
        window_start = window_end - timedelta(hours=hours)

        collected_metrics: list[EC2CpuMetric] = []

        for instance_id in instance_ids:
            if not instance_id:
                continue

            response = self.cloudwatch_client.get_metric_statistics(
                Namespace="AWS/EC2",
                MetricName="CPUUtilization",
                Dimensions=[
                    {
                        "Name": "InstanceId",
                        "Value": instance_id,
                    }
                ],
                StartTime=window_start,
                EndTime=window_end,
                Period=3600,
                Statistics=["Average", "Maximum"],
                Unit="Percent",
            )

            datapoints = sorted(
                response.get("Datapoints", []),
                key=lambda point: point["Timestamp"],
            )

            average_values = [
                float(point["Average"])
                for point in datapoints
                if "Average" in point
            ]

            maximum_values = [
                float(point["Maximum"])
                for point in datapoints
                if "Maximum" in point
            ]

            collected_metrics.append(
                EC2CpuMetric(
                    instance_id=instance_id,
                    region=self.region,
                    window_start=window_start,
                    window_end=window_end,
                    datapoint_count=len(datapoints),
                    average_cpu_percent=(
                        round(sum(average_values) / len(average_values), 4)
                        if average_values
                        else None
                    ),
                    maximum_cpu_percent=(
                        round(max(maximum_values), 4)
                        if maximum_values
                        else None
                    ),
                    latest_datapoint_at=(
                        datapoints[-1]["Timestamp"] if datapoints else None
                    ),
                )
            )

        return collected_metrics


def get_cpu_utilization(
    session,
    instance_id: str,
    region: str,
    days: int = 14,
) -> list[dict]:
    cloudwatch_client = session.client("cloudwatch", region_name=region)
    collector = CloudWatchCollector(
        cloudwatch_client=cloudwatch_client,
        region=region,
    )

    metrics = collector.collect_cpu_metrics(
        instance_ids=[instance_id],
        hours=days * 24,
    )

    return [metric.model_dump(mode="json") for metric in metrics]

"""
Deterministic detection rules — lifted from blueprint section 9.3.

Unlike most of app/services/, this file is NOT a placeholder — it's a real,
working, pure-Python rule (no AWS/DB dependency), so you can unit test it
immediately. Feed it real CloudWatch metrics once app/services/collector is
implemented and it'll work as-is.
"""

from dataclasses import dataclass


@dataclass
class MetricSample:
    cpu: float
    network_bytes: float


@dataclass
class Finding:
    rule_id: str
    severity: str
    confidence: float
    evidence: dict


def _percentile(values: list[float], pct: float) -> float:
    if not values:
        return 0.0
    values = sorted(values)
    k = (len(values) - 1) * (pct / 100)
    f, c = int(k), min(int(k) + 1, len(values) - 1)
    if f == c:
        return values[f]
    return values[f] + (values[c] - values[f]) * (k - f)


def classify_idle(metrics: list[MetricSample], tags: dict) -> Finding | None:
    if tags.get("cloudcare:exclude") == "true":
        return None
    if len(metrics) < 7:
        return None
    cpu_p95 = _percentile([m.cpu for m in metrics], 95)
    net_p95 = _percentile([m.network_bytes for m in metrics], 95)
    if cpu_p95 < 5 and net_p95 < 10_000_000:
        return Finding(
            rule_id="ec2.idle.v1",
            severity="medium",
            confidence=0.92,
            evidence={"cpu_p95": cpu_p95, "net_p95": net_p95},
        )
    return None


def classify_over_provisioned(metrics: list[MetricSample], tags: dict) -> Finding | None:
    if tags.get("cloudcare:exclude") == "true":
        return None
    if len(metrics) < 14:
        return None
    cpu_p95 = _percentile([m.cpu for m in metrics], 95)
    if cpu_p95 < 25:
        return Finding(
            rule_id="ec2.overprovisioned.v1",
            severity="low",
            confidence=0.8,
            evidence={"cpu_p95": cpu_p95},
        )
    return None

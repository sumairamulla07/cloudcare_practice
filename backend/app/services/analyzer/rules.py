"""
Deterministic detection rules — lifted from blueprint section 9.3.

Unlike most of app/services/, this file is NOT a placeholder — it's a real,
working, pure-Python rule (no AWS/DB dependency), so you can unit test it
immediately. Feed it real CloudWatch metrics once app/services/collector is
implemented and it'll work as-is.
"""

import math
from dataclasses import dataclass, field


@dataclass
class MetricSample:
    cpu: float
    network_bytes: float
    # hour-of-day (0-23) for the sample; used by nonprod schedule rule
    hour: int = 12


@dataclass
class EBSVolume:
    volume_id: str
    state: str  # "available" = unattached, "in-use" = attached


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


# ---------------------------------------------------------------------------
# Rule 3 — Unattached EBS volume  (blueprint §5.1, 24-h evidence window)
# ---------------------------------------------------------------------------

def classify_unattached_ebs(volume: EBSVolume, tags: dict) -> Finding | None:
    """Flag EBS volumes that are not attached to any instance (state == 'available').

    Evidence window: the volume must have been in 'available' state for at least
    24 hours — callers are expected to pass volumes that satisfy this window
    before calling this rule (the collector checks create/detach timestamps).
    """
    if tags.get("cloudcare:exclude") == "true":
        return None
    if volume.state != "available":
        return None
    return Finding(
        rule_id="ebs.unattached.v1",
        severity="low",
        confidence=0.95,
        evidence={"volume_id": volume.volume_id, "state": volume.state, "window_hours": 24},
    )


# ---------------------------------------------------------------------------
# Rule 4 — Non-prod off-hours schedule  (blueprint §5.1, 14-day window)
# ---------------------------------------------------------------------------

_OFF_HOURS = set(range(0, 8)) | set(range(18, 24))  # 18:00–08:00


def classify_nonprod_schedule(
    metrics: list[MetricSample],
    tags: dict,
    environment: str,
) -> Finding | None:
    """Recommend a start/stop schedule when a non-prod instance sits idle overnight.

    Condition: over a 14-day window the p95 CPU during off-hours (18:00–08:00)
    is ≤ 2 %, indicating the workload only runs during business hours.
    """
    if tags.get("cloudcare:exclude") == "true":
        return None
    if environment == "prod":
        return None
    if len(metrics) < 14:
        return None

    off_hour_cpus = [m.cpu for m in metrics if m.hour in _OFF_HOURS]
    if not off_hour_cpus:
        return None

    p95_off = _percentile(off_hour_cpus, 95)
    if p95_off <= 2.0:
        return Finding(
            rule_id="ec2.nonprod_schedule.v1",
            severity="low",
            confidence=0.85,
            evidence={
                "off_hours_cpu_p95": p95_off,
                "environment": environment,
                "window_days": 14,
            },
        )
    return None


# ---------------------------------------------------------------------------
# Rule 5 — Spend anomaly  (blueprint §5.1, daily/weekly, 14-day trailing mean)
# ---------------------------------------------------------------------------

def classify_spend_anomaly(daily_costs: list[float]) -> Finding | None:
    """Flag when today's cost exceeds the trailing 14-day mean by > 2 standard deviations.

    daily_costs: list of daily USD totals ordered oldest-first; the last element
    is the current day being evaluated.  At least 15 values are required (14
    baseline days + 1 current day).
    """
    if len(daily_costs) < 15:
        return None

    baseline = daily_costs[-15:-1]  # 14-day window excluding today
    today = daily_costs[-1]

    mean = sum(baseline) / len(baseline)
    variance = sum((x - mean) ** 2 for x in baseline) / len(baseline)
    std = math.sqrt(variance)

    if std < 0.01:
        # Near-zero variance: only flag if today is dramatically above the mean
        # (treat any day that is > 3× the mean as anomalous).
        if mean > 0 and today > mean * 3:
            return Finding(
                rule_id="cost.anomaly.v1",
                severity="high",
                confidence=0.90,
                evidence={
                    "today_usd": today,
                    "baseline_mean_usd": round(mean, 4),
                    "baseline_std_usd": 0.0,
                    "z_score": None,
                    "window_days": 14,
                },
            )
        return None

    z_score = (today - mean) / std
    if z_score > 2.0:
        return Finding(
            rule_id="cost.anomaly.v1",
            severity="high",
            confidence=min(0.5 + z_score * 0.1, 0.99),
            evidence={
                "today_usd": today,
                "baseline_mean_usd": round(mean, 4),
                "baseline_std_usd": round(std, 4),
                "z_score": round(z_score, 3),
                "window_days": 14,
            },
        )
    return None

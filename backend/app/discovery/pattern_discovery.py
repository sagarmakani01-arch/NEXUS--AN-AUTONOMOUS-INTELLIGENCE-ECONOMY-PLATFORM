import json
import logging
import math
import random

from app.discovery import persistence as db

logger = logging.getLogger("nexus.discovery.pattern")


async def discover_patterns(snapshot_data: list[dict]) -> list[dict]:
    discovered = []
    discovered.extend(await _correlation_analysis(snapshot_data))
    discovered.extend(await _trend_analysis(snapshot_data))
    discovered.extend(await _association_rule_mining(snapshot_data))
    return discovered


async def _correlation_analysis(snapshots: list[dict]) -> list[dict]:
    patterns = []
    metric_names = list(set(s.get("metric_name", "") for s in snapshots))

    for i in range(len(metric_names)):
        for j in range(i + 1, len(metric_names)):
            m1 = metric_names[i]
            m2 = metric_names[j]
            series1 = [s.get("metric_value", 0) for s in snapshots if s.get("metric_name") == m1]
            series2 = [s.get("metric_value", 0) for s in snapshots if s.get("metric_name") == m2]

            if len(series1) < 5 or len(series2) < 5:
                continue

            corr = _pearson_correlation(series1[: min(len(series1), len(series2))],
                                         series2[: min(len(series1), len(series2))])
            if abs(corr) > 0.5:
                pattern = await db.create_pattern(
                    pattern_type="correlation",
                    title=f"Correlation between {m1} and {m2}",
                    description=f"Strong {'positive' if corr > 0 else 'negative'} correlation (r={corr:.3f}) between {m1} and {m2}",
                    antecedent=m1,
                    consequent=m2,
                    confidence=abs(corr),
                    support=min(len(series1), len(series2)) / max(len(snapshots), 1),
                    lift=abs(corr) / (0.1 + 0.001),
                    sample_size=min(len(series1), len(series2)),
                    method="pearson_correlation",
                    tags=json.dumps(["correlation", m1, m2]),
                )
                patterns.append(pattern)
    return patterns


async def _trend_analysis(snapshots: list[dict]) -> list[dict]:
    patterns = []
    metric_groups: dict[str, list[float]] = {}
    for s in snapshots:
        name = s.get("metric_name", "")
        metric_groups.setdefault(name, []).append(s.get("metric_value", 0))

    for name, values in metric_groups.items():
        if len(values) < 10:
            continue
        slope = _linear_regression_slope(values)
        if abs(slope) > 0.02:
            trend_type = "upward" if slope > 0 else "downward"
            pattern = await db.create_pattern(
                pattern_type="trend",
                title=f"{trend_type.capitalize()} trend in {name}",
                description=f"{name} shows a significant {trend_type} trend over time (slope={slope:.4f})",
                antecedent=name,
                consequent=trend_type,
                confidence=min(1.0, abs(slope) * 10),
                support=len(values) / 100,
                lift=1.0,
                sample_size=len(values),
                method="linear_regression",
                tags=json.dumps(["trend", name, trend_type]),
            )
            patterns.append(pattern)
    return patterns


async def _association_rule_mining(snapshots: list[dict]) -> list[dict]:
    patterns = []
    civilization_ids = list(set(s.get("civilization_id") for s in snapshots if s.get("civilization_id")))
    if len(civilization_ids) < 3:
        return patterns

    for _ in range(3):
        civ_a, civ_b = random.sample(civilization_ids, 2)
        a_snaps = [s for s in snapshots if s.get("civilization_id") == civ_a]
        b_snaps = [s for s in snapshots if s.get("civilization_id") == civ_b]

        a_metrics = {s.get("metric_name"): s.get("metric_value", 0) for s in a_snaps[-10:]}
        b_metrics = {s.get("metric_name"): s.get("metric_value", 0) for s in b_snaps[-10:]}

        common = set(a_metrics.keys()) & set(b_metrics.keys())
        for m in common:
            diff = abs(a_metrics.get(m, 0) - b_metrics.get(m, 0))
            if diff > 0.3:
                pattern = await db.create_pattern(
                    pattern_type="association",
                    title=f"Divergence in {m} between civilizations",
                    description=f"Civilizations {civ_a[:8]} and {civ_b[:8]} show significant divergence in {m} (diff={diff:.3f})",
                    antecedent=civ_a,
                    consequent=civ_b,
                    confidence=1.0 - diff,
                    support=0.5,
                    lift=diff * 2,
                    sample_size=len(common),
                    method="association_rule",
                    tags=json.dumps(["association", "civilization", m]),
                )
                patterns.append(pattern)
    return patterns


def _pearson_correlation(x: list[float], y: list[float]) -> float:
    n = len(x)
    if n < 3:
        return 0.0
    mean_x = sum(x) / n
    mean_y = sum(y) / n
    num = sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(x, y))
    den = math.sqrt(sum((xi - mean_x) ** 2 for xi in x) * sum((yi - mean_y) ** 2 for yi in y))
    return num / (den + 0.0001)


def _linear_regression_slope(values: list[float]) -> float:
    n = len(values)
    x_vals = list(range(n))
    mean_x = sum(x_vals) / n
    mean_y = sum(values) / n
    num = sum((x - mean_x) * (y - mean_y) for x, y in zip(x_vals, values))
    den = sum((x - mean_x) ** 2 for x in x_vals)
    return num / (den + 0.0001)

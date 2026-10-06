"""The database, as a sense: Atlas metrics from Bronto's metrics API.

Atlas pushes its cluster metrics to Bronto through the OTel Metrics Sink.
Bronto's MCP server reads logs and traces but not metrics, so these two
tools call the REST API directly (docs.bronto.io/api-reference/timeseries),
with the same read-only key the MCP server uses.

Answers are kept small on purpose: a few dozen points and a summary, not the
raw series, so a 2-hour window doesn't flood the model's context.
"""

import os
from datetime import datetime, timezone

import httpx2
from strands import tool

API = os.environ.get("BRONTO_API_URL", "https://api.eu.bronto.io")
PREFIX = os.environ.get("ATLAS_METRIC_PREFIX", "mongodb")


def _headers() -> dict:
    return {"X-BRONTO-API-KEY": os.environ["BRONTO_API_KEY"]}


@tool
def list_atlas_metrics(contains: str = "") -> list[dict]:
    """List the MongoDB Atlas metrics available in Bronto: name, type, unit, description.

    Call this first to find the exact metric names to query.

    Args:
        contains: optional text the metric name must contain, e.g. "query", "opcounter", "latency", "cpu".
    """
    r = httpx2.get(f"{API}/metrics", headers=_headers(), timeout=30)
    r.raise_for_status()
    return [
        {k: m.get(k) for k in ("metric_name", "type", "unit", "description") if m.get(k)}
        for m in r.json().get("metrics", [])
        if m["metric_name"].startswith(PREFIX) and contains.lower() in m["metric_name"].lower()
    ]


@tool
def query_atlas_metrics(
    metric: str,
    time_range: str = "Last 60 minutes",
    aggregation: str = "avg",
    group_by: str = "",
    where: str = "",
    points: int = 30,
) -> dict:
    """Get one Atlas metric over time, to compare a quiet baseline with the incident window.

    Args:
        metric: exact metric name from list_atlas_metrics.
        time_range: natural language, e.g. "Last 60 minutes", "Last 3 hours".
        aggregation: avg, max, min, sum, p95, p99 or rate.
        group_by: optional attribute to split by, e.g. "host" or "process".
        where: optional filter on metric attributes, e.g. "host = 'shard-00-01'".
        points: how many time buckets to return (max 120).
    """
    body = {
        "time_range": {"natural": time_range},
        "num_of_slices": max(1, min(points, 120)),
        "queries": [{
            "name": "m",
            "select": [metric],
            "from_expr": f"metric_name = '{metric}'",
            "where": where,
            "groups": [group_by] if group_by else [],
            "aggregation": [{"time": aggregation}],
        }],
    }
    r = httpx2.post(f"{API}/timeseries/search", headers=_headers(), json=body, timeout=60)
    if r.status_code >= 400:
        return {"error": r.status_code, "details": r.text[:500]}
    result = r.json().get("m", {})
    out = {"metric": metric, "aggregation": aggregation, "time_range": time_range}
    if result.get("series"):
        out["series"] = _compact(result["series"])
    if result.get("groups_series"):
        out["groups"] = [  # "key" is the attribute grouped by, "name" its value
            {group_by: g.get("name") or "(not set)", "series": _compact(g.get("timeseries", []))}
            for g in result["groups_series"][:10]
        ]
    return out


def _compact(series: list[dict]) -> dict:
    pts = [  # Bronto sends numbers as strings
        (datetime.fromtimestamp(int(s["@timestamp"]) / 1000, timezone.utc).strftime("%d %b %H:%M"), float(s["value"]))
        for s in series if s.get("value") is not None
    ]
    values = [v for _, v in pts]
    if not values:
        return {"points": [], "note": "no data in this window"}
    return {
        "points": [f"{t} {v:.4g}" for t, v in pts],
        "min": round(min(values), 4),
        "max": round(max(values), 4),
        "first": round(values[0], 4),
        "last": round(values[-1], 4),
    }

#!/usr/bin/env python3
"""Create the "LLM KPIs — Storefront Assistant" dashboard in Bronto.

Everything except the cost widget is built from the agent's standard
OpenTelemetry GenAI spans (the .traces dataset), not from custom logging.
Datasets are referenced with from_expr, so the same script works in any org
that receives the lab's telemetry.

    BRONTO_API_KEY=... python3 dashboard/create_dashboard.py            # create
    BRONTO_API_KEY=... python3 dashboard/create_dashboard.py --delete   # remove what it created
    BRONTO_API_KEY=... python3 dashboard/create_dashboard.py --check    # print each widget's latest values

The key needs dashboard write access (an ingestion-only key gets a 403).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

BASE_URL = os.environ.get("BRONTO_API_URL", "https://api.eu.bronto.io")
NAME = "LLM KPIs — Storefront Assistant"
STATE = Path(os.environ.get("DASHBOARD_STATE", Path(__file__).with_name("state.json")))

TRACES = "\"collection\" = '.traces' AND \"dataset\" = 'storefront-assistant'"
LOGS = "\"collection\" = 'aws-ai-workshop' AND \"dataset\" = 'storefront-assistant'"

AGENT = "\"$gen_ai.operation.name\" = 'invoke_agent' AND \"$gen_ai.agent.name\" = 'storefront_assistant'"
# Strands and the Botocore instrumentation each emit a `chat` span for the same
# Bedrock call. Count the Strands one (it carries time-to-first-token) or every
# token total doubles.
CHAT = "\"$gen_ai.operation.name\" = 'chat' AND \"$gen_ai.provider.name\" = 'strands-agents'"
# ...but only the Botocore span carries finish_reasons.
BEDROCK_CALL = "\"$gen_ai.operation.name\" = 'chat' AND \"$rpc.system\" = 'aws-api'"
TOOL = "\"$gen_ai.operation.name\" = 'execute_tool'"
NS_TO_MS = {"type": "time", "input": "nanoseconds", "output": "milliseconds"}
MS = {"type": "time", "input": "milliseconds", "output": "milliseconds"}


def q(name, select, source, where="", groups=None, agg="count", reduce_to="sum", unit=None):
    query = {
        "name": name,
        "select": [select],
        "from_expr": source,
        "where": where,
        "aggregation": [{"time": agg, "reduce_to": reduce_to}],
    }
    if groups:
        query["groups"] = groups
    if unit:
        query["unit_config"] = unit
    return query


# (widget title, widget type, description, query) in dashboard order, 3 per row.
WIDGETS = [
    ("Agent requests", "line", "Customer questions answered (one invoke_agent span each).",
     q("requests", "*", TRACES, AGENT)),
    ("End-to-end latency P95", "line", "invoke_agent span duration: what the customer waits for, tools and all.",
     q("latency_p95", "$span.duration_nano", TRACES, AGENT, agg="p95", reduce_to="max", unit=NS_TO_MS)),
    ("Estimated spend (USD)", "line", "Tokens x list price. An estimate: the GenAI conventions count tokens, not dollars.",
     q("cost", "$cost_usd_estimate", LOGS, "\"$event.name\" = 'agent.invocation'", agg="sum")),

    ("Input tokens by model", "line", "Prompt tokens per model call. Tool results and history make this grow with every loop.",
     q("input_tokens", "$gen_ai.usage.input_tokens", TRACES, CHAT, ["$gen_ai.request.model"], agg="sum")),
    ("Output tokens by model", "line", "Generated tokens per model: the expensive side of the bill.",
     q("output_tokens", "$gen_ai.usage.output_tokens", TRACES, CHAT, ["$gen_ai.request.model"], agg="sum")),
    ("Time to first token P95", "line", "gen_ai.server.time_to_first_token on chat spans, per model.",
     q("ttft_p95", "$gen_ai.server.time_to_first_token", TRACES, CHAT, ["$gen_ai.request.model"], agg="p95", reduce_to="max", unit=MS)),

    ("Model call latency P95 by model", "line", "One chat span per Bedrock call.",
     q("chat_p95", "$span.duration_nano", TRACES, CHAT, ["$gen_ai.request.model"], agg="p95", reduce_to="max", unit=NS_TO_MS)),
    ("Model calls per question", "bar", "Agent-loop cycles per request. More tools, more loops, more tokens.",
     q("model_calls", "$model_calls", LOGS, "\"$event.name\" = 'agent.invocation'", ["$gen_ai.request.model"], agg="avg", reduce_to="avg")),
    ("Tokens by agent", "bar", "Main agent vs the product_researcher sub-agent (step 3).",
     q("agent_tokens", "$gen_ai.usage.total_tokens", TRACES, "\"$gen_ai.operation.name\" = 'invoke_agent'", ["$gen_ai.agent.name"], agg="sum")),

    ("Tool calls by tool", "top-list", "execute_tool spans. Strands emits these because it runs the tool; Bedrock alone cannot.",
     q("tool_calls", "*", TRACES, TOOL, ["$gen_ai.tool.name"])),
    ("Tool errors", "bar", "execute_tool spans with gen_ai.tool.status = error.",
     q("tool_errors", "*", TRACES, TOOL + " AND \"$gen_ai.tool.status\" = 'error'", ["$gen_ai.tool.name"])),
    ("Finish reasons", "pie", "Why each model call stopped: tool_use, end_turn, or max_tokens (truncated).",
     q("finish", "*", TRACES, BEDROCK_CALL, ["\"$gen_ai.response.finish_reasons.0\""])),

    ("Tokens by attendee", "top-list", "Who in the room is spending the most tokens.",
     q("attendee_tokens", "$gen_ai.usage.total_tokens", TRACES, CHAT, ["$attendee"], agg="sum")),
]


class API:
    def __init__(self, key: str):
        self.key = key

    def __call__(self, method: str, path: str, body: Any = None) -> tuple[int, Any]:
        req = urllib.request.Request(
            BASE_URL + path, method=method,
            data=json.dumps(body).encode() if body is not None else None,
            headers={"X-BRONTO-API-KEY": self.key, "Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                raw = r.read().decode()
                return r.status, json.loads(raw) if raw.strip() else {}
        except urllib.error.HTTPError as e:
            raw = e.read().decode()
            try:
                return e.code, json.loads(raw)
            except json.JSONDecodeError:
                return e.code, raw


def need(status, expected, what, resp):
    if status not in (expected if isinstance(expected, tuple) else (expected,)):
        raise SystemExit(f"{what}: HTTP {status}: {resp}")
    return resp


def load() -> dict:
    return json.loads(STATE.read_text()) if STATE.exists() else {"metrics": [], "widgets": [], "dashboard": None}


def save(state: dict) -> None:
    STATE.write_text(json.dumps(state, indent=2) + "\n")


def delete(api: API) -> None:
    state = load()
    if state["dashboard"]:
        print("dashboard", api("DELETE", f"/dashboards/{state['dashboard']}")[0])
    for w in state["widgets"]:
        print("widget   ", api("DELETE", f"/widgets/{w}")[0])
    for m in state["metrics"]:
        print("metric   ", api("DELETE", f"/metrics/definitions/{m}")[0])
    STATE.unlink(missing_ok=True)


def check(api: API) -> None:
    state = load()
    params = urllib.parse.urlencode({"time_range": "Last 6 hours", "num_of_slices": 6})
    for (title, *_), metric_id in zip(WIDGETS, state["metrics"]):
        status, resp = api("GET", f"/timeseries/{metric_id}?{params}")
        print(f"{status}  {title:34} {json.dumps(resp)[:150]}")


def create(api: API) -> None:
    status, who = api("GET", "/customer")
    need(status, 200, "identify account", who)
    print(f"org: {who.get('customer_name')} ({who.get('email')})")
    if STATE.exists():
        raise SystemExit(f"{STATE} exists: run --delete first, or remove it if the dashboard is already gone")

    state = load()
    try:
        for title, kind, desc, query in WIDGETS:
            status, metric = api("POST", "/metrics/definitions", {"name": f"Track A — {title}", "description": desc, "queries": [query]})
            need(status, 201, f"metric {title}", metric)
            state["metrics"].append(metric["id"])
            status, widget = api("POST", "/widgets", {"name": title, "description": desc, "type": kind, "metric_ids": [metric["id"]]})
            need(status, 201, f"widget {title}", widget)
            state["widgets"].append(widget["id"])
            save(state)
            print(f"  + {title}")

        status, dash = api("POST", "/dashboards", {"name": NAME})
        need(status, 201, "dashboard", dash)
        state["dashboard"] = dash["id"]
        save(state)

        status, resp = api("POST", f"/dashboards/{dash['id']}/widgets", {"widget_ids": state["widgets"]})
        need(status, (200, 201, 204), "attach widgets", resp)

        cols = 3
        layout = [{"id": w, "x": (i % cols) / cols, "y": (i // cols) * 7.0, "w": 1 / cols, "h": 7.0}
                  for i, w in enumerate(state["widgets"])]
        status, resp = api("PATCH", f"/dashboards/{dash['id']}", {"layout": {"widget_layouts": layout}})
        need(status, (200, 204), "layout", resp)
    except SystemExit:
        save(state)
        print(f"partial state saved to {STATE}; run --delete to clean up", file=sys.stderr)
        raise

    host = BASE_URL.replace("api.", "app.")
    print(f"\n{NAME}\n{host}/dashboards/{state['dashboard']}")


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--delete", action="store_true")
    p.add_argument("--check", action="store_true")
    args = p.parse_args()
    key = os.environ.get("BRONTO_API_KEY", "").strip()
    if not key:
        raise SystemExit("set BRONTO_API_KEY (a key with dashboard write access)")
    api = API(key)
    delete(api) if args.delete else check(api) if args.check else create(api)


if __name__ == "__main__":
    main()

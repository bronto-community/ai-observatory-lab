"""Storefront assistant: the agent under observation in Track A.

One image, three steps, picked with AGENT_STEP:
  1  a model behind an endpoint, no tools
  2  + three back-office tools (one of them flaky)
  3  + a product_researcher sub-agent, called as a tool

Same shape as AgentCore expects: POST /invocations, GET /ping on :8080.
"""

from telemetry import ATTENDEE, setup_telemetry

setup_telemetry()

import logging
import os
import time

from bedrock_agentcore import BedrockAgentCoreApp
from strands import Agent, tool

from llm import MODEL_ID, PROVIDER, PROVIDER_NAMES, REGION, estimated_cost, model
from tools import STEP_2_TOOLS, check_inventory

STEP = int(os.environ.get("AGENT_STEP", "1"))
log = logging.getLogger("storefront-assistant")
app = BedrockAgentCoreApp()

SYSTEM_PROMPT = """You are the customer assistant for Storefront, a small online kitchenware shop.
Answer customers briefly and politely. Use your tools for anything about orders, stock or shipping;
never guess an order status or stock level. If a tool fails, say what you could not check."""

RESEARCHER_PROMPT = """You are Storefront's product researcher. Given a product a customer wants,
check stock and suggest up to two in-stock alternatives from the catalogue with one line on why.
Catalogue: blue ceramic mug, espresso cups, walnut cutting board, linen apron, cast iron skillet, french press."""

_sub_usage = {"input": 0, "output": 0, "calls": 0}


# #region researcher
@tool
def product_researcher(request: str) -> str:
    """Hand a product question to the research sub-agent: stock plus in-stock alternatives."""
    researcher = Agent(
        name="product_researcher",
        model=model(os.environ.get("RESEARCHER_MODEL_ID", MODEL_ID)),
        system_prompt=RESEARCHER_PROMPT,
        tools=[check_inventory],
        callback_handler=None,
    )
    result = researcher(request)
    usage = result.metrics.accumulated_usage
    _sub_usage["input"] += usage.get("inputTokens", 0)
    _sub_usage["output"] += usage.get("outputTokens", 0)
    _sub_usage["calls"] += 1
    return str(result)
# #endregion researcher


def tools_for(step: int) -> list:
    if step <= 1:
        return []
    if step == 2:
        return STEP_2_TOOLS
    return STEP_2_TOOLS + [product_researcher]


@app.entrypoint
def invoke(payload: dict) -> dict:
    prompt = payload.get("prompt", "Hello!")
    model_id = payload.get("model", MODEL_ID)
    _sub_usage.update(input=0, output=0, calls=0)

# #region agent
    agent = Agent(
        name="storefront_assistant",
        model=model(model_id),
        system_prompt=SYSTEM_PROMPT,
        tools=tools_for(STEP),
        callback_handler=None,
        trace_attributes={"attendee": ATTENDEE, "lab.step": STEP},
    )
# #endregion agent

    started = time.perf_counter()
    status = "ok"
    try:
        result = agent(prompt)
        answer = str(result).strip()
    except Exception as e:  # a failed model call is data too
        status, answer, result = "error", f"{type(e).__name__}: {e}", None
    latency_ms = round((time.perf_counter() - started) * 1000)

    m = result.metrics if result else None
    usage = m.accumulated_usage if m else {}
    tokens_in = usage.get("inputTokens", 0) + _sub_usage["input"]
    tokens_out = usage.get("outputTokens", 0) + _sub_usage["output"]
    tool_calls = sum(t.call_count for t in m.tool_metrics.values()) if m else 0
    tool_errors = sum(t.error_count for t in m.tool_metrics.values()) if m else 0
    failed_tools = sorted(name for name, t in m.tool_metrics.items() if t.error_count) if m else []

    # One structured event per request: the row every dashboard widget reads.
    summary = {
        "event.name": "agent.invocation",
        "attendee": ATTENDEE,
        "lab.step": STEP,
        "status": status,
        "gen_ai.provider.name": PROVIDER_NAMES[PROVIDER],
        "gen_ai.operation.name": "invoke_agent",
        "gen_ai.agent.name": "storefront_assistant",
        "gen_ai.request.model": model_id,
        "gen_ai.usage.input_tokens": tokens_in,
        "gen_ai.usage.output_tokens": tokens_out,
        "gen_ai.usage.total_tokens": tokens_in + tokens_out,
        "latency_ms": latency_ms,
        "model_calls": m.cycle_count if m else 0,
        "tool_calls": tool_calls,
        "tool_errors": tool_errors,
        "subagent_calls": _sub_usage["calls"],
        "cost_usd_estimate": estimated_cost(model_id, tokens_in, tokens_out),
        "stop_reason": str(getattr(result, "stop_reason", "")) if result else "error",
        # The conversation, as searchable fields (content capture: treat as sensitive).
        "gen_ai.input.messages": prompt,
        "gen_ai.output.messages": answer,
        "tools.failed": ",".join(failed_tools),
    }
    # OTel log attributes can't be None: leave the cost out when there's no list price.
    log.info("agent.invocation", extra={k: v for k, v in summary.items() if v is not None})

    return {"result": answer, "stats": {k: summary[k] for k in (
        "gen_ai.request.model", "gen_ai.usage.input_tokens", "gen_ai.usage.output_tokens",
        "latency_ms", "model_calls", "tool_calls", "tool_errors", "subagent_calls", "cost_usd_estimate")}}


if __name__ == "__main__":
    where = f" in {REGION}" if PROVIDER == "bedrock" else ""
    print(f"Storefront assistant, step {STEP}, {PROVIDER}: {MODEL_ID}{where}, attendee={ATTENDEE}", flush=True)
    print("""Try: curl -s localhost:8080/invocations -d '{"prompt": "Where is order 1042?"}'""", flush=True)
    app.run()

"""An AI SRE for Storefront, built up in six steps, picked with AGENT_STEP:

  1  the loop + an identity   a model behind an endpoint, with prompts/*.md as its system prompt
  2  traced                   its own model and tool calls, as OpenTelemetry spans in your Bronto
  3  eyes                     Bronto MCP: Storefront's logs and traces in the shared demo org
  4  the database             a tool for Atlas metrics (Bronto MCP reads logs and traces, not metrics)
  5  a mouth                  the answer is filed as a GitHub issue
  6  the code                 GitHub MCP: Storefront's source, commits and releases

Every step keeps what the earlier ones added. POST /invocations {"prompt": ...} on :8080.
"""

import os
import re
from pathlib import Path

STEP = int(os.environ.get("AGENT_STEP", "1"))

# #region trace
# Traced: Strands already emits OpenTelemetry GenAI spans for every agent loop,
# model call and tool call. All it needs is somewhere to send them: your own
# Bronto, with your ingestion key in OTEL_EXPORTER_OTLP_HEADERS.
if STEP >= 2 and os.environ.get("OTEL_EXPORTER_OTLP_HEADERS"):
    region = os.environ.get("BRONTO_REGION", "eu").strip().lower() or "eu"
    os.environ.setdefault("OTEL_EXPORTER_OTLP_ENDPOINT", f"https://ingestion.{region}.bronto.io")
    from strands.telemetry import StrandsTelemetry
    StrandsTelemetry().setup_otlp_exporter()
# #endregion trace

import httpx2
from bedrock_agentcore import BedrockAgentCoreApp
from mcp.client.streamable_http import streamable_http_client
from strands import Agent
from strands.tools.mcp import MCPClient

from llm import model

app = BedrockAgentCoreApp()

# #region identity
# The identity: every prompts/*.md file becomes part of the system prompt,
# including the my.md you mount in. Files for later steps are skipped.
LATER = {"db.md": 4, "report.md": 5, "code.md": 6}
ORDER = ["role.md", "rules.md", "db.md", "code.md", "report.md"]  # then anything else, my.md last


def system_prompt() -> str:
    files = sorted(Path("prompts").glob("*.md"),
                   key=lambda p: (ORDER.index(p.name) if p.name in ORDER else len(ORDER), p.name == "my.md", p.name))
    return "\n\n".join(p.read_text() for p in files if STEP >= LATER.get(p.name, 1))
# #endregion identity

# #region eyes
# The eyes: Bronto's MCP server, on the shared demo org where Storefront runs.
# Its tools (list datasets, search logs and traces, ...) become the agent's tools.
bronto = MCPClient(lambda: streamable_http_client(
    os.environ.get("BRONTO_MCP_URL", "https://mcp.eu.bronto.io/mcp"),
    http_client=httpx2.AsyncClient(headers={"X-BRONTO-API-KEY": os.environ["BRONTO_API_KEY"]}, timeout=60),
))
# #endregion eyes

# #region code
# The code: GitHub's MCP server, read-only repository tools (files, commits, releases).
github = MCPClient(lambda: streamable_http_client(
    os.environ.get("GITHUB_MCP_URL", "https://api.githubcopilot.com/mcp/x/repos/readonly"),
    http_client=httpx2.AsyncClient(headers={"Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}"}, timeout=60),
))
# #endregion code


def tools() -> list:
    found = []
    if STEP >= 3:
        found.append(bronto)
    if STEP >= 4:
        from atlas_metrics import list_atlas_metrics, query_atlas_metrics
        found += [list_atlas_metrics, query_atlas_metrics]
    if STEP >= 6:
        found.append(github)
    return found


# #region mouth
# The mouth: the hypothesis goes where humans already look, as a GitHub issue.
def file_issue(question: str, hypothesis: str) -> str:
    r = httpx2.post(
        f"https://api.github.com/repos/{os.environ['GITHUB_REPO']}/issues",
        headers={"Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}"},
        json={"title": f"[investigation] {question}"[:120], "body": hypothesis},
        timeout=30,
    )
    r.raise_for_status()
    return r.json()["html_url"]
# #endregion mouth


def answer(result, reasoning: bool) -> str:
    """Some models write their reasoning into the answer. Drop it unless asked."""
    text = str(result).strip()
    if reasoning or not text.startswith("<reasoning>"):
        return text
    if re.search(r"</(reasoning|analysis)>?", text):
        return re.sub(r"(?s)^.*</(reasoning|analysis)>?", "", text).strip()
    m = re.search(r"(?m)^(\*\*|#|\|)", text)
    return text[m.start():].strip() if m else text


# #region agent
@app.entrypoint
def invoke(payload: dict) -> dict:
    question = payload.get("prompt", "Hello!")
    agent = Agent(
        model=model(max_tokens=4096),
        system_prompt=system_prompt(),
        tools=tools(),
        trace_attributes={"attendee": os.environ.get("ATTENDEE", "anonymous"), "agent.step": STEP},
    )
    hypothesis = answer(agent(question), payload.get("reasoning", False))
    if STEP >= 5:
        return {"result": file_issue(question, hypothesis)}
    return {"result": hypothesis}
# #endregion agent


if __name__ == "__main__":
    print(f"Step {STEP} agent running on :8080. Ask it with: curl -s localhost:8080/invocations -d '{{\"prompt\": \"Who are you?\"}}'", flush=True)
    app.run()

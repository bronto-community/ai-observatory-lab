# The lab's AI SRE

`ghcr.io/bronto-community/mongodb-lab-agent` is a small Strands agent behind an
AgentCore-style endpoint (`POST /invocations` on :8080). One image, six steps,
picked with `AGENT_STEP=1..6`; see the docstring at the top of `agent.py`.

| File | What it does |
|---|---|
| `agent.py` | The loop, identity, tracing, eyes (Bronto MCP), mouth (GitHub issue), code (GitHub MCP) |
| `atlas_metrics.py` | Step 4: Atlas metrics from Bronto's metrics API (MCP reads logs and traces, not metrics) |
| `prompts/*.md` | The system prompt. `db.md`, `report.md` and `code.md` switch on at steps 4, 5 and 6 |
| `../../agent/llm.py` | Shared with Track A: `LLM_PROVIDER` picks Gemini (default), OpenAI, Anthropic or Bedrock |

Build and publish, from the repo root:

```bash
docker buildx build --platform linux/amd64,linux/arm64 -f mongodb-dublin/agent/Dockerfile -t ghcr.io/bronto-community/mongodb-lab-agent --push .
```

Environment (all in the attendee's `.env`):

| Variable | Step | What |
|---|---|---|
| `GEMINI_API_KEY` | 1 | Or `LLM_PROVIDER` plus that provider's key |
| `OTEL_EXPORTER_OTLP_HEADERS=x-bronto-api-key=…`, `BRONTO_REGION`, `ATTENDEE` | 2 | Your own Bronto ingestion key; your agent's traces go there |
| `BRONTO_API_KEY` | 3 | The shared demo org's public read-only key (MCP and the metrics API) |
| `GITHUB_REPO`, `GITHUB_TOKEN` | 5 | Your `ai-sre-issues` repo and a token with Issues: read and write |

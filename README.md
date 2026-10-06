# AI Observatory: self-paced labs

A talk and two hands-on labs from the AWS + Bronto evening "An Evening at the AI Observatory", in a form you can
run on your own. The guide is the website, and this repository is everything behind it:

**→ [ai-observatory-lab.vercel.app](https://ai-observatory-lab.vercel.app)**

| Session | What it covers | You come away with |
|---|---|---|
| [Intro talk](https://ai-observatory-lab.vercel.app/intro) · 25 min | Observability for AI and AI for observability; the OpenTelemetry GenAI conventions | A shared vocabulary for the two labs |
| [Track A: Observability for AI](https://ai-observatory-lab.vercel.app/track-a) · about 40 min | Run a Strands agent in Docker and read its GenAI traces in Bronto: tokens, tool calls, a failing tool, a sub-agent, two models | An LLM KPI dashboard in your own Bronto, and knowing where to look in a trace |
| [Track B: AI for Observability](https://ai-observatory-lab.vercel.app/track-b) · about 45 min, by Severin Neumann | Build an AI SRE in seven steps, with Bronto MCP and GitHub, against a live incident | An agent that files a GitHub issue with its hypothesis and evidence |
| [MongoDB Dublin: AI observability, from the model call to the database](https://ai-observatory-lab.vercel.app/dublin) · 20 min talk + 75 min build | Trace an AI SRE into your own Bronto, connect Storefront's traces with MongoDB Atlas metrics and slow-query logs, and find a database-rooted incident's cause | An agent that names the slow query and the commit behind it ([`mongodb-dublin/`](mongodb-dublin/)) |

## What you need

- **Your own Bronto account**, EU or US: a [trial](https://bronto.io/signup) (no credit card) or an existing one,
  with an ingestion key and a key that can create dashboards. Track A sends everything here. Track B doesn't use
  it: its agent reads a shared Bronto demo org with a public read-only key the guide provides.
- **An LLM**, one of:
  - an **AWS account** for Amazon Bedrock, in any region with the lab's models (`us-west-2` by default), plus the
    **AWS CLI v2**; or
  - **your own API key** from Google Gemini, OpenAI or Anthropic. No key? Gemini's
    [free tier](https://ai.google.dev/gemini-api/docs/billing) covers both labs.
- **Docker**: every agent runs as a container. macOS, Linux and Windows (PowerShell) all work.
- For Track B: a **GitHub** account, an empty public repository and a fine-grained token.

Start at [Start here](https://ai-observatory-lab.vercel.app/start): pick your setup, and every command on the site
follows it.

## Quick start (Track A, own Gemini key, macOS / Linux)

```bash
mkdir ai-observatory && cd ai-observatory
cat > .env <<'EOF'
LLM_PROVIDER=gemini
GEMINI_API_KEY=YOUR-GEMINI-KEY
BRONTO_REGION=eu
OTEL_EXPORTER_OTLP_HEADERS=x-bronto-api-key=YOUR-BRONTO-INGESTION-KEY
ATTENDEE=yourname
EOF
```

```bash
docker run --rm --env-file .env ghcr.io/bronto-community/track-a-agent python doctor.py
```

```bash
docker run --rm -p 8080:8080 --env-file .env -e AGENT_STEP=1 ghcr.io/bronto-community/track-a-agent
```

Then, in a second terminal:

```bash
curl -s localhost:8080/invocations -d '{"prompt": "Where is order 1042 and when will it arrive?"}'
```

The full guide, with the AWS route, Windows commands and every step, is on the
[website](https://ai-observatory-lab.vercel.app/track-a).

## What's in this repository

| Path | What it is |
|---|---|
| [`site/`](site) | The website (Next.js, static). `cd site && npm install && npm run dev` |
| [`agent/`](agent) | The Track A agent (Strands), its tools, telemetry setup, `doctor.py` and `traffic.py`. Published as `ghcr.io/bronto-community/track-a-agent` |
| [`agent/llm.py`](agent/llm.py) | Picks the model: Bedrock, or Gemini / OpenAI / Anthropic with `LLM_PROVIDER` |
| [`dashboard/`](dashboard) | Builds the "LLM KPIs — Storefront Assistant" dashboard in your Bronto |
| [`track-b/`](track-b) | Severin's Track B agent images, unchanged, plus the same provider switch. Published as `ghcr.io/bronto-community/track-b-agent:step-N` |
| [`infra/track-b-harness/`](infra/track-b-harness) | How the always-on Track B incident is hosted (one small EC2 instance; the incident itself is not in this repo) |
| [`slides/`](slides) | The Track A deck (Slidev), published at [observability-for-ai-lab.vercel.app](https://observability-for-ai-lab.vercel.app) |
| [`iam/least-privilege.json`](iam/least-privilege.json) | An IAM policy for running Track A in your own AWS account |
| [`docs/live-evening.md`](docs/live-evening.md) | Track A as it ran on the night, with AWS workshop accounts |
| [`mongodb-dublin/`](mongodb-dublin) | The MongoDB Dublin talk and lab: its deck, its own AI SRE agent (`ghcr.io/bronto-community/mongodb-lab-agent`), the Mongo-backed Storefront and its incident harness |

The other two decks are Severin Neumann's:
[intro talk](https://ai-observatory-talk.vercel.app) and [Track B](https://aisre-lab.vercel.app).

Telemetry follows Bronto's [AgentCore guide](https://docs.bronto.io/ai-features/aws-agentcore) and the
[OpenTelemetry GenAI semantic conventions](https://opentelemetry.io/docs/specs/semconv/gen-ai/).

# Track A: Observability for AI

A small customer-assistant agent (Strands on Amazon Bedrock) that sends its
OpenTelemetry traces, logs and metrics to Bronto. You run it in Docker, ask
it questions, and read what it did: model calls, tokens, tool calls, a
failing tool, a sub-agent.

Slides: <https://observability-for-ai-lab.vercel.app> · This guide as a web page: <https://observability-for-ai-lab.vercel.app/lab>

## Run it

You need Docker and AWS credentials that can call Bedrock. Pick your shell:

- **macOS, Linux, or Windows with WSL**: the bash/zsh commands below. The workshop slides use these.
- **Windows without WSL**: the PowerShell commands after them.

Everything else (the image, the steps, what you see in Bronto) is identical.

The `.env` examples below already contain the **shared workshop ingestion key**
for tonight's Bronto org. It can only send data in; it can't read anything,
and it's revoked after the event. Using your own Bronto account instead? See
[Your own Bronto account](#your-own-bronto-account).

### macOS and Linux (bash, zsh), and Windows under WSL

1. **Credentials.** On the workshop page choose **Get AWS CLI credentials**,
   copy the block for macOS / Linux (the lines start with `export AWS_…`), and
   paste it into the terminal you'll run Docker from.

2. **A folder and a `.env` file.**

   ```bash
   mkdir track-a && cd track-a
   cat > .env <<'EOF'
   AWS_ACCESS_KEY_ID
   AWS_SECRET_ACCESS_KEY
   AWS_SESSION_TOKEN
   AWS_REGION=us-west-2
   OTEL_EXPORTER_OTLP_HEADERS=x-bronto-api-key=03a34d3a-975f-4341-9f9e-95cd0a4161bc.-o4bnm_fb2iX7EiBSLoMHibQ0eU0AhTZWeosgQ5RulY=
   ATTENDEE=yourname
   EOF
   ```

   The bare `AWS_…` lines pass the credentials you exported into the container.

> **Run the commands below one box at a time, in order.** Don't paste
> several boxes together: step 4 starts the agent and keeps running, so
> anything pasted after it never runs.

3. **Check your setup.** Paste this, press Enter, and wait for three `ok` lines:

   ```bash
   docker run --rm --env-file .env ghcr.io/bronto-community/track-a-agent python doctor.py
   ```

4. **Start the agent.** Paste this in the **same terminal**. It keeps running
   and prints a line per request: **leave it running**. Ctrl-C stops it.

   ```bash
   docker run --rm -p 8080:8080 --env-file .env -e AGENT_STEP=1 ghcr.io/bronto-community/track-a-agent
   ```

5. **Ask it something.** Open a **second terminal** (a new tab or window) and paste:

   ```bash
   curl -s localhost:8080/invocations -d '{"prompt": "Where is order 1042?"}'
   ```

   Same question with a different model (also in the second terminal):

   ```bash
   curl -s localhost:8080/invocations -d '{"prompt": "Where is order 1042?", "model": "us.amazon.nova-lite-v1:0"}'
   ```

   To move to the next step, go back to the first terminal, press **Ctrl-C**,
   and run step 4 again with `AGENT_STEP=2` (then `3`).

**Linux notes**
- If you run `sudo docker`, sudo drops your exported credentials and the
  doctor reports "Unable to locate credentials". Use `sudo -E docker …`, or
  add yourself to the `docker` group (`sudo usermod -aG docker $USER`, then log
  out and back in).
- Docker Engine is enough; Docker Desktop isn't required.

**WSL notes**
- Run everything inside the WSL terminal, with Docker Desktop's WSL
  integration turned on (Settings → Resources → WSL integration).
- Paste the `export` credential block, not the PowerShell one.

### Windows (PowerShell)

Use PowerShell, not Command Prompt. Windows PowerShell 5.1 and PowerShell 7 both work.
Docker Desktop must be running.

1. **Credentials.** On the workshop page choose **Get AWS CLI credentials**
   and copy the block for PowerShell (the lines start with `$Env:AWS_…`). Paste
   it into the PowerShell window you'll run Docker from. If the page only shows
   `export` lines, rewrite each as `$Env:NAME="value"`.

2. **A folder and a `.env` file.**

   ```powershell
   mkdir track-a; cd track-a
   @"
   AWS_ACCESS_KEY_ID
   AWS_SECRET_ACCESS_KEY
   AWS_SESSION_TOKEN
   AWS_REGION=us-west-2
   OTEL_EXPORTER_OTLP_HEADERS=x-bronto-api-key=03a34d3a-975f-4341-9f9e-95cd0a4161bc.-o4bnm_fb2iX7EiBSLoMHibQ0eU0AhTZWeosgQ5RulY=
   ATTENDEE=yourname
   "@ | Set-Content -Encoding ascii .env
   ```

   Keep `-Encoding ascii`. Without it Windows PowerShell 5.1 can write a
   byte-order mark, and Docker then misreads the first line.

> **Run the commands below one box at a time, in order.** Step 4 starts the
> agent and keeps running, so anything pasted after it never runs.

3. **Check your setup.** Paste this, press Enter, and wait for three `ok` lines:

   ```powershell
   docker run --rm --env-file .env ghcr.io/bronto-community/track-a-agent python doctor.py
   ```

4. **Start the agent.** Same PowerShell window. It keeps running: **leave it
   running**. Ctrl-C stops it.

   ```powershell
   docker run --rm -p 8080:8080 --env-file .env -e AGENT_STEP=1 ghcr.io/bronto-community/track-a-agent
   ```

5. **Ask it something.** Open a **second PowerShell window** and paste:

   ```powershell
   Invoke-RestMethod localhost:8080/invocations -Method Post -ContentType application/json -Body (@{prompt = "Where is order 1042?"} | ConvertTo-Json)
   ```

   Same question with a different model (also in the second window):

   ```powershell
   Invoke-RestMethod localhost:8080/invocations -Method Post -ContentType application/json -Body (@{prompt = "Where is order 1042?"; model = "us.amazon.nova-lite-v1:0"} | ConvertTo-Json)
   ```

   Next step: first window, **Ctrl-C**, then run step 4 again with `AGENT_STEP=2` (then `3`).

**Why not `curl` on Windows?** In Windows PowerShell 5.1, `curl` is an alias
for `Invoke-WebRequest`, and the real `curl.exe` mangles the JSON quotes
unless you escape them. `Invoke-RestMethod` avoids both problems and prints
`result` and `stats` as a table.

### The three steps

| `AGENT_STEP` | What the agent has |
|---|---|
| `1` | A model and a system prompt. No tools. |
| `2` | `lookup_order`, `check_inventory`, and `get_shipping_eta`, which times out about one call in four |
| `3` | Step 2 plus `product_researcher`, a second agent called as a tool |

Add `"model": "us.amazon.nova-lite-v1:0"` to the request body to switch
models for one request. The default is `us.anthropic.claude-haiku-4-5-20251001-v1:0`.
Every response includes a `stats` block with tokens, latency, model calls,
tool calls and an estimated cost.

From a clone of this repo, `docker compose up agent` does the same thing, and
`docker compose run --rm traffic` sends 20 mixed questions.

## Your own AWS account

The same image works with any account where you can call Bedrock.

1. Sign in with the CLI: `aws configure sso` or `aws login`, then point the
   shell at that profile: `export AWS_PROFILE=yourprofile` (bash/zsh) or
   `$Env:AWS_PROFILE="yourprofile"` (PowerShell).
2. Replace the three bare `AWS_…` lines in `.env` with a bare `AWS_PROFILE`
   line, and mount your AWS config into each `docker run`:
   - bash/zsh: `-v ~/.aws:/root/.aws:ro`
   - PowerShell: `-v "$env:USERPROFILE\.aws:/root/.aws:ro"`
3. Model access: Amazon Nova works straight away. Anthropic models need a
   one-time use-case form in the Bedrock console (Model catalog → Claude).
4. Least privilege: attach [`iam/least-privilege.json`](iam/least-privilege.json)
   to your user or role. It allows Bedrock invoke on Claude Haiku/Sonnet 4.5
   and Nova, and `sts:GetCallerIdentity` for the doctor. Nothing else.
5. Another region: set `AWS_REGION` and pick a model or inference profile
   that exists there (`eu.` profiles in Europe, for example).

A full run of all three steps is a few hundred thousand tokens: a few cents on
Haiku 4.5, a fraction of a cent on Nova Lite.

## Your own Bronto account

Start a free trial at [bronto.io/signup](https://bronto.io/signup), create an
ingestion API key, and put it in `OTEL_EXPORTER_OTLP_HEADERS`. For a US
account, add `OTEL_EXPORTER_OTLP_ENDPOINT=https://ingestion.us.bronto.io`.

Then build the same dashboard in your org with a key that can write dashboards:

```bash
BRONTO_API_KEY=... python3 dashboard/create_dashboard.py
```

On Windows: `$Env:BRONTO_API_KEY="..."; python dashboard\create_dashboard.py`.

## What's in here

| Path | What |
|---|---|
| `agent/` | The agent, its tools, the telemetry setup, `doctor.py`, `traffic.py` |
| `dashboard/create_dashboard.py` | Builds the "LLM KPIs — Storefront Assistant" dashboard |
| `iam/least-privilege.json` | IAM policy for running the lab in your own account |
| `slides/` | The Track A deck (Slidev): `cd slides && npm install && npm run dev` |
| `facilitator.md` | Prep checklist and notes for whoever runs the session |

Telemetry setup follows Bronto's
[AgentCore guide](https://docs.bronto.io/ai-features/aws-agentcore).

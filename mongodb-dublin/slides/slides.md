---
theme: default
title: AI Observability & Monitoring
info: |
  ## AI Observability & Monitoring: Bronto × MongoDB, Dublin AI Week
  A 20-minute talk, then a 75-minute guided build: trace an AI agent, connect
  application signals with MongoDB Atlas metrics, and build an AI SRE that
  finds the root cause of a production incident.
colorSchema: light
transition: slide-left
mdc: true
class: text-left
favicon: /img/bronto-dino.png
fonts:
  sans: Radio Canada Big
  serif: Source Serif 4
  mono: Geist Mono
---

<div class="title-hero">
  <img src="/img/confetti-left.png" class="confetti c-left" />
  <img src="/img/confetti-right.png" class="confetti c-right" />

# AI Observability & Monitoring

</div>

<div class="subtitle">From the model call to the database: what your AI system is really doing</div>

<div class="track">Bronto × MongoDB · Dublin AI Week · 7 October 2026 · with Give(a)Go</div>

<a href="https://bronto.io" target="_blank" rel="noopener" class="abs-bl m-10 brand-logo-link">
  <img src="/img/bronto-logo.webp" class="brand-logo" />
</a>

<style>
.title-hero { position: relative; display: inline-block; }
.title-hero h1 { font-size: 3.8rem; line-height: 1.02; }
.confetti { position: absolute; width: 118px; height: auto; pointer-events: none; }
.c-left { top: -100px; left: -60px; }
.c-right { top: 50%; right: -132px; transform: translateY(-50%); }
.subtitle { margin-top: 1.6rem; font-size: 1.3rem; color: var(--ink-dim); }
.track {
  margin-top: 1.2rem; font-family: 'Geist Mono', monospace; font-size: 0.8rem;
  text-transform: uppercase; letter-spacing: 0.14em; color: var(--sapphire);
}
.brand-logo { width: 150px; height: auto; }
.brand-logo-link { display: inline-block; line-height: 0; }
</style>

<!--
Up while Harshit wraps. One line on who you are.

Shape of the next 95 minutes: 20 minutes of talk, then we build. Laptops can
stay closed for now; open them when the QR code comes up.
-->

---
layout: center
---

<div class="bridge">
  <div class="kicker">Picking up from Harshit</div>
  <h1 class="bh">The database was the blind spot.</h1>

  <div class="cols even">
    <div class="stack">
      <div class="card">
        <b>Before</b>
        <span>Your traces end at a span called <code>mongodb find</code>. Why it took 1.2 seconds lives in a different tool, with a different login, owned by a different team.</span>
      </div>
      <div class="card mongo">
        <b>Atlas OTel Metrics Sink (GA)</b>
        <span>Atlas pushes cluster metrics over OTLP to any OpenTelemetry backend. M10 and up. Atlas Log Integration ships the mongod logs too.</span>
      </div>
    </div>
    <div class="stack">
      <div class="card hl">
        <b>Tonight</b>
        <span>Storefront's traces, its logs, and its Atlas cluster's metrics and slow-query logs all land in one Bronto org. One query language, one timeline.</span>
      </div>
      <div class="card">
        <b>Why it matters for AI</b>
        <span>An agent investigating an incident can only reason about what it can see. Close the blind spot for humans and you close it for the agent.</span>
      </div>
    </div>
  </div>
</div>

<style>
.bridge { max-width: 58rem; }
.bh { font-size: 2.5rem; margin: 0.5rem 0 1.4rem; }
</style>

<!--
Harshit showed you the why; I'll show you the wiring in a minute, and then you
use it.

The MongoDB post is "Close the database blind spot with Atlas observability".
The key line: Atlas metrics go to any OTLP-compatible backend. Bronto is one.
-->

---

# How we wired it for tonight

<div class="flow mt-6">
  <div class="node mongo"><div class="i-lucide-database ico" /><b>Atlas M10</b><span>Storefront's products and 1.5M orders, eu-west-1</span></div>
  <div class="arrow">→</div>
  <div class="node mongo"><div class="i-lucide-radio-tower ico" /><b>OTel Metrics Sink</b><span>MongoDB + hardware metrics, every minute</span></div>
  <div class="arrow">+</div>
  <div class="node mongo"><div class="i-lucide-scroll-text ico" /><b>OTel Log Export</b><span>the mongod log, slow queries included</span></div>
  <div class="arrow">→</div>
  <div class="node hl"><div class="i-lucide-search ico" /><b>Bronto</b><span>next to Storefront's traces, same org</span></div>
</div>

<div class="cols even mt-8">
  <div class="card">
    <b>Configuration</b>
    <span>Project → Integrations → OpenTelemetry. Endpoint <code>https://ingestion.eu.bronto.io/v1/metrics</code>, one header: <code>x-bronto-api-key</code>. Atlas sends a test metric the moment you save. Also scriptable through the Admin API.</span>
  </div>
  <div class="card warn">
    <b>What to know</b>
    <span>M10 and up. TLS with a public CA (Bronto's ingestion endpoint qualifies). Logs: about 1 GB per host per day, and they can contain PII.</span>
  </div>
</div>

<!--
No collector in between: Atlas pushes straight to Bronto with the key in a
header. The metrics integration took one Admin API call; the log export is a
form in the Atlas UI.
-->

---

# Two readings of "AI observability"

<div class="cols even mt-6">
  <div class="card hl">
    <div class="kicker">Observability for AI</div>
    <b style="font-size:1.4rem">Watch your agent think</b>
    <p>Every model call, tool call and token, as a trace. What did it cost? Why was it slow? Which tool failed, and what did the user get told?</p>
    <p><b>Tonight, step 2.</b></p>
  </div>
  <div class="card mongo">
    <div class="kicker" style="color:#00684A">AI for observability</div>
    <b style="font-size:1.4rem">Let an agent read your telemetry</b>
    <p>An AI SRE: give a model your logs, traces and metrics as tools, and ask it what broke. How good is it? What can't it see?</p>
    <p><b>Tonight, steps 3 to 6.</b></p>
  </div>
</div>

<div class="lede mt-8">You build one agent. It produces telemetry about itself, and it consumes telemetry about Storefront.</div>

<!--
Both readings, one agent. Keep this slide short: it's the map for the rest.
-->

---

# An agent is a span in someone's request

<TraceTree :upto="$clicks === 0 ? 1 : $clicks === 1 ? 4 : 99" class="mt-3" />

<div v-click="1" />
<div v-click="2" />

<div class="legend">
  <span><i class="d a" />agent</span><span><i class="d m" />model call</span><span><i class="d t" />tool</span><span><i class="d w" />SDK call</span>
  <span class="src">A real agent trace in Bronto, from our AWS Observatory lab</span>
</div>

<style>
.legend { display: flex; gap: 1.2rem; margin-top: 1.2rem; font-size: 0.75rem; color: var(--ink-dim); align-items: center; }
.legend .d { display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin-right: 0.35rem; }
.d.a { background: var(--sapphire); } .d.m { background: var(--mint); } .d.t { background: #E0A100; } .d.w { background: #FF9900; }
.legend .src { margin-left: auto; font-style: italic; }
</style>

<!--
Click 0: one span, 6.6 seconds. That's all classic APM gives you.
Click 1: the loop, a model call (866 tokens in), it chose a tool.
Click 2: a sub-agent, its own loop, four inventory lookups, then the answer.

The point: it's just a trace. Same tools, same backend as the rest of your
system, once the framework emits the spans.
-->

---

# The vocabulary: OpenTelemetry GenAI conventions

<div class="cols">
<div>

<div class="n">On every model call span</div>

```
gen_ai.operation.name           chat
gen_ai.provider.name            gcp.gemini
gen_ai.request.model            gemini-3.8-flash
gen_ai.usage.input_tokens       2,914
gen_ai.usage.output_tokens      388
gen_ai.response.finish_reasons  ["tool_use"]
```

<div class="n">On every tool call span</div>

```
gen_ai.operation.name   execute_tool
gen_ai.tool.name        query_atlas_metrics
gen_ai.tool.status      success
```

</div>
<div class="stack" style="padding-top:1.4rem">

<div class="card">
<b>These are your GROUP BY</b>
<span>Model, tokens, tool, finish reason. Latency, cost and failure dashboards are these names, grouped or summed.</span>
</div>

<div class="card">
<b>Frameworks emit them for free</b>
<span>Strands (tonight's agent), and most agent frameworks now. You point the exporter somewhere; you don't write spans.</span>
</div>

<div class="card warn">
<b>Still moving</b>
<span>Only two attributes are Required, and the spec has no tagged release. Prompts on spans are Opt-In: treat them as sensitive data.</span>
</div>

</div>
</div>

<style>
.slidev-layout { --slidev-code-font-size: 0.7em; }
</style>

<!--
The values are illustrative for tonight's agent on Gemini. Replace with real
ones from rehearsal.
-->

---

# What breaks in AI systems in production

<div class="grid4 mt-6">
  <div class="card"><b>Latency</b><span>Every loop is another model call. P95 hides the three-loop answers.</span></div>
  <div class="card"><b>Token blow-up</b><span>Input grows with every tool call: history and tool results ride along.</span></div>
  <div class="card"><b>Failing tools</b><span>A tool error often becomes a confident, wrong answer to the user.</span></div>
  <div class="card mongo"><b>The dependency underneath</b><span>The tool is fine; the query behind it isn't. Slow database, slow agent, slow everything.</span></div>
</div>

<div class="lede mt-8">The first three are visible in the agent's own trace. The fourth needs the database's signals next to it. That's the gap Harshit just closed.</div>

<style>
.grid4 { display: grid; grid-template-columns: repeat(4, 1fr); gap: 0.8rem; }
</style>

---

# Joining app signals and database signals

<IncidentTrace :bad="$clicks >= 1" class="mt-4" />
<div v-click="1" />

<div class="cols even mt-6">
  <div class="card">
    <b>From the trace</b>
    <span><code>db.system.name = mongodb</code>, the operation, the collection, and the duration of every database call, as a child span of the request.</span>
  </div>
  <div class="card mongo">
    <b>From Atlas</b>
    <span>Metrics: query targeting jumps (documents scanned per document returned), op latency and CPU climb. Logs: <code>Slow query … planSummary: COLLSCAN, docsExamined: 1,500,000</code>.</span>
  </div>
</div>

<!--
Click 0: a healthy checkout. 140 ms, mostly the payment provider.
Click 1: after a release. Same request, 1.4 seconds, and nearly all of it is one
count on orders.

The trace tells you WHERE. Atlas tells you WHY: it scanned every order.
Tonight's incident is exactly this. Don't give away which commit.

Numbers are illustrative until rehearsal; replace with a real trace.
-->

---

# An AI SRE, in five parts

<div class="flow mt-6">
  <div class="node"><div class="i-lucide-repeat ico" /><b>A loop</b><span>a model that can call tools until it's done</span></div>
  <div class="node"><div class="i-lucide-id-card ico" /><b>An identity</b><span>who it is, its rules: the system prompt</span></div>
  <div class="node hl"><div class="i-lucide-eye ico" /><b>Eyes</b><span>Bronto MCP: logs and traces. Plus a metrics tool for Atlas</span></div>
  <div class="node"><div class="i-lucide-message-square ico" /><b>A mouth</b><span>its finding, as a GitHub issue</span></div>
  <div class="node"><div class="i-lucide-code ico" /><b>The code</b><span>GitHub MCP: the release and its commits</span></div>
</div>

<div class="lede mt-8">That's the whole thing. Managed products (AWS DevOps Agent and others) package the same parts. Build one once and you know what's inside them, and what they can't see.</div>

<div class="credit">After Severin Neumann's "Build your own AI SRE" lab.</div>

<style>
.credit { position: absolute; bottom: 2rem; right: 3.5rem; font-size: 0.75rem; color: var(--ink-dim); font-style: italic; }
</style>

<!--
Each part is one step tonight, plus tracing and the database.
-->

---
layout: center
---

<div class="plan">
  <div class="kicker">Tonight, on your laptop</div>
  <h1 class="plan-head">Your agent, traced into your Bronto, investigating our Storefront.</h1>

  <div class="flow">
    <div class="node"><div class="i-lucide-laptop ico" /><b>Your laptop</b><span>the agent, in Docker<br/>Gemini (free tier) or your own key</span></div>
    <div class="arrow">→</div>
    <div class="node hl"><div class="i-lucide-activity ico" /><b>Your Bronto</b><span>your agent's own traces:<br/>model calls, tools, tokens</span></div>
    <div class="arrow">+</div>
    <div class="node mongo"><div class="i-lucide-store ico" /><b>Shared demo org</b><span>Storefront traces + Atlas metrics and logs, read-only</span></div>
    <div class="arrow">→</div>
    <div class="node"><img src="/img/logo-github.svg" class="gh" /><b>Your GitHub</b><span>its finding, as an issue</span></div>
  </div>

  <div class="agenda">
    <span><b>10 min</b> setup</span>
    <span><b>6 steps</b> ~10 min each</span>
    <span><b>8:30</b> what did your agent find?</span>
  </div>
</div>

<style>
.plan { max-width: 62rem; }
.plan-head { font-size: 2.1rem; margin: 0.6rem 0 2rem; }
.gh { width: 22px; height: 22px; }
.agenda { display: flex; gap: 2rem; margin-top: 2rem; font-size: 1rem; color: var(--ink-dim); }
.agenda b { color: var(--ink); font-family: 'Geist Mono', monospace; margin-right: 0.35rem; }
</style>

<!--
Two Bronto orgs: theirs (they signed up before tonight) receives their agent's
traces. Ours is the shared demo org with Storefront, read with a public
read-only key: nobody logs in to it, the agent reads it.

Storefront: a small shop. checkout-api and catalog-api on MongoDB Atlas.
Tonight a release went out at 7:30 and checkout got slow.
-->

---
layout: center
---

<div class="go">
  <div class="kicker">Let's build</div>
  <h1 class="go-head">Open the lab guide</h1>
  <div class="go-grid">
    <QrCode url="https://ai-observatory-lab.vercel.app/dublin" :size="200" caption="ai-observatory-lab.vercel.app/dublin" />
    <div class="sc-list">
      <span>Docker running</span>
      <span>A Gemini API key (free: aistudio.google.com/apikey)</span>
      <span>Your Bronto account and an ingestion key</span>
      <span>A GitHub token for one empty repo, <code>ai-sre-issues</code></span>
    </div>
  </div>
</div>

<style>
.go { max-width: 56rem; }
.go-head { font-size: 2.8rem; margin: 0.5rem 0 1.6rem; }
.go-grid { display: flex; gap: 3rem; align-items: center; }
.go-grid .sc-list span { color: var(--ink); }
</style>

<!--
Leave this up for a full minute. Walk the room: who has no Bronto account?
Hand them the workshop ingestion key card.
-->

---
layout: center
---

<SectionCard kicker="Guided build · 75 minutes" title="Build your own AI SRE" art="/img/dino-blocks.png">
  <div class="sc-list">
    <span><b>1</b> · the loop and an identity</span>
    <span><b>2</b> · trace it into your Bronto</span>
    <span><b>3</b> · eyes: Bronto MCP</span>
    <span><b>4</b> · the database: Atlas metrics</span>
    <span><b>5</b> · a mouth: a GitHub issue</span>
    <span><b>6</b> · the code</span>
  </div>
</SectionCard>

---

# Setup

<div class="step-time">7:15 · 10 min</div>

<div class="cols even">
<div>

<div class="n">1 · Docker is running, and the image is here</div>

<Cmd run="docker pull ghcr.io/bronto-community/mongodb-lab-agent" />

<div class="n">2 · A folder and a <code>.env</code></div>

<Cmd run="mkdir mongodb-lab && cd mongodb-lab
cat > .env <<'EOF'
GEMINI_API_KEY=YOUR-GEMINI-KEY
EOF" />

<div class="hint">Another provider? Add <code>LLM_PROVIDER=openai</code>, <code>anthropic</code> or <code>bedrock</code> and its key. The guide has every variant, and PowerShell versions.</div>

</div>
<div>

<div class="n">3 · Your rules for the agent</div>

<Cmd run="cat > my.md <<'EOF'
- Answer in at most three bullet points.
- End every answer with your confidence: low, medium or high.
- Sign off as &quot;your friendly on-call dino&quot;.
EOF" />

<div class="hint">Every <code>.md</code> file in its <code>prompts/</code> folder becomes the system prompt. You'll mount this one in.</div>

<div class="card mt-4">
<b>Two terminals</b>
<span>Terminal 1 runs the agent and stays running. Terminal 2 asks it questions. To move to the next step: <kbd>Ctrl-C</kbd> in terminal 1, run the new command.</span>
</div>

</div>
</div>

<!--
Free Gemini keys: aistudio.google.com/apikey, sign in with a Google account,
"Create API key". Rate limits are fine for one person.
-->

---

# Step 1: the loop and an identity

<div class="step-time">8 min</div>

<div class="cols">
<div>

<div class="n">Terminal 1 · start it</div>

<Cmd run='docker run --rm -p 8080:8080 --env-file .env -v "$PWD/my.md:/app/prompts/my.md" -e AGENT_STEP=1 ghcr.io/bronto-community/mongodb-lab-agent' />
<div class="keep">Leave it running.</div>

<div class="n">Terminal 2 · ask it</div>

<Ask prompt="Who are you?" />
<div class="ask-label mt-3">Then: <b>"Checkout is slow. What is wrong?"</b></div>

</div>
<div class="stack" style="padding-top:1.2rem">

<div class="card">
<b>What's inside</b>
<span>A Strands agent: a model, a system prompt from <code>prompts/*.md</code>, no tools yet. An HTTP endpoint on :8080.</span>
</div>

<div class="card hl">
<b>What to notice</b>
<span>It follows your rules. And asked about checkout, it should say it can't see anything. If it invents an answer, that's the first lesson.</span>
</div>

</div>
</div>

<style>
.keep { font-size: 0.72rem; color: var(--ink-dim); margin: 0.25rem 0 0.1rem; }
</style>

---

# Step 2: trace it into your Bronto

<div class="step-time">12 min</div>

<div class="cols">
<div>

<div class="n">Add your Bronto key to <code>.env</code></div>

<Cmd run="cat >> .env <<'EOF'
OTEL_EXPORTER_OTLP_HEADERS=x-bronto-api-key=YOUR-INGESTION-KEY
BRONTO_REGION=eu
ATTENDEE=yourname
EOF" />
<div class="hint"><code>BRONTO_REGION</code> is <code>us</code> if your Bronto address is app.us.bronto.io.</div>

<div class="n">Restart with <code>AGENT_STEP=2</code>, ask again</div>

<Cmd run='docker run --rm -p 8080:8080 --env-file .env -v "$PWD/my.md:/app/prompts/my.md" -e AGENT_STEP=2 ghcr.io/bronto-community/mongodb-lab-agent' />

</div>
<div class="stack" style="padding-top:1.2rem">

<div class="card hl">
<b>In your Bronto</b>
<span>Search → service <code>ai-sre</code> → open a trace. <code>invoke_agent</code> → <code>execute_event_loop_cycle</code> → <code>chat</code>. Tokens in and out are on the <code>chat</code> span.</span>
</div>

<div class="card">
<b>The whole change</b>
<span>Strands already makes the spans. Step 2 only gives it an exporter: <code>StrandsTelemetry().setup_otlp_exporter()</code> and an OTLP endpoint.</span>
</div>

<div class="card">
<b>Keep the tab open</b>
<span>Every step from now on adds spans: MCP tool calls, the metrics tool, longer loops. Watch the input tokens grow.</span>
</div>

</div>
</div>

<!--
The env vars are standard OpenTelemetry. Nothing Bronto-specific except the
header name and the endpoint. The agent sets the endpoint from BRONTO_REGION.
-->

---

# Step 3: eyes (Bronto MCP)

<div class="step-time">10 min</div>

<div class="cols">
<div>

<div class="n">The shared demo org's read-only key</div>

<Cmd run="echo 'BRONTO_API_KEY=13a79ead-d125-4f71-ab4d-c579119c7e1c.tUqIG3BTaonVJi_fdFldd8QjtfIcGzr4ZQfYJoXqXRo=' >> .env" />

<div class="n">Restart with <code>AGENT_STEP=3</code>, then ask</div>

<Cmd run='docker run --rm -p 8080:8080 --env-file .env -v "$PWD/my.md:/app/prompts/my.md" -e AGENT_STEP=3 ghcr.io/bronto-community/mongodb-lab-agent' />

<div class="ask-label">First <b>"What services do you know about?"</b>, then <b>"Anything wrong with checkout?"</b></div>

</div>
<div class="stack" style="padding-top:1.2rem">

<div class="card">
<b>What it can now see</b>
<span>Bronto's MCP server: list datasets, search logs and traces in the shared org where Storefront runs. Its tools become the agent's tools.</span>
</div>

<div class="card hl">
<b>What to notice</b>
<span>It should find that checkout got slow. Does it say why? Look at the trace in your Bronto: how many MCP calls, how many tokens?</span>
</div>

<div class="card warn">
<b>What it can't see</b>
<span>Bronto MCP reads logs and traces, not metrics. Atlas's metrics are invisible to it, for now.</span>
</div>

</div>
</div>

<!--
Bronto MCP: mcp.eu.bronto.io/mcp. Key is read-only and public on purpose.

Typical answer: "checkout-api p95 went from ~140 ms to ~1.4 s around :30,
something in checkout-api". Sometimes it blames catalog: catalog logs a noisy
"cache miss" warning all the time. Good discussion point.
-->

---

# Step 4: the database

<div class="step-time">12 min</div>

<div class="cols">
<div>

<div class="n">Teach it how you investigate: add to <code>my.md</code></div>

<Cmd run="cat >> my.md <<'EOF'
- Slow is broken too: compare latency (p50, p95) before and after, not only errors.
- Compare against a quiet window earlier the same evening.
- When a request is slow, look at its child spans: is the time in the database?
- Then check the database's side: Atlas metrics (query targeting, operation latency) and slow-query logs.
EOF" />

<div class="n">Restart with <code>AGENT_STEP=4</code></div>

<Cmd run='docker run --rm -p 8080:8080 --env-file .env -v "$PWD/my.md:/app/prompts/my.md" -e AGENT_STEP=4 ghcr.io/bronto-community/mongodb-lab-agent' />

<div class="ask-label">Ask: <b>"Customers say checkout got slow tonight. Is it the database?"</b></div>

</div>
<div class="stack" style="padding-top:1.2rem">

<div class="card mongo">
<b>A new sense</b>
<span>Two tools that call Bronto's metrics API: <code>list_atlas_metrics</code> and <code>query_atlas_metrics</code>. About 80 lines of Python.</span>
</div>

<div class="card hl">
<b>What to notice</b>
<span>Does it connect the slow <code>mongodb count</code> span to Atlas's numbers? Does it find the <code>COLLSCAN</code> slow-query line, and which collection and filter?</span>
</div>

<div class="card">
<b>Instructions matter</b>
<span>Same model, four lines of rules. That's how you'd teach a new on-call engineer, too.</span>
</div>

</div>
</div>

<!--
This is the "connect application signals with database metrics" step from the
agenda. If someone's agent doesn't use the metrics tool, ask them to add "use
query_atlas_metrics" to my.md: the tool description alone isn't always enough.
-->

---

# Step 5: a mouth (a GitHub issue)

<div class="step-time">8 min</div>

<div class="cols">
<div>

<div class="n">Your repo and token</div>

<Cmd run="cat >> .env <<'EOF'
GITHUB_REPO=YOUR-GITHUB-USER/ai-sre-issues
GITHUB_TOKEN=YOUR-GITHUB-TOKEN
EOF" />
<div class="hint">A fine-grained token, only for <code>ai-sre-issues</code>, permission <b>Issues: read and write</b>.</div>

<div class="n">Restart with <code>AGENT_STEP=5</code>, ask again</div>

<Cmd run='docker run --rm -p 8080:8080 --env-file .env -v "$PWD/my.md:/app/prompts/my.md" -e AGENT_STEP=5 ghcr.io/bronto-community/mongodb-lab-agent' />

</div>
<div class="stack" style="padding-top:1.2rem">

<div class="card hl">
<b>The answer is a link</b>
<span>A new issue in your repo: a one-line hypothesis, the evidence, its confidence, and what it couldn't check.</span>
</div>

<div class="card">
<b>Why an issue</b>
<span>Its output goes where humans already look, with the evidence attached. Would you act on it? What's missing?</span>
</div>

</div>
</div>

---

# Step 6: the code

<div class="step-time">10 min</div>

<div class="cols">
<div>

<div class="n">Restart with <code>AGENT_STEP=6</code></div>

<Cmd run='docker run --rm -p 8080:8080 --env-file .env -v "$PWD/my.md:/app/prompts/my.md" -e AGENT_STEP=6 ghcr.io/bronto-community/mongodb-lab-agent' />

<div class="ask-label">Ask: <b>"Customers say checkout got slow tonight. What is going on?"</b></div>

<div class="ask-label">If it stops at the deploy: <b>"Which change in that release caused it? Read the code."</b></div>

</div>
<div class="stack" style="padding-top:1.2rem">

<div class="card">
<b>What it can now read</b>
<span>GitHub MCP, read-only: <code>bronto-community/storefront-mongo</code>, its releases and commits. Every service reports the commit it runs as <code>deployment.commit</code>.</span>
</div>

<div class="card hl">
<b>The release has three commits</b>
<span>Two of them are decoys, and one of the decoys touches MongoDB too. Does it pick the right one? Does it say which index is missing?</span>
</div>

</div>
</div>

<!--
The culprit adds a count on orders filtered by customer_email. The indexes are
on customer_id, not email: see scripts/create_indexes.py. The commit message
says "orders are already indexed by customer, so this is cheap". That's the
trap. Don't say this out loud until 8:30.
-->

---
layout: center
---

<div class="wrap">
  <div class="kicker">8:30 · builds, lessons, questions</div>
  <h1 class="wrap-head">What did your agent find?</h1>

  <div class="cols even">
    <div class="sc-list">
      <span>Who got the right commit? With which model?</span>
      <span>Whose agent blamed catalog, or the pymongo bump?</span>
      <span>How many tokens did your best investigation cost? (Check your Bronto.)</span>
      <span>What would your agent get wrong on your system?</span>
    </div>
    <div class="stack">
      <div class="card">
        <b>What you built</b>
        <span>A trigger (curl), a loop (Strands), an identity (prompts), eyes (Bronto MCP + a metrics tool), a mouth (GitHub), the code (GitHub MCP). Traced end to end.</span>
      </div>
      <div class="card mongo">
        <b>What closed the gap</b>
        <span>Database signals in the same place as the app's. Without step 4, the best it can say is "something in checkout".</span>
      </div>
    </div>
  </div>
</div>

<style>
.wrap { max-width: 62rem; }
.wrap-head { font-size: 2.6rem; margin: 0.5rem 0 1.6rem; }
.wrap .sc-list span { color: var(--ink); font-size: 1.05rem; }
</style>

<!--
Reveal: v4.1.0, "flag returning customers for the loyalty banner". A count on
orders by customer_email; the index is on customer_id. COLLSCAN of 1.5M orders
on every checkout. The fix: an index on customer_email, or count by id.
-->

---
layout: center
---

<div class="home">
  <div class="kicker">Take it home</div>
  <h1 class="home-head">Thank you, Dublin</h1>

  <div class="home-grid">
    <div class="sc-list">
      <span>The guide stays up. Run it again at your own pace.</span>
      <span>Point the agent at your own Bronto: swap the read-only key.</span>
      <span>Atlas on M10+: Project → Integrations → OpenTelemetry.</span>
      <span>Bronto: a free account at bronto.io.</span>
    </div>
    <div class="qrs">
      <QrCode url="https://ai-observatory-lab.vercel.app/dublin" :size="120" caption="lab guide" />
      <QrCode url="https://github.com/bronto-community/ai-observatory-lab" :size="120" caption="the code" />
      <QrCode url="https://bronto.io" :size="120" caption="bronto.io" />
    </div>
  </div>
</div>

<img src="/img/bronto-dino.png" class="abs-br mr-12 mb-10 dino" />

<style>
.home { max-width: 60rem; }
.home-head { font-size: 2.6rem; margin: 0.5rem 0 1.6rem; }
.home-grid { display: flex; gap: 2.5rem; align-items: center; }
.home-grid .sc-list span { color: var(--ink); font-size: 1.05rem; }
.qrs { display: flex; gap: 1.2rem; }
.dino { width: 90px; }
</style>

<!--
Thank Harshit, MongoDB for the room, Give(a)Go for organising.
-->

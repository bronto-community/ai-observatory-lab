---
theme: default
title: Observability for AI
info: |
  ## Observability for AI — Track A
  Run an agent on Bedrock, send its telemetry to Bronto, and read what it did:
  model calls, tokens, tool calls, sub-agents, and the KPIs that matter.
  Part of the AWS + Bronto AI & Observability evening.
colorSchema: light
transition: slide-left
mdc: true
class: text-left
favicon: /favicon.ico
fonts:
  sans: Radio Canada Big
  serif: Source Serif 4
  mono: Geist Mono
---

<div class="title-hero">
  <img src="/img/confetti-left.png" class="confetti c-left" />
  <img src="/img/confetti-right.png" class="confetti c-right" />

# Observability for AI

</div>

<div class="subtitle">Watch an agent think: traces, tokens and tools, in Bronto</div>

<div class="track">Track A · 40 minutes · hands-on</div>

<a href="https://bronto.io" target="_blank" rel="noopener" class="abs-bl m-10 brand-logo-link">
  <img src="/img/bronto-logo.webp" class="brand-logo" />
</a>

<style>
.title-hero { position: relative; display: inline-block; }
.title-hero h1 { font-size: 4.1rem; line-height: 1.02; }
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
Up while people come back from the intro. Say who you are in one line.

Severin just said the agent is a span in somebody's request, and that AgentCore
ships to CloudWatch unless you change one environment variable. The next 40
minutes are that environment variable, and what shows up when you change it.
-->

---
layout: center
---

<div class="plan">
  <div class="kicker">Tonight, in this room</div>
  <h1 class="plan-head">You run an agent. Bronto shows you what it did.</h1>

  <div class="flow">
    <div class="node"><div class="i-lucide-laptop ico" /><b>Your laptop</b><span>the agent, in Docker</span></div>
    <div class="arrow">→</div>
    <div class="node"><div class="i-lucide-brain ico" /><b>Amazon Bedrock</b><span>Claude Haiku 4.5 · Nova Lite<br/>us-west-2, your workshop account</span></div>
    <div class="arrow">+</div>
    <div class="node hl"><div class="i-lucide-radio-tower ico" /><b>OpenTelemetry → Bronto</b><span>every model call, tool call<br/>and token, as spans</span></div>
    <div class="arrow">→</div>
    <div class="node"><div class="i-lucide-layout-dashboard ico" /><b>One dashboard</b><span>the whole room's<br/>LLM KPIs, live</span></div>
  </div>

  <div class="agenda">
    <span><b>8 min</b> what an agent trace looks like</span>
    <span><b>25 min</b> three steps, hands on</span>
    <span><b>5 min</b> the dashboard</span>
  </div>
</div>

<style>
.plan { max-width: 60rem; }
.kicker {
  font-family: 'Geist Mono', monospace; font-size: 0.85rem; font-weight: 600;
  text-transform: uppercase; letter-spacing: 0.16em; color: var(--sapphire);
}
.plan-head { font-size: 2.2rem; margin: 0.6rem 0 2rem; }
.flow { display: flex; align-items: stretch; gap: 0.6rem; }
.node {
  flex: 1; display: flex; flex-direction: column; gap: 0.35rem;
  background: var(--surface); border: 1px solid var(--border); border-radius: 14px;
  padding: 0.9rem 1rem;
}
.node.hl { border-color: var(--sapphire); box-shadow: 0 8px 24px -16px var(--sapphire); }
.node b { font-size: 1rem; }
.node span { font-size: 0.82rem; color: var(--ink-dim); line-height: 1.35; }
.ico { font-size: 1.4rem; color: var(--sapphire); }
.arrow { align-self: center; color: var(--ink-dim); font-size: 1.3rem; }
.agenda { display: flex; gap: 2rem; margin-top: 2rem; font-size: 1rem; color: var(--ink-dim); }
.agenda b { color: var(--ink); font-family: 'Geist Mono', monospace; margin-right: 0.35rem; }
</style>

<!--
The agent is a small customer assistant for a kitchenware shop. It looks up
orders, checks stock, asks a carrier for delivery times. One of its tools
fails about a quarter of the time, on purpose.

Everyone sends to one shared Bronto tenant, so by the end the dashboard has the
whole room on it.
-->

---
layout: center
---

<SectionCard kicker="Part 1 · 8 minutes" title="What an agent looks like from the outside" art="/img/dino-scientist.png">
  <div class="sc-list">
    <span>One question, one trace, a dozen spans</span>
    <span>The GenAI vocabulary, and where it stops</span>
    <span>Tokens, not dollars</span>
  </div>
</SectionCard>

---

# One customer question, as a trace

<div class="q">"Do you have espresso cups? If not, what would you suggest instead?"</div>

<TraceTree :upto="$clicks === 0 ? 1 : $clicks === 1 ? 4 : 99" class="mt-3" />

<div v-click="1" />
<div v-click="2" />

<div class="legend">
  <span><i class="d a" />agent</span><span><i class="d m" />model call</span><span><i class="d t" />tool</span><span><i class="d w" />AWS SDK</span>
  <span class="src">A real trace from this lab, captured in Bronto during rehearsal</span>
</div>

<style>
.q { font-family: 'Source Serif 4', Georgia, serif; font-size: 1.25rem; color: var(--ink-dim); font-style: italic; }
.legend { display: flex; gap: 1.2rem; margin-top: 1.2rem; font-size: 0.75rem; color: var(--ink-dim); align-items: center; }
.legend .d { display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin-right: 0.35rem; }
.d.a { background: var(--sapphire); } .d.m { background: var(--mint); } .d.t { background: #E0A100; } .d.w { background: #FF9900; }
.legend .src { margin-left: auto; font-style: italic; }
</style>

<!--
Click 0: one span. The customer asked a question and waited 6.6 seconds.
That's all classic APM would tell you.

Click 1: open it. The agent loop, then a model call: Haiku read 866 tokens
and decided to use a tool. Under it, the AWS SDK span for the same Bedrock
call. Two instrumentations, one call, two spans. Come back to that.

Click 2: the rest. It handed the question to a second agent, the product
researcher, which ran its own loop and checked inventory four times. Then the
main agent wrote the answer.

Three model calls you can see, two more hidden inside the sub-agent. The
parent span says 1,898 input tokens. The real number for this question is
3,548, because the sub-agent's tokens aren't in the parent's total.
-->

---

# The vocabulary: OpenTelemetry GenAI conventions

<div class="cols">
<div>

<div class="n">On every model call span</div>

```
gen_ai.operation.name           chat
gen_ai.provider.name            aws.bedrock
gen_ai.request.model            us.anthropic.claude-haiku-4-5…
gen_ai.usage.input_tokens       866
gen_ai.usage.output_tokens      62
gen_ai.response.finish_reasons  ["tool_use"]
gen_ai.server.time_to_first_token  1235
```

<div class="n">On every tool call span</div>

```
gen_ai.operation.name   execute_tool
gen_ai.tool.name        get_shipping_eta
gen_ai.tool.call.id     tooluse_uMdDidEKz0fX…
gen_ai.tool.status      error
```

</div>
<div class="side">

<div class="card">
<b>These are your GROUP BY</b>
<span>Model, tokens, tool, finish reason. Every widget on tonight's dashboard is one of these names, grouped or summed.</span>
</div>

<div class="card warn">
<b>Only two are Required</b>
<span><code>operation.name</code> and <code>provider.name</code>. Everything else is Recommended or Opt-In, and the conventions have never had a tagged release.</span>
</div>

<div class="card">
<b>Prompts are Opt-In</b>
<span>Message content is off by default in the spec. Strands captures it anyway. Treat it as sensitive data.</span>
</div>

</div>
</div>

<style>
.cols { display: grid; grid-template-columns: minmax(0,1.25fr) minmax(0,1fr); gap: 1.6rem; margin-top: 0.6rem; }
.n {
  margin: 0.6rem 0 0.3rem; font-family: 'Geist Mono', monospace; font-size: 0.7rem; font-weight: 600;
  text-transform: uppercase; letter-spacing: 0.12em; color: var(--sapphire);
}
.slidev-layout { --slidev-code-font-size: 0.7em; }
.side { display: flex; flex-direction: column; gap: 0.8rem; padding-top: 1.4rem; }
.card { background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 0.8rem 1rem; display: flex; flex-direction: column; gap: 0.3rem; }
.card b { font-size: 1rem; }
.card span { font-size: 0.85rem; color: var(--ink-dim); line-height: 1.4; }
.card.warn { border-color: #F5D37A; }
</style>

<!--
Not a taxonomy, a list of attribute names. You already know how to work with
those.

The values on the left are real, off the trace we just looked at.

Two Required attributes, operation name and provider name. Provider name is
how a backend knows what else to expect. The rest are Recommended or Opt-In,
and the spec has no tagged release and no schema URL yet. Build on span
attributes: they have moved much less than the metric names.

Content capture is Opt-In in the spec. Strands turns it on by default, so
tonight the prompts and answers are on the spans. Fine for a lab; think about
it before production.
-->

---

# Two instrumentations, one Bedrock call

<div class="vs">
  <div class="col">
    <div class="who">Strands (the agent framework)</div>

```
span.name                chat
gen_ai.provider.name     strands-agents
gen_ai.server.time_to_first_token   1235
gen_ai.usage.input_tokens           866
```

  </div>
  <div class="col">
    <div class="who">Botocore (the AWS SDK)</div>

```
span.name                chat us.anthropic.claude…
gen_ai.system            aws.bedrock
gen_ai.response.finish_reasons   ["tool_use"]
gen_ai.usage.input_tokens        866
```

  </div>
</div>

<div class="lessons">
  <div><b>Sum every <code>chat</code> span and your token bill doubles.</b> We saw 156 chat spans for 78 model calls.</div>
  <div><b>Neither span has everything.</b> Time to first token is only on one; finish reason is only on the other.</div>
  <div><b>They don't agree on the vocabulary.</b> <code>provider.name = strands-agents</code> on one; the spec's value, <code>aws.bedrock</code>, only as the older <code>gen_ai.system</code> on the other.</div>
</div>

<style>
.vs { display: grid; grid-template-columns: minmax(0,1fr) minmax(0,1fr); gap: 1.2rem; margin-top: 0.4rem; }
.who { font-weight: 700; margin-bottom: 0.35rem; }
.slidev-layout { --slidev-code-font-size: 0.72em; }
.lessons { display: flex; flex-direction: column; gap: 0.65rem; margin-top: 1.4rem; }
.lessons div { font-size: 1rem; color: var(--ink-dim); line-height: 1.4; padding-left: 1rem; border-left: 3px solid var(--mint); }
.lessons b { color: var(--ink); }
</style>

<!--
This is what "the conventions are still moving" looks like on a real trace.

Both instrumentations are doing their job. Strands wraps the model call and
knows about streaming, so it has time to first token. Botocore wraps the HTTP
call and reads the response, so it has the finish reason. Both record tokens.

Found it building tonight's dashboard: the token totals were exactly double.
The fix is one filter, provider.name = strands-agents, and the finish-reason
widget deliberately reads the other span. Every team running more than one
instrumentation will hit this.
-->

---

# Tokens, not dollars

<div class="cols">
<div>

<div class="big">No <code>gen_ai.usage.cost</code></div>

The conventions count tokens and stop there. There is no cost attribute; an open proposal (PR #443) would add one.

<div class="big mt-6">Tokens × list price ≠ your bill</div>

Recomputing Anthropic spend from tokens, with prompt caching in play, came out at "roughly 40% of true spend" (issue #484).

</div>
<div class="side">

<div class="card">
<b>What we do tonight</b>
<span>The agent logs one <code>agent.invocation</code> event per question with <code>cost_usd_estimate</code>: tokens × on-demand list price. The dashboard labels it <i>estimated</i>, and means it.</span>
</div>

<div class="card">
<b>What the room will see</b>
<span>Same question, same tools: Claude Haiku 4.5 at <b>$0.0057</b>, Nova Lite at <b>$0.0002</b>. Twenty-five times cheaper. Is the answer as good?</span>
</div>

</div>
</div>

<style>
.cols { display: grid; grid-template-columns: minmax(0,1.2fr) minmax(0,1fr); gap: 2rem; margin-top: 0.8rem; }
.cols p { font-size: 1.02rem; color: var(--ink-dim); line-height: 1.45; }
.big { font-family: 'Source Serif 4', Georgia, serif; font-size: 1.7rem; color: var(--ink); }
.side { display: flex; flex-direction: column; gap: 0.9rem; }
.card { background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 0.9rem 1rem; display: flex; flex-direction: column; gap: 0.3rem; }
.card b { font-size: 1rem; }
.card span { font-size: 0.88rem; color: var(--ink-dim); line-height: 1.45; }
</style>

<!--
Keep the 40% in quotes: it's verbatim from the issue.

The cost numbers on the right are from my rehearsal runs, one step-3
question each. Hand off: "let's go and make some tokens."
-->

---
layout: center
---

<SectionCard kicker="Part 2 · 25 minutes" title="Hands on: three steps" art="/img/dino-blocks.png">
  <div class="sc-list">
    <span><b>1</b> · a model behind an endpoint</span>
    <span><b>2</b> · give it tools, and one that breaks</span>
    <span><b>3</b> · give it a sub-agent, and a cheaper model</span>
  </div>
</SectionCard>

---

# Before you start

<div class="steps two">
<div>

<div class="n">1 · Docker is running</div>

<Cmd run="docker run --rm hello-world" />

<div class="n">2 · Paste your workshop AWS credentials into this terminal</div>

From the workshop page: **Get AWS CLI credentials** → copy the `export AWS_…` block → paste. Check with <code>aws sts get-caller-identity</code> if you have the CLI.

<div class="n">4 · Check everything (run on its own, wait for it)</div>

<Cmd run="docker run --rm --env-file .env ghcr.io/bronto-community/track-a-agent python doctor.py" />

<div class="hint">Three <b>ok</b> lines and you're ready.</div>

<div class="win"><b>Windows?</b> Use WSL and these commands work as they are. In plain PowerShell, the <code>.env</code> and <code>curl</code> lines are different: <b>observability-for-ai-lab.vercel.app/lab</b> has a PowerShell version of every command.</div>

</div>
<div>

<div class="n">3 · Make a folder and a <code>.env</code> file (one paste)</div>

<Cmd run="mkdir track-a && cd track-a
cat > .env <<'EOF'
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
AWS_SESSION_TOKEN
AWS_REGION=us-west-2
OTEL_EXPORTER_OTLP_HEADERS=x-bronto-api-key=KEY-FROM-YOUR-TABLE-CARD
ATTENDEE=yourname
EOF" />

<div class="hint">The three bare <code>AWS_</code> lines pass your exported credentials through to the container. <code>ATTENDEE</code> is how you'll find your own traces: lowercase, no spaces.</div>

</div>
</div>

<style>
.steps .n {
  margin: 0.8rem 0 0.3rem;
  font-family: 'Geist Mono', monospace; font-size: 0.7rem; font-weight: 600;
  text-transform: uppercase; letter-spacing: 0.12em; color: var(--sapphire);
}
.steps .n:first-child { margin-top: 0.2rem; }
.steps.two { display: grid; grid-template-columns: minmax(0,1fr) minmax(0,1.1fr); gap: 1.6rem; }
.steps .n code { font-size: 1em; text-transform: none; }
.steps p { font-size: 0.95rem; margin: 0.2rem 0; }
.hint { font-size: 0.8rem; color: var(--ink-dim); margin-top: 0.35rem; }
.win { font-size: 0.78rem; line-height: 1.4; margin-top: 0.9rem; padding: 0.5rem 0.7rem; border-radius: 10px; background: var(--surface); border: 1px solid var(--border); }
</style>

<!--
The doctor checks three things in the order they break: AWS credentials,
Bedrock model access, and the Bronto key. Three "ok" lines and you're ready.

Most raised hands: credentials pasted into a different terminal tab, or
expired. Re-copy them from the workshop page.

Windows laptops: WSL is the easy path, since every command on these slides works
unchanged. In plain PowerShell three things differ (the credential block, the .env
heredoc, and curl). The README has the PowerShell versions; point people at it
rather than live-debugging quoting. On Linux, "sudo docker" drops the
exported credentials: use "sudo -E docker".

No workshop account? Your own AWS account works: see the README, "Your own
AWS account". Nova Lite needs no model-access form.
-->

---

# Step 1 — a model behind an endpoint

<div class="cols">
<div>

<div class="n">Start it</div>

<Cmd run="docker run --rm -p 8080:8080 --env-file .env -e AGENT_STEP=1 ghcr.io/bronto-community/track-a-agent" />

<div class="keep">Keeps running: <b>leave it</b>. Ask from a <b>second terminal</b>.</div>

<div class="n">Ask it something, from a second terminal</div>

<Ask prompt="Where is order 1042, when will it arrive, and do you still have the blue ceramic mug?" />

<div class="n">It answers. It has no tools.</div>

```
I'll check those details for you right away.
<function_calls><invoke name="check_order_status">…
I apologize—I'm unable to access our order and
inventory systems at the moment…
```

</div>
<div>

<div class="n">The only telemetry code in the agent</div>

<<< @/agent/telemetry.py#traces python

<div class="n">Find it in Bronto</div>

**Traces** → filter `attendee = yourname` → open the newest trace.

<div class="look">
Look for: one <code>invoke_agent</code> span, one <code>chat</code> span, <code>gen_ai.usage.input_tokens</code> ≈ <b>91</b>.
</div>

</div>
</div>

<style>
.cols { display: grid; grid-template-columns: minmax(0,1fr) minmax(0,1fr); gap: 1.6rem; }
.n {
  margin: 0.7rem 0 0.3rem; font-family: 'Geist Mono', monospace; font-size: 0.7rem; font-weight: 600;
  text-transform: uppercase; letter-spacing: 0.12em; color: var(--sapphire);
}
.slidev-layout { --slidev-code-font-size: 0.66em; }
.slidev-layout p { font-size: 0.92rem; margin: 0.2rem 0; }
.look { font-size: 0.9rem; background: var(--mint-soft); border-radius: 10px; padding: 0.6rem 0.8rem; margin-top: 0.5rem; }
</style>

<!--
Let someone read their answer out loud. With no tools, Haiku writes the tool
calls it wishes it had, as text, then apologises. Fluent and invented. That
is what "no evidence" looks like.

The code on the right is the whole instrumentation: an OpenTelemetry tracer
provider, handed to Strands. The Dockerfile sets the endpoint to Bronto and
DISABLE_ADOT_OBSERVABILITY=true. On AgentCore, those same environment
variables are what move the telemetry from CloudWatch to Bronto.

In Bronto: Traces, filter on attendee. It's a small trace: 91 tokens in.
Remember that number.
-->

---

# Step 2 — give it tools, and one that breaks

<div class="cols">
<div>

<div class="n">Restart with step 2 (Ctrl-C first)</div>

<Cmd run="docker run --rm -p 8080:8080 --env-file .env -e AGENT_STEP=2 ghcr.io/bronto-community/track-a-agent" />

<div class="keep">Keeps running: <b>leave it</b>. Ask from a <b>second terminal</b>.</div>

<div class="n">Same question</div>

<Ask prompt="Where is order 1042, when will it arrive, and do you still have the blue ceramic mug?" out='"result": "Order 1042 has shipped with DHL and should arrive in 3 days… 12 mugs in stock"
"stats": { "input_tokens": 1925, "model_calls": 2, "tool_calls": 3, "tool_errors": 0 }' />

<div class="n">Ask it three or four more times</div>

`get_shipping_eta` times out about one call in four. Keep asking until you get one.

</div>
<div>

<div class="n">The flaky tool</div>

<<< @/agent/tools.py#flaky python

<div class="look">
Spans: find an <code>execute_tool</code> with <code>gen_ai.tool.status = error</code>.<br/>
Logs: what did the customer get told?
</div>

```sql
"$attendee" = 'yourname' AND "$tools.failed" != ''
```

</div>
</div>

<style>
.cols { display: grid; grid-template-columns: minmax(0,1fr) minmax(0,1fr); gap: 1.6rem; }
.n {
  margin: 0.7rem 0 0.3rem; font-family: 'Geist Mono', monospace; font-size: 0.7rem; font-weight: 600;
  text-transform: uppercase; letter-spacing: 0.12em; color: var(--sapphire);
}
.slidev-layout { --slidev-code-font-size: 0.66em; }
.slidev-layout p { font-size: 0.92rem; margin: 0.2rem 0; }
.look { font-size: 0.9rem; background: var(--mint-soft); border-radius: 10px; padding: 0.6rem 0.8rem; margin-top: 0.5rem; }
.small { font-size: 0.78rem; color: var(--ink-dim); }
</style>

<!--
Input tokens went from 91 to 1,925. Same question. The tool definitions and
tool results are now part of every prompt, and the agent called the model
twice: once to decide which tools to call, once to write the answer.

Tool spans exist here because Strands runs the tools. Bedrock's Converse API
hands back "please call this tool" and nothing more; it can't see the tool
run. The spec's own reference notes call execute_tool "not instrumentable"
at the Bedrock layer. The framework is the only place that span can come from.

The error span: status error, the exception message on the span. Then the
log query: every question where a tool failed, with the answer the customer
got. In rehearsal, for order 1044 (already delivered) the agent skipped
lookup_order, went straight to the carrier, hit the timeout and told the
customer to "try again". The spans say a tool failed; only the transcript
says the customer got a bad answer.
-->

---

# Step 3 — a sub-agent, and a cheaper model

<div class="cols">
<div>

<div class="n">Restart with step 3</div>

<Cmd run="docker run --rm -p 8080:8080 --env-file .env -e AGENT_STEP=3 ghcr.io/bronto-community/track-a-agent" />

<div class="keep">Keeps running: <b>leave it</b>. Ask from a <b>second terminal</b>.</div>

<div class="n">Ask with Claude Haiku 4.5 (the default)</div>

<Ask prompt="Do you have espresso cups? If not, what would you suggest instead?" />

<div class="n">Same question, Amazon Nova Lite. No restart.</div>

<Ask prompt="Do you have espresso cups? If not, what would you suggest instead?" model="us.amazon.nova-lite-v1:0" />

<div class="res">
<table>
<tr><th></th><th>tokens in / out</th><th>latency</th><th>est. cost</th></tr>
<tr><td>Haiku 4.5</td><td>3,630 / 416</td><td>6.7 s</td><td>$0.0057</td></tr>
<tr><td>Nova Lite</td><td>2,480 / 317</td><td>5.1 s</td><td>$0.0002</td></tr>
</table>
</div>

</div>
<div>

<div class="n">The sub-agent is just a tool</div>

<<< @/agent/agent.py#researcher python

</div>
</div>

<style>
.cols { display: grid; grid-template-columns: minmax(0,1.05fr) minmax(0,1fr); gap: 1.4rem; }
.n {
  margin: 0.6rem 0 0.3rem; font-family: 'Geist Mono', monospace; font-size: 0.7rem; font-weight: 600;
  text-transform: uppercase; letter-spacing: 0.12em; color: var(--sapphire);
}
.slidev-layout { --slidev-code-font-size: 0.62em; }
.res { margin-top: 0.7rem; font-size: 0.8rem; }
.res table { border-collapse: collapse; width: 100%; }
.res th, .res td { padding: 0.2rem 0.5rem; text-align: left; border-bottom: 1px solid var(--border); }
.res th { color: var(--ink-dim); font-weight: 600; font-size: 0.72rem; }
.res span { display: block; margin-top: 0.3rem; color: var(--ink-dim); font-style: italic; font-size: 0.72rem; }
</style>

<!--
Step 3 adds product_researcher: a second Strands agent with its own prompt and
one tool, wrapped as a tool of the first agent. In the trace it shows up as
execute_tool product_researcher, with a whole invoke_agent nested inside.

The table is from my rehearsal runs. Theirs will differ: that's the point.

Ask them to compare the two answers, not just the numbers. In my run Nova
Lite skipped the sub-agent, hit the flaky tool, and leaked a <thinking> block
into the customer's answer. Twenty-five times cheaper, and it shows.

Then, the question for the dashboard: one question, how many tokens? The
parent invoke_agent span doesn't include the sub-agent's tokens. You have to
add them up yourself.
-->

---
layout: center
---

<div class="ac">
  <div class="kicker">Same image, on AgentCore Runtime</div>
  <h1 class="ac-head">Only the environment changes</h1>

```bash
agentcore configure -e agent.py -n storefront_assistant -r us-west-2 \
  -rf requirements.txt --disable-otel --non-interactive \
  --deployment-type direct_code_deploy --runtime PYTHON_3_13

agentcore deploy \
  --env DISABLE_ADOT_OBSERVABILITY=true \
  --env OTEL_EXPORTER_OTLP_ENDPOINT=https://ingestion.eu.bronto.io \
  --env OTEL_EXPORTER_OTLP_PROTOCOL=http/protobuf \
  --env OTEL_EXPORTER_OTLP_HEADERS="x-bronto-api-key=…" \
  --env AGENT_STEP=3 --env ATTENDEE=agentcore
```

  <div class="ac-note">Leave those flags off and AgentCore sends the same spans to CloudWatch GenAI Observability. Pass them on <b>every</b> deploy: they aren't remembered.</div>
</div>

<style>
.ac { max-width: 52rem; }
.kicker {
  font-family: 'Geist Mono', monospace; font-size: 0.85rem; font-weight: 600;
  text-transform: uppercase; letter-spacing: 0.16em; color: var(--sapphire);
}
.ac-head { font-size: 2.6rem; margin: 0.5rem 0 1.2rem; }
.ac-note { margin-top: 1.1rem; font-size: 1rem; color: var(--ink-dim); line-height: 1.45; }
</style>

<!--
Demo only. I deployed this before the session, in a workshop account.

Why direct_code_deploy: the default container build runs in CodeBuild, and the
workshop role can't pass a role to CodeBuild (iam:PassRole is limited to
Bedrock, AgentCore, ECS, EC2, EFS) or push to ECR. Direct code deploy uploads
the code to S3 and AgentCore runs it, with no container build. Invoke it once, then filter
Bronto on attendee = agentcore: it sits on the dashboard next to everyone
else's laptop.

The agent code is identical. That is Severin's "one environment variable"
from the intro, made literal.
-->

---
layout: center
---

<SectionCard kicker="Part 3 · 5 minutes" title="The dashboard: LLM KPIs for the whole room" art="/img/dino-space.png" />

<!--
Switch to the Bronto tab: LLM KPIs — Storefront Assistant.
-->

---

# What to watch when an LLM is in production

<div class="kpis">
  <div class="kpi"><div class="k">Requests</div><div class="w">invoke_agent span count</div><p>Traffic. The denominator for everything else.</p></div>
  <div class="kpi"><div class="k">End-to-end latency P95</div><div class="w">invoke_agent duration</div><p>What the customer waits for, tools and all. Averages hide the three-loop answers.</p></div>
  <div class="kpi"><div class="k">Time to first token</div><div class="w">gen_ai.server.time_to_first_token</div><p>What a streaming user feels. Per model.</p></div>
  <div class="kpi"><div class="k">Tokens in / out, by model</div><div class="w">gen_ai.usage.*_tokens</div><p>Input grows with every loop: history and tool results ride along.</p></div>
  <div class="kpi"><div class="k">Model calls per question</div><div class="w">loop cycles per request</div><p>The multiplier on cost and latency. Creeping up = the agent is struggling.</p></div>
  <div class="kpi"><div class="k">Tool calls and tool errors</div><div class="w">execute_tool, gen_ai.tool.status</div><p>Your dependencies, seen from the agent. An error here often becomes a confident wrong answer.</p></div>
  <div class="kpi"><div class="k">Finish reasons</div><div class="w">gen_ai.response.finish_reasons</div><p><code>max_tokens</code> means a truncated answer the customer saw.</p></div>
  <div class="kpi"><div class="k">Tokens by agent</div><div class="w">invoke_agent, by gen_ai.agent.name</div><p>What the sub-agent really costs: its tokens aren't in the parent's total.</p></div>
  <div class="kpi"><div class="k">Estimated spend</div><div class="w">tokens × list price</div><p>An estimate, labelled as one. Reconcile against the bill.</p></div>
</div>

<style>
.kpis { display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.65rem; margin-top: 0.6rem; }
.kpi { background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 0.6rem 0.8rem; }
.kpi .k { font-weight: 700; font-size: 0.95rem; }
.kpi .w { font-family: 'Geist Mono', monospace; font-size: 0.64rem; color: var(--sapphire); margin: 0.15rem 0 0.25rem; }
.kpi p { font-size: 0.76rem; color: var(--ink-dim); line-height: 1.35; margin: 0; }
</style>

<!--
Walk the live dashboard in this order, then come back to this slide as the
summary. Every widget is built from the standard GenAI span attributes except
spend, which comes from the one log event per request.

Numbers from my rehearsal run of 29 questions: P95 7.7 seconds end to end,
TTFT P95 1.26 seconds, about 2 model calls per question, 5 tool errors, all
from get_shipping_eta, and $0.08 of estimated spend. The room will beat all of
those.

Point at "Tokens by attendee": who in the room spent the most?
-->

---
layout: center
---

<div class="home">
  <div class="kicker">Take it home</div>
  <h1 class="home-head">Run it again tomorrow, on your own account</h1>

  <div class="home-grid">
    <div class="sc-list">
      <span>Same image. <code>export AWS_PROFILE=you</code>, mount <code>~/.aws</code>, done.</span>
      <span>Nova Lite needs no model-access form; Claude needs a one-time use-case form.</span>
      <span>A least-privilege IAM policy is in the repo: Bedrock invoke, nothing else.</span>
      <span>Bronto: 14-day free trial, then the dashboard script rebuilds this dashboard in your org.</span>
    </div>
    <div class="qrs">
      <QrCode url="https://observability-for-ai-lab.vercel.app/lab" :size="120" caption="lab guide" />
      <QrCode url="https://github.com/bronto-community/ai-observatory-lab" :size="120" caption="the code" />
      <QrCode url="https://bronto.io/signup" :size="120" caption="bronto.io/signup" />
    </div>
  </div>
</div>

<style>
.home { max-width: 60rem; }
.kicker {
  font-family: 'Geist Mono', monospace; font-size: 0.85rem; font-weight: 600;
  text-transform: uppercase; letter-spacing: 0.16em; color: var(--sapphire);
}
.home-head { font-size: 2.5rem; margin: 0.5rem 0 1.6rem; }
.home-grid { display: flex; gap: 2.5rem; align-items: center; }
.home-grid .sc-list span { color: var(--ink); font-size: 1.05rem; }
.qrs { display: flex; gap: 1.2rem; }
</style>

<!--
Lab guide (the README, all platforms): observability-for-ai-lab.vercel.app/lab. Code: github.com/bronto-community/ai-observatory-lab.
-->

---
layout: center
---

<div class="hand">
  <div class="kicker">Next · Track B</div>
  <h1 class="hand-head">Your agent now produces evidence about itself.</h1>
  <div class="hand-sub">Next, Severin builds an agent that consumes evidence about your system: an AI SRE on AgentCore, reading Bronto.</div>
  <div class="hand-sub small">Same runtime, opposite direction.</div>
  <a class="next-link" href="https://ai-observatory-lab.vercel.app/track-b" target="_top">Continue to Track B: build your own AI SRE →</a>
</div>

<img src="/img/bronto-dino.png" class="abs-br mr-12 mb-10 hand-dino" />

<style>
.hand { max-width: 48rem; }
.kicker {
  font-family: 'Geist Mono', monospace; font-size: 0.85rem; font-weight: 600;
  text-transform: uppercase; letter-spacing: 0.16em; color: var(--sapphire);
}
.hand-head { font-size: 2.7rem; margin: 0.5rem 0 1.2rem; }
.hand-sub { font-size: 1.2rem; color: var(--ink-dim); line-height: 1.45; }
.hand-sub.small { margin-top: 0.8rem; font-size: 1rem; font-style: italic; }
.hand-dino { width: 110px; }
.next-link {
  display: inline-block; margin-top: 1.8rem; padding: 0.6rem 1.1rem; border-radius: 10px;
  background: var(--sapphire); color: #fff !important; font-weight: 700; text-decoration: none !important;
}
</style>

<!--
One line and go: "It's a production system now. It's non-deterministic and
it won't explain itself, unless you make it. Food, then Severin."
-->

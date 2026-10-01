import Link from "next/link";
import { Requirements } from "@/components/Guide";
import { SetupChooser } from "@/components/SetupChooser";

const SESSIONS = [
  {
    href: "/intro",
    kicker: "Talk · 25 min",
    title: "An Evening at the AI Observatory",
    go: "Watch the talk",
    covers: [
      "Two readings of one title: observability for AI, and AI for observability",
      "An agent as a service in someone's request, and the vocabulary it needs: tokens, tool calls, prompts",
      "The OpenTelemetry GenAI conventions, and frameworks that already emit them",
      "What a model is good at in an incident, and what it can't see",
    ],
    outcomes: [
      "A shared vocabulary for the two labs",
      "Knowing which lab answers which question",
    ],
  },
  {
    href: "/track-a",
    kicker: "Track A · lab · about 40 min",
    title: "Observability for AI",
    go: "Start Track A",
    covers: [
      "Run a Strands customer-assistant agent in Docker, on Amazon Bedrock or your own LLM key",
      "Send its OpenTelemetry GenAI traces, logs and metrics to your own Bronto",
      "Add tools (one fails on purpose), then a sub-agent, then compare two models",
      "Build a ready-made LLM KPI dashboard",
    ],
    outcomes: [
      "Find any model call, tool call and token count in a trace",
      "Explain why input tokens grow with every tool call",
      "Spot a failing tool, and see what the customer was told",
      "Compare models on latency, tokens and estimated cost",
      "Keep an LLM KPI dashboard in your Bronto account",
    ],
  },
  {
    href: "/track-b",
    kicker: "Track B · lab · about 45 min · by Severin Neumann",
    title: "AI for Observability",
    go: "Start Track B",
    covers: [
      "Build an AI SRE in seven steps: a loop, an identity, eyes, a mouth, better instructions, another model, the code",
      "Give it Bronto MCP to read telemetry, and GitHub to file its findings and read source code",
      "Point it at a live incident: Storefront's checkout slows down every hour after a release",
    ],
    outcomes: [
      "A working investigating agent that files a GitHub issue with its hypothesis and evidence",
      "See how instructions and model choice change its conclusions",
      "Know what a managed agent such as AWS DevOps Agent does for you, and what it can't see",
    ],
  },
];

export default function Home() {
  return (
    <div className="landing">
      <section className="hero">
        <div>
          <div className="kicker">Self-paced · AWS + Bronto</div>
          <h1>An Evening at the AI Observatory, at your own pace</h1>
          <p className="lead">
            A talk and two hands-on labs from the live event. First, watch an AI agent think: every model call, tool
            call and token as OpenTelemetry traces in Bronto. Then build an AI SRE that reads telemetry and works an
            incident.
          </p>
          <p>You run everything yourself: your own Bronto account, and an LLM from your AWS account or your own OpenAI, Anthropic or Google key. It costs nothing to start.</p>
          <a href="#setup" className="cta">Choose your setup →</a>
        </div>
        <img src="/img/dino-scientist.png" alt="The Bronto dinosaur in a lab coat" className="lineart" />
      </section>

      <h2>The three sessions</h2>
      <div className="sessions">
        {SESSIONS.map((s) => (
          <article key={s.href} className="session">
            <span className="kicker">{s.kicker}</span>
            <h3>{s.title}</h3>
            <div className="session-cols">
              <div>
                <h4>What it covers</h4>
                <ul>{s.covers.map((c) => <li key={c}>{c}</li>)}</ul>
              </div>
              <div>
                <h4>You come away with</h4>
                <ul>{s.outcomes.map((o) => <li key={o}>{o}</li>)}</ul>
              </div>
            </div>
            <Link href={s.href} className="go">{s.go} →</Link>
          </article>
        ))}
      </div>

      <h2>Choose your setup</h2>
      <p>
        Pick what you&rsquo;ll use. Every page then shows the commands for your choices, and the site remembers them.
      </p>
      <SetupChooser />
      <p><Link href="/start" className="cta">Start the setup →</Link></p>

      <h2>What you need</h2>
      <Requirements />

      <section className="offers" aria-label="What you start with">
        <div className="offer">
          <div className="kicker">Bronto</div>
          <div className="big">Free trial, no credit card</div>
          <p>Logs, traces and metrics, with the Bronto MCP server for agents. Sign up with Google or email at <a href="https://bronto.io/signup" target="_blank" rel="noopener">bronto.io/signup</a>.</p>
        </div>
        <div className="offer">
          <div className="kicker">Your LLM</div>
          <div className="big">AWS Bedrock, or your own key</div>
          <p>
            Run the agents on Amazon Bedrock in your AWS account, using models that need no access form, or bring an
            API key from OpenAI, Anthropic or Google. No key yet? Google Gemini&rsquo;s{" "}
            <a href="https://ai.google.dev/gemini-api/docs/billing" target="_blank" rel="noopener">free tier</a> covers both
            labs. New to AWS? See the current offer at{" "}
            <a href="https://aws.amazon.com/free/" target="_blank" rel="noopener">aws.amazon.com/free</a>.
          </p>
        </div>
      </section>

      <h2>Everything in one place</h2>
      <ul className="resources">
        <li><Link href="/start">Setup: Bronto, your LLM, Docker, <code>.env</code></Link></li>
        <li><Link href="/byo-llm">Use your own OpenAI, Anthropic or Google key</Link></li>
        <li><a href="https://ai-observatory-talk.vercel.app" target="_blank" rel="noopener">Intro talk deck ↗</a></li>
        <li><a href="https://observability-for-ai-lab.vercel.app" target="_blank" rel="noopener">Track A deck ↗</a></li>
        <li><a href="https://aisre-lab.vercel.app" target="_blank" rel="noopener">Track B deck ↗</a></li>
        <li><a href="https://github.com/bronto-community/track-a-observability-for-ai" target="_blank" rel="noopener">Lab code on GitHub ↗</a></li>
        <li><Link href="/agentcore">Deploy to AgentCore Runtime (Paid plan)</Link></li>
        <li><Link href="/cleanup">Clean up when you&rsquo;re done</Link></li>
      </ul>
    </div>
  );
}

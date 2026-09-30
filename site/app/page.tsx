import Link from "next/link";

export default function Home() {
  return (
    <div className="landing">
      <section className="hero">
        <div>
          <div className="kicker">Self-paced · AWS + Bronto</div>
          <h1>An Evening at the AI Observatory, at your own pace</h1>
          <p className="lead">
            Two hands-on labs from the live event. First, watch an AI agent think: every model call, tool call and
            token as OpenTelemetry traces in Bronto. Then build an AI SRE that reads telemetry and works an incident.
          </p>
          <p>You run everything yourself, in your own AWS account and your own Bronto trial. It costs nothing to start.</p>
          <Link href="/start" className="cta">Start here →</Link>
        </div>
        <img src="/img/dino-scientist.png" alt="The Bronto dinosaur in a lab coat" />
      </section>

      <section className="offers" aria-label="Free offers">
        <div className="offer">
          <div className="kicker">Bronto</div>
          <div className="big">14 days free, no credit card</div>
          <p>Logs, traces and metrics, with the Bronto MCP server for agents. Sign up with Google or email at <a href="https://bronto.io/signup" target="_blank" rel="noopener">bronto.io/signup</a>.</p>
        </div>
        <div className="offer">
          <div className="kicker">AWS</div>
          <div className="big">Up to $200 in credits</div>
          <p>
            New accounts get $100 on sign-up, plus $20 each for up to five getting-started activities. One of them is
            trying a model in the <strong>Amazon Bedrock playground</strong>. The Free plan never charges you.{" "}
            <a href="https://aws.amazon.com/free/" target="_blank" rel="noopener">aws.amazon.com/free</a>
          </p>
        </div>
      </section>

      <h2>The three sessions</h2>
      <div className="cards">
        <Link href="/intro" className="card">
          <span className="kicker">25 min · talk</span>
          <h3>An Evening at the AI Observatory</h3>
          <p>Why AI sits on both sides of observability: agents as systems to observe, and agents as the ones doing the observing.</p>
          <span className="go">Watch the deck →</span>
        </Link>
        <Link href="/track-a" className="card">
          <span className="kicker">Track A · lab</span>
          <h3>Observability for AI</h3>
          <p>Run a Strands agent on Amazon Bedrock and see its GenAI traces, tokens, tool errors and sub-agent in Bronto. Then the LLM KPI dashboard.</p>
          <span className="go">Start Track A →</span>
        </Link>
        <Link href="/track-b" className="card">
          <span className="kicker">Track B · lab</span>
          <h3>AI for Observability</h3>
          <p>Build your own AI SRE in seven steps: identity, Bronto MCP for eyes, GitHub for the code and the report, against a live incident.</p>
          <span className="go">Start Track B →</span>
        </Link>
      </div>

      <h2>Everything in one place</h2>
      <ul className="resources">
        <li><Link href="/start">Setup: accounts, AWS CLI, Docker, <code>.env</code></Link></li>
        <li><Link href="/byo-llm">Use your own OpenAI, Anthropic or Google key</Link></li>
        <li><a href="https://ai-observatory-talk.vercel.app" target="_blank" rel="noopener">Intro talk deck ↗</a></li>
        <li><a href="https://observability-for-ai-lab.vercel.app" target="_blank" rel="noopener">Track A deck ↗</a></li>
        <li><a href="https://aisre-lab.vercel.app" target="_blank" rel="noopener">Track B deck ↗</a></li>
        <li><a href="https://github.com/bronto-community/track-a-observability-for-ai" target="_blank" rel="noopener">Track A code on GitHub ↗</a></li>
        <li><Link href="/agentcore">Deploy to AgentCore Runtime (Paid plan)</Link></li>
        <li><Link href="/cleanup">Clean up when you&rsquo;re done</Link></li>
      </ul>
    </div>
  );
}

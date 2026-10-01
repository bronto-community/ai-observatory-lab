import Link from "next/link";
import type { ReactNode } from "react";

// A numbered step. `then` says what to wait for before moving on, because
// people paste several boxes at once otherwise.
export function Step({ n, title, then, children }: { n: number | string; title: string; then?: string; children?: ReactNode }) {
  return (
    <section className="step">
      <div className="step-n" aria-hidden>{n}</div>
      <div className="step-body">
        <h3>{title}</h3>
        {children}
        {then && <p className="step-then"><strong>Then:</strong> {then}</p>}
      </div>
    </section>
  );
}

export function Steps({ children }: { children: ReactNode }) {
  return <div className="steps">{children}</div>;
}

type Tone = "note" | "warn" | "tip";
export function Callout({ tone = "note", title, children }: { tone?: Tone; title?: string; children: ReactNode }) {
  return (
    <aside className={`callout callout-${tone}`}>
      {title && <strong className="callout-title">{title}</strong>}
      <div>{children}</div>
    </aside>
  );
}

export function OneAtATime() {
  return (
    <Callout tone="warn" title="Run one box at a time">
      Paste a box, press Enter, and wait for it to finish before the next one. The agent command keeps running
      in its terminal, so anything pasted after it never runs: ask your questions from a <strong>second terminal</strong>.
    </Callout>
  );
}

// An embedded Slidev deck, with a link out for full screen.
export function Deck({ src, title }: { src: string; title: string }) {
  return (
    <figure className="deck">
      <div className="deck-frame">
        <iframe src={src} title={title} loading="lazy" allow="fullscreen; clipboard-write" />
      </div>
      <figcaption>
        {title} · <a href={src} target="_blank" rel="noopener">open full screen ↗</a> · arrow keys to move
      </figcaption>
    </figure>
  );
}

export function NextPage({ href, label }: { href: string; label: string }) {
  return (
    <p className="next-page">
      <Link href={href}>Next: {label} →</Link>
    </p>
  );
}

// What a learner needs, shown on the landing page and at the top of /start.
export function Requirements() {
  return (
    <table className="reqs">
      <thead>
        <tr><th>You need</th><th>What for</th><th>Labs</th></tr>
      </thead>
      <tbody>
        <tr>
          <td>A Bronto account</td>
          <td>
            <strong>Your own</strong>, EU or US: a new <a href="https://bronto.io/signup" target="_blank" rel="noopener">trial</a>{" "}
            (no credit card) or one you already have, with two API keys you create: <strong>ingestion</strong> and{" "}
            <strong>dashboards</strong>. Track A sends your agent&rsquo;s telemetry here. Track B doesn&rsquo;t use it:
            its agent reads a <strong>shared Bronto demo org</strong> with a read-only key we provide.
          </td>
          <td className="who">Track A</td>
        </tr>
        <tr>
          <td>An LLM, one of</td>
          <td>
            <strong>An AWS account</strong> for Amazon Bedrock (new or existing), <strong>or your own API key</strong> from OpenAI, Anthropic or Google. No key? Google Gemini&rsquo;s free tier covers both labs.
          </td>
          <td className="who">A and B</td>
        </tr>
        <tr>
          <td>Docker</td>
          <td>Docker Desktop, OrbStack, Colima or Docker Engine. Every agent runs as a container.</td>
          <td className="who">A and B</td>
        </tr>
        <tr>
          <td>The AWS CLI v2</td>
          <td>Only on the AWS route: it signs you in and hands the credentials to the container.</td>
          <td className="who">If AWS</td>
        </tr>
        <tr>
          <td>A GitHub account</td>
          <td>An empty public repository for the agent&rsquo;s reports, and a fine-grained token for it.</td>
          <td className="who">Track B</td>
        </tr>
      </tbody>
    </table>
  );
}

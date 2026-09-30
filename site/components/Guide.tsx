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

import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";

export const metadata: Metadata = {
  title: { default: "AI Observatory", template: "%s · AI Observatory" },
  description:
    "Self-paced labs from the AWS + Bronto evening: observe an AI agent with OpenTelemetry, then build an AI SRE that reads your telemetry.",
};

const NAV = [
  { href: "/start", label: "Start" },
  { href: "/intro", label: "Intro talk" },
  { href: "/track-a", label: "Track A" },
  { href: "/track-b", label: "Track B" },
  { href: "/byo-llm", label: "Your own LLM key" },
];

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="" />
        {/* eslint-disable-next-line @next/next/no-page-custom-font */}
        <link
          href="https://fonts.googleapis.com/css2?family=Geist+Mono:wght@400;600&family=Radio+Canada+Big:wght@400;600;700&family=Source+Serif+4:wght@500;600&display=swap"
          rel="stylesheet"
        />
      </head>
      <body>
        <header className="site-header">
          <Link href="/" className="brand">
            <img src="/img/bronto-dino.png" alt="" width={28} height={28} />
            <span>AI Observatory</span>
          </Link>
          <nav aria-label="Main">
            {NAV.map((n) => (
              <Link key={n.href} href={n.href}>{n.label}</Link>
            ))}
          </nav>
        </header>
        <main>{children}</main>
        <footer className="site-footer">
          <span>
            From the AWS + Bronto evening, &ldquo;An Evening at the AI Observatory&rdquo;.
          </span>
          <span>
            <a href="https://github.com/bronto-community/track-a-observability-for-ai" target="_blank" rel="noopener">Source on GitHub</a>
            {" · "}
            <Link href="/agentcore">AgentCore (Paid plan)</Link>
            {" · "}
            <Link href="/cleanup">Clean up</Link>
            {" · "}
            <a href="https://bronto.io" target="_blank" rel="noopener">bronto.io</a>
          </span>
        </footer>
      </body>
    </html>
  );
}

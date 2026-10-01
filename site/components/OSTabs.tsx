"use client";

import { Children, isValidElement, useEffect, useState, type ReactElement, type ReactNode } from "react";

// Two shared choices, each remembered in this browser and kept in sync across
// every tab set on the site:
//   OSTabs   "macOS / Linux" vs "Windows (PowerShell)"
//   LLMTabs  "AWS Bedrock" vs "Your own API key"
export function Tab({ children }: { label: string; children: ReactNode }) {
  return <>{children}</>;
}

function SharedTabs({ group, children, guess }: { group: string; children: ReactNode; guess?: (labels: string[]) => string | null }) {
  const key = `ai-observatory-${group}`;
  const event = `${key}-change`;
  const tabs = Children.toArray(children).filter(isValidElement) as ReactElement<{ label: string; children: ReactNode }>[];
  const labels = tabs.map((t) => t.props.label);
  const [active, setActive] = useState(labels[0]);

  useEffect(() => {
    let saved: string | null = null;
    try { saved = localStorage.getItem(key); } catch {}
    if (!saved && guess) saved = guess(labels);
    if (saved && labels.includes(saved)) setActive(saved);
    const onChange = (e: Event) => {
      const v = (e as CustomEvent<string>).detail;
      if (labels.includes(v)) setActive(v);
    };
    window.addEventListener(event, onChange);
    return () => window.removeEventListener(event, onChange);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  function pick(label: string) {
    setActive(label);
    try { localStorage.setItem(key, label); } catch {}
    window.dispatchEvent(new CustomEvent(event, { detail: label }));
  }

  return (
    <div className={`tabs tabs-${group}`}>
      <div className="tab-bar" role="tablist">
        {labels.map((l) => (
          <button key={l} type="button" role="tab" aria-selected={l === active} className={l === active ? "on" : ""} onClick={() => pick(l)}>
            {l}
          </button>
        ))}
      </div>
      {tabs.map((t) => (
        <div key={t.props.label} role="tabpanel" hidden={t.props.label !== active}>
          {t.props.children}
        </div>
      ))}
    </div>
  );
}

export function OSTabs({ children }: { children: ReactNode }) {
  return (
    <SharedTabs group="os" guess={(labels) => (/Win/i.test(navigator.platform) ? labels.find((l) => /windows/i.test(l)) ?? null : null)}>
      {children}
    </SharedTabs>
  );
}

export function LLMTabs({ children }: { children: ReactNode }) {
  return <SharedTabs group="llm">{children}</SharedTabs>;
}

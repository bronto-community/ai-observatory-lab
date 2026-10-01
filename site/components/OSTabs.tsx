"use client";

import { Children, isValidElement, type ReactElement, type ReactNode } from "react";
import { usePref, type PrefKey } from "./prefs";

// Tab sets that follow the learner's setup (see prefs.ts): picking a tab here
// changes it everywhere, including the setup chooser.
//   OSTabs   "macOS / Linux" vs "Windows (PowerShell)"
//   LLMTabs  "AWS Bedrock" vs "Your own API key"
export function Tab({ children }: { label: string; children: ReactNode }) {
  return <>{children}</>;
}

function SharedTabs({ pref, children }: { pref: PrefKey; children: ReactNode }) {
  const tabs = Children.toArray(children).filter(isValidElement) as ReactElement<{ label: string; children: ReactNode }>[];
  const labels = tabs.map((t) => t.props.label);
  const [value, setValue] = usePref(pref);
  const active = labels.includes(value) ? value : labels[0];

  return (
    <div className={`tabs tabs-${pref}`}>
      <div className="tab-bar" role="tablist">
        {labels.map((l) => (
          <button key={l} type="button" role="tab" aria-selected={l === active} className={l === active ? "on" : ""} onClick={() => setValue(l)}>
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
  return <SharedTabs pref="os">{children}</SharedTabs>;
}

export function LLMTabs({ children }: { children: ReactNode }) {
  return <SharedTabs pref="llm">{children}</SharedTabs>;
}

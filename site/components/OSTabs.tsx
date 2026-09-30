"use client";

import { Children, isValidElement, useEffect, useState, type ReactElement, type ReactNode } from "react";

// "macOS / Linux" vs "Windows (PowerShell)". The choice is shared by every
// tab set on the site and remembered in this browser.
const KEY = "ai-observatory-os";
const EVENT = "ai-observatory-os-change";

export function Tab({ children }: { label: string; children: ReactNode }) {
  return <>{children}</>;
}

export function OSTabs({ children }: { children: ReactNode }) {
  const tabs = Children.toArray(children).filter(isValidElement) as ReactElement<{ label: string; children: ReactNode }>[];
  const labels = tabs.map((t) => t.props.label);
  const [active, setActive] = useState(labels[0]);

  useEffect(() => {
    let saved: string | null = null;
    try { saved = localStorage.getItem(KEY); } catch {}
    if (!saved && /Win/i.test(navigator.platform)) saved = labels.find((l) => /windows/i.test(l)) ?? null;
    if (saved && labels.includes(saved)) setActive(saved);
    const onChange = (e: Event) => {
      const v = (e as CustomEvent<string>).detail;
      if (labels.includes(v)) setActive(v);
    };
    window.addEventListener(EVENT, onChange);
    return () => window.removeEventListener(EVENT, onChange);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  function pick(label: string) {
    setActive(label);
    try { localStorage.setItem(KEY, label); } catch {}
    window.dispatchEvent(new CustomEvent(EVENT, { detail: label }));
  }

  return (
    <div className="tabs">
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

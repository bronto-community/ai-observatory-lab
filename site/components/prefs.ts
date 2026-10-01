"use client";

import { useEffect, useState } from "react";

// The learner's setup, remembered in this browser. Every tab set, code block
// and chooser on the site reads and writes the same values, and a change in
// one place updates the others straight away.
export const PREFS = {
  llm: { label: "Your LLM", options: ["AWS Bedrock", "Your own API key"] },
  provider: { label: "Your API key is from", options: ["Google Gemini", "OpenAI", "Anthropic"] },
  os: { label: "Your computer", options: ["macOS / Linux", "Windows (PowerShell)"] },
  region: { label: "Your Bronto account is in", options: ["EU", "US"] },
} as const;

export type PrefKey = keyof typeof PREFS;

const storageKey = (k: PrefKey) => `ai-observatory-${k}`;
const eventName = (k: PrefKey) => `ai-observatory-${k}-change`;

function guess(k: PrefKey): string | null {
  if (k === "os" && typeof navigator !== "undefined" && /Win/i.test(navigator.platform)) return PREFS.os.options[1];
  return null;
}

export function readPref(k: PrefKey): string {
  let v: string | null = null;
  try { v = localStorage.getItem(storageKey(k)); } catch {}
  const options = PREFS[k].options as readonly string[];
  if (v && options.includes(v)) return v;
  return guess(k) ?? options[0];
}

export function writePref(k: PrefKey, v: string) {
  try { localStorage.setItem(storageKey(k), v); } catch {}
  window.dispatchEvent(new CustomEvent(eventName(k), { detail: v }));
}

// [value, setValue]. Renders the first option on the server, then the saved one.
export function usePref(k: PrefKey): [string, (v: string) => void] {
  const [value, setValue] = useState<string>(PREFS[k].options[0]);
  useEffect(() => {
    setValue(readPref(k));
    const on = (e: Event) => setValue((e as CustomEvent<string>).detail);
    window.addEventListener(eventName(k), on);
    return () => window.removeEventListener(eventName(k), on);
  }, [k]);
  return [value, (v: string) => writePref(k, v)];
}

// The .env lines a code block shows depend on the provider and region chosen.
const PROVIDER_LINES: Record<string, [string, string]> = {
  "Google Gemini": ["gemini", "GEMINI_API_KEY"],
  OpenAI: ["openai", "OPENAI_API_KEY"],
  Anthropic: ["anthropic", "ANTHROPIC_API_KEY"],
};

export function personalise(text: string, provider: string, region: string): string {
  const [name, key] = PROVIDER_LINES[provider] ?? PROVIDER_LINES["Google Gemini"];
  return text
    .replace(/LLM_PROVIDER=gemini(\r?\n)GEMINI_API_KEY=/g, `LLM_PROVIDER=${name}$1${key}=`)
    .replace(/BRONTO_REGION=eu\b/g, `BRONTO_REGION=${region.toLowerCase()}`)
    .replace(/ingestion\.eu\.bronto\.io/g, `ingestion.${region.toLowerCase()}.bronto.io`);
}

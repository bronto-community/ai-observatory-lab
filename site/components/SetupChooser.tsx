"use client";

import Link from "next/link";
import { PREFS, usePref, type PrefKey } from "./prefs";

const HINTS: Partial<Record<string, string>> = {
  "AWS Bedrock": "Amazon Nova and gpt-oss on Bedrock, in your AWS account. Needs the AWS CLI.",
  "Your own API key": "No AWS account needed.",
  "Google Gemini": "Its free tier covers both labs.",
  OpenAI: "Needs prepaid credit.",
  Anthropic: "Needs prepaid credit.",
  EU: "app.eu.bronto.io",
  US: "app.us.bronto.io",
};

function Group({ k, disabled }: { k: PrefKey; disabled?: boolean }) {
  const [value, setValue] = usePref(k);
  const { label, options } = PREFS[k];
  return (
    <fieldset className="choice" disabled={disabled}>
      <legend>{label}</legend>
      {options.map((o) => (
        <label key={o} className={o === value ? "on" : ""}>
          <input type="radio" name={`setup-${k}`} value={o} checked={o === value} onChange={() => setValue(o)} />
          <span>
            <strong>{o}</strong>
            {HINTS[o] && <small>{HINTS[o]}</small>}
          </span>
        </label>
      ))}
    </fieldset>
  );
}

// The learner's setup. The choices are remembered in this browser and every
// command on the site follows them.
export function SetupChooser() {
  const [llm] = usePref("llm");
  return (
    <section className="chooser" id="setup" aria-label="Your setup">
      <Group k="llm" />
      <Group k="provider" disabled={llm !== "Your own API key"} />
      <Group k="os" />
      <Group k="region" />
      <p className="chooser-note">
        Saved in this browser. Every command on the site follows these choices, and you can change them here or on any
        tab.
      </p>
    </section>
  );
}

// One line on the lab pages: what the commands below assume, and where to change it.
export function SetupSummary() {
  const [llm] = usePref("llm");
  const [provider] = usePref("provider");
  const [os] = usePref("os");
  const [region] = usePref("region");
  const model = llm === "AWS Bedrock" ? "AWS Bedrock" : provider;
  return (
    <p className="setup-summary">
      Your setup: <strong>{model}</strong> · <strong>{os}</strong> · Bronto <strong>{region}</strong>{" "}
      <Link href="/#setup">change</Link>
    </p>
  );
}

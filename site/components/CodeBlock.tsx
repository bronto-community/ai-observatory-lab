"use client";

import { Children, cloneElement, isValidElement, useRef, useState, type ComponentProps, type ReactNode } from "react";
import { personalise, usePref } from "./prefs";

// Every fenced code block gets a copy button. Copies the block's text exactly,
// so one box = one thing to paste. The text follows the learner's setup: their
// LLM provider's .env lines and their Bronto region.
function rewrite(node: ReactNode, fix: (s: string) => string): ReactNode {
  return Children.map(node, (child) => {
    if (typeof child === "string") return fix(child);
    if (isValidElement<{ children?: ReactNode }>(child) && child.props.children !== undefined) {
      return cloneElement(child, undefined, rewrite(child.props.children, fix));
    }
    return child;
  });
}

export function CodeBlock({ children, ...props }: ComponentProps<"pre">) {
  const ref = useRef<HTMLPreElement>(null);
  const [label, setLabel] = useState("Copy");
  const [provider] = usePref("provider");
  const [region] = usePref("region");

  async function copy() {
    const text = ref.current?.innerText.replace(/\n$/, "") ?? "";
    try {
      await navigator.clipboard.writeText(text);
      setLabel("Copied");
    } catch {
      setLabel("Select and copy");
    }
    setTimeout(() => setLabel("Copy"), 1400);
  }

  return (
    <div className="code">
      <pre ref={ref} {...props}>{rewrite(children, (s) => personalise(s, provider, region))}</pre>
      <button type="button" className="copy" onClick={copy} aria-label="Copy to clipboard">
        {label}
      </button>
    </div>
  );
}

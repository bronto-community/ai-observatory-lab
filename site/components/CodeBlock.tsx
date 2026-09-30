"use client";

import { useRef, useState, type ComponentProps } from "react";

// Every fenced code block gets a copy button. Copies the block's text exactly,
// so one box = one thing to paste.
export function CodeBlock(props: ComponentProps<"pre">) {
  const ref = useRef<HTMLPreElement>(null);
  const [label, setLabel] = useState("Copy");

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
      <pre ref={ref} {...props} />
      <button type="button" className="copy" onClick={copy} aria-label="Copy to clipboard">
        {label}
      </button>
    </div>
  );
}

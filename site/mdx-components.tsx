import type { MDXComponents } from "mdx/types";
import { CodeBlock } from "@/components/CodeBlock";
import { Callout, Deck, NextPage, OneAtATime, Requirements, Step, Steps } from "@/components/Guide";
import { LLMTabs, OSTabs, Tab } from "@/components/OSTabs";

const components: MDXComponents = {
  pre: CodeBlock,
  a: ({ href = "", ...props }) =>
    /^https?:\/\//.test(href) ? <a href={href} target="_blank" rel="noopener" {...props} /> : <a href={href} {...props} />,
  Callout,
  Deck,
  LLMTabs,
  NextPage,
  OneAtATime,
  OSTabs,
  Requirements,
  Step,
  Steps,
  Tab,
};

export function useMDXComponents(): MDXComponents {
  return components;
}

#!/usr/bin/env python3
"""Render ../README.md as the /lab page of the slides site.

    uvx --from markdown python build-lab-page.py <output-dir>

Writes <output-dir>/lab/index.html. Relative links in the README (files in
the repo) are pointed at the public GitHub repo so they work from the site.
"""

import re
import sys
from pathlib import Path

import markdown

REPO = "https://github.com/bronto-community/track-a-observability-for-ai"
HERE = Path(__file__).resolve().parent

md = (HERE.parent / "README.md").read_text()
md = re.sub(r"\]\((?!https?://|#)([^)]+)\)", lambda m: f"]({REPO}/blob/main/{m.group(1)})", md)
body = markdown.markdown(md, extensions=["fenced_code", "tables", "sane_lists", "toc"])

page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Track A lab guide</title>
<meta name="description" content="Run the Observability for AI lab on macOS, Linux or Windows, in the workshop account or your own.">
<link rel="icon" href="/img/bronto-dino.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Radio+Canada+Big:wght@400;600;700&family=Source+Serif+4:wght@500&family=Geist+Mono:wght@400;600&display=swap" rel="stylesheet">
<style>
:root {{
  --bg: #FAF8F4; --surface: #FFFFFF; --ink: #2B2620; --ink-dim: #6F665A;
  --border: #E7E0D4; --sapphire: #476BFF; --code-bg: #F3EFE8;
}}
@media (prefers-color-scheme: dark) {{
  :root:not([data-theme="light"]) {{
    --bg: #17150F; --surface: #211E18; --ink: #EDE7DC; --ink-dim: #A89F92;
    --border: #3A352C; --sapphire: #8FA6FF; --code-bg: #26221B;
  }}
}}
:root[data-theme="dark"] {{
  --bg: #17150F; --surface: #211E18; --ink: #EDE7DC; --ink-dim: #A89F92;
  --border: #3A352C; --sapphire: #8FA6FF; --code-bg: #26221B;
}}
* {{ box-sizing: border-box; }}
body {{
  margin: 0; background: var(--bg); color: var(--ink);
  font: 17px/1.6 'Radio Canada Big', system-ui, sans-serif;
}}
main {{ max-width: 52rem; margin: 0 auto; padding: 2.5rem 16px 5rem; }}
.top {{ display: flex; align-items: center; gap: 0.75rem; margin-bottom: 2rem; font-size: 0.9rem; }}
.top img {{ width: 28px; height: 28px; }}
.top a {{ color: var(--ink-dim); text-decoration: none; }}
.top a:hover {{ color: var(--sapphire); }}
h1, h2 {{ font-family: 'Source Serif 4', Georgia, serif; font-weight: 500; letter-spacing: -0.01em; line-height: 1.15; }}
h1 {{ font-size: 2.4rem; margin: 0 0 1rem; }}
h2 {{ font-size: 1.7rem; margin: 2.8rem 0 0.8rem; padding-top: 1.2rem; border-top: 1px solid var(--border); }}
h3 {{ font-size: 1.15rem; margin: 2rem 0 0.6rem; }}
a {{ color: var(--sapphire); }}
code {{ font-family: 'Geist Mono', ui-monospace, monospace; font-size: 0.86em; background: var(--code-bg); padding: 0.1em 0.35em; border-radius: 4px; overflow-wrap: anywhere; }}
pre {{ position: relative; background: var(--code-bg); border: 1px solid var(--border); border-radius: 10px; padding: 0.9rem 1rem; overflow-x: auto; }}
pre code {{ background: none; padding: 0; font-size: 0.82rem; line-height: 1.55; overflow-wrap: normal; }}
.copy {{ position: absolute; top: 0.4rem; right: 0.4rem; border: 1px solid var(--border); background: var(--surface); color: var(--ink-dim); border-radius: 6px; font: 600 0.72rem 'Geist Mono', monospace; padding: 0.25rem 0.5rem; cursor: pointer; }}
.copy:hover {{ color: var(--sapphire); }}
table {{ border-collapse: collapse; width: 100%; display: block; overflow-x: auto; font-size: 0.92rem; }}
th, td {{ border-bottom: 1px solid var(--border); padding: 0.45rem 0.6rem; text-align: left; vertical-align: top; }}
th {{ color: var(--ink-dim); font-weight: 600; }}
li {{ margin: 0.25rem 0; }}
strong {{ font-weight: 700; }}
</style>
</head>
<body>
<main>
<div class="top">
  <img src="/img/bronto-dino.png" alt="">
  <a href="/">← Slides</a> · <a href="{REPO}">GitHub repo</a>
</div>
<aside style="background:var(--code-bg);border:1px solid var(--border);border-radius:10px;padding:0.8rem 1rem;margin-bottom:1.5rem">
  <strong>Doing this on your own?</strong> The self-paced edition, with your own AWS and Bronto accounts, both
  labs and all three decks, is at <a href="https://ai-observatory-lab.vercel.app">ai-observatory-lab.vercel.app</a>.
</aside>
{body}
</main>
<script>
document.querySelectorAll('pre').forEach(pre => {{
  const b = document.createElement('button');
  b.className = 'copy'; b.type = 'button'; b.textContent = 'copy';
  b.onclick = async () => {{
    try {{ await navigator.clipboard.writeText(pre.querySelector('code').innerText); b.textContent = 'copied'; }}
    catch (e) {{ b.textContent = 'select + copy'; }}
    setTimeout(() => b.textContent = 'copy', 1400);
  }};
  pre.appendChild(b);
}});
</script>
</body>
</html>
"""

out = Path(sys.argv[1]) / "lab"
out.mkdir(parents=True, exist_ok=True)
(out / "index.html").write_text(page)
print(f"wrote {out / 'index.html'}")

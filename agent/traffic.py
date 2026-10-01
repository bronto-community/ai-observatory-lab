"""Send a mix of customer questions to the local agent, so your dashboard has
something to show. Usage: docker compose run --rm traffic  (N=20 by default)."""

import json
import os
import random
import re
import time
import urllib.request

URL = os.environ.get("AGENT_URL", "http://localhost:8080/invocations")
N = int(os.environ.get("N", "20"))
MODELS = [m for m in os.environ.get("MODELS", "").split(",") if m]

QUESTIONS = [
    "Where is order 1042 and when will it arrive?",
    "Has order 1043 shipped yet?",
    "Do you have espresso cups? If not, what would you suggest instead?",
    "Is the walnut cutting board in stock?",
    "I want a french press. Any in stock, or something similar?",
    "What's the status of order 1045?",
    "When will order 1044 get here?",
    "Do you sell linen aprons, and how many do you have?",
    "Order 9999 never arrived, can you check it?",
    "Recommend a gift under the kitchen theme that is in stock right now.",
]



def short(model_id: str) -> str:
    """us.amazon.nova-2-lite-v1:0 -> nova-2-lite-v1:0; vendor IDs stay as they are."""
    return re.sub(r"^((us|eu|apac|global)\.)?(amazon|openai|anthropic|meta)\.", "", model_id)


for i in range(N):
    body = {"prompt": random.choice(QUESTIONS)}
    if MODELS:
        body["model"] = random.choice(MODELS)
    req = urllib.request.Request(URL, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            s = json.load(r)["stats"]
        print(f"{i + 1:>3}/{N}  {short(s['gen_ai.request.model'])[:28]:<28} "
              f"{s['latency_ms']:>6} ms  {s['gen_ai.usage.input_tokens']:>5} in  "
              f"{s['gen_ai.usage.output_tokens']:>4} out  tools={s['tool_calls']} errors={s['tool_errors']}", flush=True)
    except Exception as e:
        print(f"{i + 1:>3}/{N}  failed: {e}", flush=True)
    time.sleep(random.uniform(0.5, 2))

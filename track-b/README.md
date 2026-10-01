# Track B images: Severin's AI SRE agent, on any LLM

`ghcr.io/bronto-community/track-b-agent:step-N` is Severin Neumann's
`ghcr.io/bronto-community/ai-sre-agent:step-N`, unchanged, plus one switch:
set `LLM_PROVIDER=openai|anthropic|gemini` and that provider's API key, and
the agent uses that model instead of Amazon Bedrock. Without it, it is
Bedrock exactly as before.

`sitecustomize.py` swaps `strands.models.BedrockModel` for the Track A model
factory (`agent/llm.py`) at start-up, so his `agent.py` files need no edits.

Build and publish every step (from the repo root):

```bash
for s in step-1 step-2 step-3 step-4 step-7; do docker buildx build --platform linux/amd64,linux/arm64 -f track-b/Dockerfile --build-arg STEP=$s -t ghcr.io/bronto-community/track-b-agent:$s --push .; done
```

The guide: <https://ai-observatory-lab.vercel.app/track-b>

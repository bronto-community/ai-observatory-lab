# Severin's AI SRE agent for one step, unchanged, plus the Track A model switch:
# LLM_PROVIDER=openai|anthropic|gemini with that provider's API key, or
# Bedrock as before. Build from the repo root:
#   docker build -f track-b/Dockerfile --build-arg STEP=step-7 .
ARG STEP=step-1
FROM ghcr.io/bronto-community/ai-sre-agent:${STEP}
LABEL org.opencontainers.image.source=https://github.com/bronto-community/ai-observatory-lab \
      org.opencontainers.image.description="Severin Neumann's AI SRE agent, plus a switch to OpenAI, Anthropic or Gemini"
RUN python -m ensurepip >/dev/null \
 && python -m pip install --no-cache-dir -q --root-user-action=ignore "strands-agents[openai,anthropic,gemini]==1.57.1" \
 && (python -m pip uninstall -y -q --root-user-action=ignore pip setuptools >/dev/null 2>&1 || true) \
 && python -c "import openai, anthropic, google.genai"
COPY agent/llm.py track-b/sitecustomize.py /usr/local/lib/python3.12/site-packages/

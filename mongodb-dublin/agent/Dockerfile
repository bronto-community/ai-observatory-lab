# The AI SRE for the MongoDB Dublin lab. One image, six steps, picked with
# AGENT_STEP. Build from the repo root (llm.py is shared with Track A):
#   docker build -f mongodb-dublin/agent/Dockerfile -t ghcr.io/bronto-community/mongodb-lab-agent .
FROM python:3.13-slim
LABEL org.opencontainers.image.source=https://github.com/bronto-community/ai-observatory-lab \
      org.opencontainers.image.description="Build your own AI SRE: Storefront on MongoDB Atlas, investigated through Bronto"

WORKDIR /app
COPY mongodb-dublin/agent/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY agent/llm.py mongodb-dublin/agent/*.py ./
COPY mongodb-dublin/agent/prompts ./prompts

# Gemini's free tier by default; LLM_PROVIDER=bedrock|openai|anthropic also work.
# Keys arrive at run time in --env-file .env and are never baked in.
ENV PYTHONUNBUFFERED=1 \
    LLM_PROVIDER=gemini \
    AGENT_STEP=1 \
    DISABLE_ADOT_OBSERVABILITY=true \
    OTEL_EXPORTER_OTLP_PROTOCOL=http/protobuf \
    OTEL_SEMCONV_STABILITY_OPT_IN=gen_ai_latest_experimental,gen_ai_tool_definitions \
    OTEL_SERVICE_NAME=ai-sre \
    OTEL_RESOURCE_ATTRIBUTES=service.namespace=mongodb-dublin

EXPOSE 8080
CMD ["python", "agent.py"]

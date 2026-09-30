FROM python:3.13-slim

WORKDIR /app
# Build from the repo root:  docker build -f agent/Dockerfile .
COPY agent/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY agent/*.py dashboard/create_dashboard.py ./

# Telemetry goes to Bronto (EU), not CloudWatch. The API key arrives at run
# time in OTEL_EXPORTER_OTLP_HEADERS and is never baked into the image.
ENV PYTHONUNBUFFERED=1 \
    DISABLE_ADOT_OBSERVABILITY=true \
    OTEL_EXPORTER_OTLP_ENDPOINT=https://ingestion.eu.bronto.io \
    OTEL_EXPORTER_OTLP_PROTOCOL=http/protobuf \
    OTEL_SEMCONV_STABILITY_OPT_IN=gen_ai_latest_experimental,gen_ai_tool_definitions \
    OTEL_SERVICE_NAME=storefront-assistant \
    AWS_REGION=us-west-2 \
    AGENT_STEP=1

EXPOSE 8080
CMD ["python", "agent.py"]

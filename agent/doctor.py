"""Preflight: docker run --rm --env-file .env <image> python doctor.py

Checks, in the order they usually break: the model (AWS credentials and
Bedrock access, or your OpenAI / Anthropic / Gemini key) and the Bronto
ingestion key.
"""

import json
import os
import sys
import time
import urllib.error
import urllib.request

import boto3

from llm import MODEL_ID, PROVIDER, REGION, model
REGION_BRONTO = os.environ.get("BRONTO_REGION", "eu").strip().lower() or "eu"
ENDPOINT = os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT") or f"https://ingestion.{REGION_BRONTO}.bronto.io"
failed = False


def check(name, fn):
    global failed
    try:
        print(f"  ok    {name}: {fn()}")
    except Exception as e:
        failed = True
        print(f"  FAIL  {name}: {type(e).__name__}: {str(e)[:220]}")


def aws_identity():
    arn = boto3.client("sts", region_name=REGION).get_caller_identity()["Arn"]
    return arn


def bedrock():
    r = boto3.client("bedrock-runtime", region_name=REGION).converse(
        modelId=MODEL_ID, messages=[{"role": "user", "content": [{"text": "Reply with OK"}]}],
        inferenceConfig={"maxTokens": 5},
    )
    return f"{MODEL_ID} answered in {r['metrics']['latencyMs']} ms"


def vendor_model():
    from strands import Agent
    started = time.perf_counter()
    Agent(model=model(), callback_handler=None)("Reply with the single word OK")
    return f"{PROVIDER} {MODEL_ID} answered in {round((time.perf_counter() - started) * 1000)} ms"


def bronto():
    header = os.environ.get("OTEL_EXPORTER_OTLP_HEADERS", "")
    if "x-bronto-api-key=" not in header or "PASTE-KEY-HERE" in header:
        raise ValueError("set OTEL_EXPORTER_OTLP_HEADERS=x-bronto-api-key=<key> in .env")
    key = header.split("x-bronto-api-key=", 1)[1].split(",")[0]
    record = {"resourceLogs": [{"resource": {"attributes": [
        {"key": "service.name", "value": {"stringValue": os.environ.get("OTEL_SERVICE_NAME", "storefront-assistant")}},
        {"key": "service.namespace", "value": {"stringValue": "aws-ai-workshop"}},
        {"key": "attendee", "value": {"stringValue": os.environ.get("ATTENDEE", "anonymous")}},
    ]}, "scopeLogs": [{"logRecords": [{"timeUnixNano": str(time.time_ns()),
        "body": {"stringValue": "doctor: hello from the preflight check"}}]}]}]}
    req = urllib.request.Request(f"{ENDPOINT}/v1/logs", data=json.dumps(record).encode(),
        headers={"Content-Type": "application/json", "x-bronto-api-key": key})
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return f"{ENDPOINT} accepted a test event (HTTP {r.status})"
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"HTTP {e.code}: wrong key, or the wrong BRONTO_REGION? (eu or us, as in your app.eu / app.us address)") from None


print(f"Track A doctor  (provider {PROVIDER}, model {MODEL_ID}, attendee {os.environ.get('ATTENDEE', '?')})")
if PROVIDER == "bedrock":
    check("AWS credentials", aws_identity)
    check("Bedrock model access", bedrock)
else:
    check(f"{PROVIDER} API key and model", vendor_model)
check("Bronto ingestion", bronto)
if failed:
    print("\nFix the FAIL lines above. Expired AWS credentials? Refresh them (aws login, then re-export into .env) and run the doctor again.")
    sys.exit(1)
print("\nAll good. Start step 1 (same command on macOS, Linux and Windows):\n  docker run --rm -p 8080:8080 --env-file .env -e AGENT_STEP=1 ghcr.io/bronto-community/track-a-agent")

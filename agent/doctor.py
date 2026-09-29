"""Preflight: docker compose run --rm doctor

Checks, in the order they usually break: AWS credentials, region, Bedrock
model access, and the Bronto ingestion key.
"""

import json
import os
import sys
import time
import urllib.error
import urllib.request

import boto3

REGION = os.environ.get("AWS_REGION", "us-west-2")
MODEL_ID = os.environ.get("BEDROCK_MODEL_ID", "us.anthropic.claude-haiku-4-5-20251001-v1:0")
ENDPOINT = os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT", "https://ingestion.eu.bronto.io")
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
        raise RuntimeError(f"HTTP {e.code}: wrong key, or a US key against the EU endpoint?") from None


print(f"Track A doctor  (region {REGION}, attendee {os.environ.get('ATTENDEE', '?')})")
check("AWS credentials", aws_identity)
check("Bedrock model access", bedrock)
check("Bronto ingestion", bronto)
if failed:
    print("\nFix the FAIL lines above. Expired workshop credentials? Copy fresh ones from the workshop page and paste them into this terminal again.")
    sys.exit(1)
print("\nAll good. Start step 1 (same command on macOS, Linux and Windows):\n  docker run --rm -p 8080:8080 --env-file .env -e AGENT_STEP=1 ghcr.io/bronto-community/track-a-agent")

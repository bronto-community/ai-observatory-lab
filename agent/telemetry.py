"""OpenTelemetry bootstrap, following Bronto's AgentCore recipe:
https://docs.bronto.io/ai-features/aws-agentcore

One Resource shared by traces, metrics and logs. Everything is exported over
OTLP/HTTP to whatever OTEL_EXPORTER_OTLP_ENDPOINT says (Bronto, in this lab),
with the API key in OTEL_EXPORTER_OTLP_HEADERS. Call setup_telemetry() before
importing Strands.
"""

import json
import logging
import os
from collections.abc import Mapping

os.environ.setdefault("OTEL_SEMCONV_STABILITY_OPT_IN", "gen_ai_latest_experimental,gen_ai_tool_definitions")
# Botocore's GenAI events carry the prompt and reply text only when this is set.
os.environ.setdefault("OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT", "true")

from opentelemetry import metrics, trace
from opentelemetry._logs import set_logger_provider
from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.instrumentation.botocore import BotocoreInstrumentor
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler, LogRecordProcessor
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider

class GenAIEventFlattener(LogRecordProcessor):
    """Make Botocore's GenAI events readable in Bronto.

    Those events put their text in a map-valued log body and their type in the
    OTLP event_name field. Bronto keeps neither today, so they arrive as empty
    rows. Copy both into attributes before export: `event.name`, plus one
    `body.<path>` attribute per leaf (Bronto flattens arrays the same way, as
    .0, .1, ...). The body becomes the JSON text so @raw is readable too.
    """

    def on_emit(self, record) -> None:
        lr = record.log_record
        name = getattr(lr, "event_name", None)
        if name:
            lr.attributes["event.name"] = name
        if isinstance(lr.body, Mapping):
            for key, value in _flatten(lr.body, "body"):
                lr.attributes[key] = value
            lr.body = json.dumps(lr.body, default=str)

    def shutdown(self) -> None:
        pass

    def force_flush(self, timeout_millis: int = 30000) -> bool:
        return True


def _flatten(value, prefix):
    if isinstance(value, Mapping):
        for k, v in value.items():
            yield from _flatten(v, f"{prefix}.{k}")
    elif isinstance(value, (list, tuple)):
        for i, v in enumerate(value):
            yield from _flatten(v, f"{prefix}.{i}")
    elif isinstance(value, (str, bool, int, float)):
        yield prefix, value
    elif value is not None:
        yield prefix, str(value)


ATTENDEE = os.environ.get("ATTENDEE", "anonymous").strip().lower().replace(" ", "-") or "anonymous"


def setup_telemetry() -> None:
    # Everyone in the room shares one service (so one Bronto dataset and one
    # dashboard); `attendee` tells you which traces and logs are yours.
    resource = Resource.create({
        "service.name": os.environ.get("OTEL_SERVICE_NAME", "storefront-assistant"),
        "service.namespace": os.environ.get("SERVICE_NAMESPACE", "aws-ai-workshop"),
        "deployment.environment": os.environ.get("DEPLOYMENT_ENV", "workshop"),
        "attendee": ATTENDEE,
    })

# #region traces
    # Traces: Strands creates its spans from the global provider.
    tracer_provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(tracer_provider)

    from strands.telemetry import StrandsTelemetry
    StrandsTelemetry(tracer_provider=tracer_provider).setup_otlp_exporter()
# #endregion traces

    # Logs: only the agent's own logger ships to Bronto, one structured event
    # per question. Attaching to the root logger would also ship every
    # library's INFO chatter (botocore credentials, AgentCore, Strands).
    logger_provider = LoggerProvider(resource=resource)
    logger_provider.add_log_record_processor(GenAIEventFlattener())  # must run before export
    logger_provider.add_log_record_processor(BatchLogRecordProcessor(OTLPLogExporter()))
    set_logger_provider(logger_provider)
    app_log = logging.getLogger("storefront-assistant")
    app_log.addHandler(LoggingHandler(logger_provider=logger_provider))
    app_log.setLevel(logging.INFO)
    app_log.propagate = False

    # Metrics: Strands' own instruments (event-loop cycles, token counters, ...).
    metrics.set_meter_provider(MeterProvider(
        resource=resource,
        metric_readers=[PeriodicExportingMetricReader(OTLPMetricExporter(), export_interval_millis=15000)],
    ))

    # The Bedrock and AgentCore API calls themselves, as child spans, plus a
    # GenAI log event per message (system prompt, user turn, tool result,
    # model reply). Same text as Strands' span events: deliberately duplicated
    # so the conversation is searchable in Log Search too.
    BotocoreInstrumentor().instrument(logger_provider=logger_provider)

"""OpenTelemetry wiring, shared by every service."""

import logging
import os

from opentelemetry import metrics, trace
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.instrumentation.pymongo import PymongoInstrumentor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

SERVICE = os.environ.get("SERVICE_NAME", "unknown")
VERSION = os.environ.get("SERVICE_VERSION", "0.0.0")
COMMIT = os.environ.get("GIT_COMMIT", "unknown")
REPO = os.environ.get("GIT_REPO", "")


def setup(app) -> None:
    resource = Resource.create({
        "service.name": SERVICE,
        "service.version": VERSION,
        "deployment.commit": COMMIT,
    })
    provider = TracerProvider(resource=resource)
    provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))
    trace.set_tracer_provider(provider)
    metrics.set_meter_provider(MeterProvider(
        resource=resource,
        metric_readers=[PeriodicExportingMetricReader(OTLPMetricExporter(), export_interval_millis=5000)],
    ))
    HTTPXClientInstrumentor().instrument()
    PymongoInstrumentor().instrument()
    FastAPIInstrumentor.instrument_app(app)
    logging.basicConfig(level=logging.INFO, format=f"%(asctime)s {SERVICE} %(levelname)s %(message)s")
    logging.getLogger("httpx").setLevel(logging.WARNING)


def announce_release() -> None:
    """Mark the running build in telemetry, so a trace can be tied to a commit."""
    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span("deploy") as span:
        span.set_attribute("deployment.service", SERVICE)
        span.set_attribute("deployment.version", VERSION)
        span.set_attribute("deployment.commit", COMMIT)
        span.set_attribute("deployment.repo", REPO)
    logging.getLogger(SERVICE).info("release %s (%s) is live", VERSION, COMMIT)

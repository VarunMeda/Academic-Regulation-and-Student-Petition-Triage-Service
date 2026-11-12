"""Optional OpenTelemetry setup and W3C context propagation helpers."""
from contextlib import contextmanager

try:
    from opentelemetry import propagate, trace
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    AVAILABLE = True
except ImportError:
    AVAILABLE = False


def configure(app, service_name: str, endpoint: str) -> bool:
    if not AVAILABLE:
        return False
    provider = TracerProvider(resource=Resource.create({"service.name": service_name}))
    provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint=endpoint)))
    trace.set_tracer_provider(provider)
    FastAPIInstrumentor.instrument_app(app)
    return True


def inject() -> str | None:
    if not AVAILABLE:
        return None
    carrier = {}
    propagate.inject(carrier)
    return carrier.get("traceparent")


@contextmanager
def consume(traceparent: str | None, name: str):
    if not AVAILABLE or not traceparent:
        yield None
        return
    carrier = {"traceparent": traceparent}
    extracted = propagate.extract(carrier)
    tracer = trace.get_tracer("academic-petition-triage")
    with tracer.start_as_current_span(name, context=extracted, kind=trace.SpanKind.CONSUMER) as span:
        yield span


@contextmanager
def span(name: str, attributes: dict | None = None):
    if not AVAILABLE:
        yield None
        return
    tracer = trace.get_tracer("academic-petition-triage")
    with tracer.start_as_current_span(name, attributes=attributes or {}) as current:
        yield current

"""
OpenTelemetry Value Logging Example

Demonstrates automatic logging of reactive value updates. Interact with the
inputs and watch the console for log events showing when values are updated.

See README.md for setup instructions.
"""

# Set up OpenTelemetry before importing shiny
# This ensures tracing is enabled for the entire application lifecycle
from opentelemetry import trace
from opentelemetry._logs import set_logger_provider
from opentelemetry.sdk._logs import LoggerProvider
from opentelemetry.sdk._logs.export import (
    ConsoleLogRecordExporter,
    SimpleLogRecordProcessor,
)
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor

trace_provider = TracerProvider()
# For demo purposes, log to the console
trace_provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))
trace.set_tracer_provider(trace_provider)

# Set up OpenTelemetry logging
log_provider = LoggerProvider()
log_provider.add_log_record_processor(
    # For demo purposes, log to the console
    SimpleLogRecordProcessor(ConsoleLogRecordExporter())
)
set_logger_provider(log_provider)

# Now import shiny
from shiny import App, reactive, render, ui  # noqa: E402

app_ui = ui.page_fluid(
    ui.h2("OpenTelemetry Value Logging Demo"),
    ui.p(
        "This app demonstrates automatic logging of reactive value updates. "
        "Check the console output to see log events."
    ),
    ui.input_slider("slider", "Slider value", 0, 100, 50),
    ui.input_text("text", "Text input", "Hello"),
    ui.output_text_verbatim("slider_value"),
    ui.output_text_verbatim("text_value"),
    ui.output_text_verbatim("counter_value"),
    ui.input_action_button("increment", "Increment Counter"),
)


def server(input, output, session):
    # Create a reactive value
    counter = reactive.Value(0)

    @reactive.effect
    @reactive.event(input.increment)
    def _():
        # When the button is clicked, update the counter
        # This will generate a log event
        counter.set(counter() + 1)

    @render.text
    def slider_value():
        # When the slider changes, this will trigger value update logging
        return f"Slider value: {input.slider()}"

    @render.text
    def text_value():
        # When the text input changes, this will trigger value update logging
        return f"Text input: {input.text()}"

    @render.text
    def counter_value():
        # Display the counter value
        return f"Counter: {counter()}"


app = App(app_ui, server)

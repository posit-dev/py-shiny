"""
Example demonstrating OpenTelemetry collection level control and value logging.

This app shows:
1. How to use `otel_collect` to control Shiny telemetry collection
2. Automatic logging of reactive value updates
3. How `otel_collect("none")` suppresses both spans and value logs

Run with:
    python app.py

Watch the console for spans and log events as you interact with the app.
"""

# Configure OpenTelemetry BEFORE importing shiny
from opentelemetry import trace  # noqa: E402
from opentelemetry._logs import set_logger_provider  # noqa: E402
from opentelemetry.sdk._logs import LoggerProvider  # noqa: E402
from opentelemetry.sdk._logs.export import (  # noqa: E402
    ConsoleLogRecordExporter,
    SimpleLogRecordProcessor,
)
from opentelemetry.sdk.trace import TracerProvider  # noqa: E402
from opentelemetry.sdk.trace.export import (  # noqa: E402
    ConsoleSpanExporter,
    SimpleSpanProcessor,
)

# # Set up tracing
trace_provider = TracerProvider()
trace_provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))
trace.set_tracer_provider(trace_provider)

# Set up logging (for value update logs)
log_provider = LoggerProvider()
log_provider.add_log_record_processor(
    SimpleLogRecordProcessor(ConsoleLogRecordExporter())
)
set_logger_provider(log_provider)

# Now import shiny
from shiny import App, reactive, render, ui  # noqa: E402
from shiny.otel import otel_collect  # noqa: E402

app_ui = ui.page_fluid(
    ui.h2("OpenTelemetry: Collection Control & Value Logging"),
    ui.markdown("""
        This demo shows how `otel_collect` controls **both spans and value logs**.

        Watch the console to see:
        - **Spans**: Session lifecycle, reactive execution
        - **Logs**: Reactive value updates with source references
        - **Control**: How `@otel_collect("none")` suppresses both
        """),
    ui.hr(),
    ui.layout_columns(
        ui.card(
            ui.card_header("Normal Telemetry (Full Collection)"),
            ui.input_slider("normal_slider", "Slider", 0, 100, 50),
            ui.input_action_button("normal_increment", "Increment Counter"),
            ui.output_text_verbatim("normal_counter_display"),
            ui.markdown("""
                **Telemetry:** ✅ Spans + value logs
                This section generates full telemetry.
                """),
        ),
        ui.card(
            ui.card_header("Suppressed Telemetry (No Collection)"),
            ui.input_slider("private_slider", "Slider", 0, 100, 50),
            ui.input_action_button("private_increment", "Increment Counter"),
            ui.output_text_verbatim("private_counter_display"),
            ui.markdown("""
                **Telemetry:** ❌ No spans, no value logs
                Uses `@otel_collect("none")` to suppress all Shiny telemetry.
                """),
        ),
    ),
    ui.hr(),
    ui.h4("Computation Results"),
    ui.p("Click buttons to trigger computations with different telemetry levels:"),
    ui.layout_columns(
        ui.input_action_button("compute", "Compute (Normal)", class_="btn-primary"),
        ui.input_action_button(
            "compute_private", "Compute (Private)", class_="btn-warning"
        ),
    ),
    ui.layout_columns(
        ui.output_text_verbatim("result"),
        ui.output_text_verbatim("result_private"),
    ),
)


def server(input, output, session):
    # Normal section: Full telemetry (spans + value logs)
    normal_counter = reactive.value(0)

    @reactive.effect
    @reactive.event(input.normal_increment)
    def _():
        # Value update will generate a log event
        normal_counter.set(normal_counter.get() + 1)
        print(f"\n>>> Normal counter updated to: {normal_counter.get()}")

    @render.text
    def normal_counter_display():
        # Reading slider and counter generates telemetry
        slider_val = input.normal_slider()
        counter_val = normal_counter()
        return f"Slider: {slider_val}\nCounter: {counter_val}\n\n✅ Full telemetry"

    # Private section: Suppressed telemetry (no spans, no value logs)
    private_counter = reactive.value(0)
    print("Private counter: ", private_counter._name, private_counter._try_infer_name())

    @reactive.effect
    @reactive.event(input.private_increment)
    @otel_collect("none")  # Suppresses ALL telemetry for this effect
    def _():
        # No value update log will be generated
        private_counter.set(private_counter.get() + 1)
        print(f"\n>>> Private counter updated to: {private_counter.get()} (NO LOGS)")

    @render.text
    @otel_collect("none")  # Suppresses ALL telemetry for this output
    def private_counter_display():
        # No telemetry for slider reads or counter reads
        slider_val = input.private_slider()
        counter_val = private_counter()
        return f"Slider: {slider_val}\nCounter: {counter_val}\n\n❌ No telemetry"

    # Computation examples
    compute_counter = reactive.value(0)
    compute_counter_private = reactive.value(0)

    @reactive.effect
    @reactive.event(input.compute)
    def _():
        compute_counter.set(compute_counter.get() + 1)

    @reactive.effect
    @reactive.event(input.compute_private)
    @otel_collect("none")
    def _():
        compute_counter_private.set(compute_counter_private.get() + 1)

    @render.text
    def result():
        """Normal computation with full telemetry."""
        count = compute_counter.get()
        if count == 0:
            return "Click 'Compute (Normal)' to run\n\n✅ Spans + value logs"

        # Simple computation (telemetry enabled)
        total = sum(range(1, 101))
        return f"Sum 1..100 = {total:,}\nRun #{count}\n\n✅ Spans + value logs"

    @render.text
    @otel_collect("none")  # Decorator suppresses ALL telemetry
    def result_private():
        """Private computation with no telemetry."""
        count = compute_counter_private.get()
        if count == 0:
            return "Click 'Compute (Private)' to run\n\n❌ No spans, no logs"

        # Simple computation (no telemetry)
        total = sum(range(1, 101))
        return f"Sum 1..100 = {total:,}\nRun #{count}\n\n❌ No spans, no logs"


app = App(app_ui, server)


if __name__ == "__main__":
    import os

    # Set default collection level to ALL (collect everything)
    os.environ.setdefault("SHINY_OTEL_COLLECT", "all")

    # Run the app
    from shiny import run_app

    print("\n" + "=" * 80)
    print("OpenTelemetry: Collection Control & Value Logging Demo")
    print("=" * 80)
    print("\nThis demo shows:")
    print("  1. Normal telemetry: Spans + value update logs")
    print("  2. Suppressed telemetry: @otel_collect('none') disables both")
    print("\nCollection level: ALL (default)")
    print("\nInteract with the app and watch for:")
    print("  • Spans: reactive execution, session lifecycle")
    print("  • Logs: value updates with source references")
    print("  • Suppression: How @otel_collect('none') affects both")
    print("=" * 80 + "\n")

    run_app(app, launch_browser=True)

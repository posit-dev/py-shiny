"""
Test app for input_submit_textarea
"""

from shiny import App, Inputs, Outputs, Session, reactive, render, ui

app_ui = ui.page_fluid(
    ui.h3("Basic submit textarea"),
    ui.input_submit_textarea(
        "basic",
        label="Enter text",
        placeholder="Type something here...",
        value="Initial value",
        rows=3,
        width="400px",
    ),
    ui.output_code("basic_value", placeholder=True),
    ui.hr(),
    ui.h3("Submit textarea with enter key (no modifier)"),
    ui.input_submit_textarea(
        "no_modifier",
        label="Press Enter to submit",
        placeholder="Press Enter to submit",
        rows=2,
        submit_key="enter",
    ),
    ui.output_code("no_modifier_value", placeholder=True),
    ui.hr(),
    ui.h3("Submit textarea with custom button"),
    ui.input_submit_textarea(
        "custom_button",
        label="Custom button",
        placeholder="Type and click submit",
        button=ui.input_task_button("custom_submit", "Send", class_="btn-success"),
        rows=1,
    ),
    ui.output_code("custom_button_value", placeholder=True),
    ui.hr(),
    ui.h3("Update controls"),
    ui.input_action_button("update_value", "Set to 'Updated value'"),
    ui.input_action_button("update_placeholder", "Update placeholder"),
    ui.input_action_button("submit_programmatic", "Submit programmatically"),
)


def server(input: Inputs, output: Outputs, session: Session):

    @render.text
    def basic_value():
        if "basic" in input:
            return f"Submitted: {input.basic()}"
        else:
            return "No value submitted yet"

    @render.text
    def no_modifier_value():
        if "no_modifier" in input:
            return f"Submitted: {input.no_modifier()}"
        else:
            return "No value submitted yet"

    @render.text
    def custom_button_value():
        if "custom_button" in input:
            return f"Submitted: {input.custom_button()}"
        else:
            return "No value submitted yet"

    @reactive.effect
    @reactive.event(input.update_value)
    def _():
        ui.update_submit_textarea("basic", value="Updated value")

    @reactive.effect
    @reactive.event(input.update_placeholder)
    def _():
        ui.update_submit_textarea("basic", placeholder="New placeholder text")

    @reactive.effect
    @reactive.event(input.submit_programmatic)
    def _():
        ui.update_submit_textarea(
            "basic", value="Programmatically submitted", submit=True
        )


app = App(app_ui, server)

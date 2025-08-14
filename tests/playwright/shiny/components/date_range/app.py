from datetime import date

from dateutil.relativedelta import relativedelta

from shiny import App, Inputs, Outputs, Session, reactive, render, ui

min_date = date.fromisoformat("2011-11-04")
max_date = min_date + relativedelta(days=10)

app_ui = ui.page_fluid(
    ui.input_date_range(
        "standard_date_picker",
        "Normal Input:",
        start=min_date,
        end=max_date,
        min=min_date,
        max=max_date,
        format="yyyy-mm-dd",
        language="en",
    ),
    ui.output_text("standard"),
    ui.br(),
    ui.br(),
    ui.input_date_range(
        "none_date_picker",
        "None Input:",
        start=None,
        end=None,
        min=None,
        max=None,
        format="yyyy-mm-dd",
        language="en",
    ),
    ui.output_text("none"),
    ui.br(),
    ui.br(),
    ui.input_date_range(
        "empty_date_picker",
        "Empty Input:",
        start="",
        end="",
        min=None,
        max=None,
        format="yyyy-mm-dd",
        language="en",
    ),
    ui.output_text("empty"),
)


def server(input: Inputs, output: Outputs, session: Session):
    @render.text
    def standard():
        return (
            "Date Picker Value: "
            + str(input.standard_date_picker()[0])
            + " to "
            + str(input.standard_date_picker()[1])
        )

    @render.text
    def none():
        return (
            "Date Picker Value: "
            + str(input.none_date_picker()[0])
            + " to "
            + str(input.none_date_picker()[1])
        )

    @render.text
    def empty():
        return (
            "Date Picker Value: "
            + str(input.empty_date_picker()[0])
            + " to "
            + str(input.empty_date_picker()[1])
        )

    @reactive.effect
    @reactive.event(input.update, ignore_none=True, ignore_init=True)
    def _():
        d = date.fromisoformat("2011-11-05")
        ui.update_date("standard_date_picker", value=d)


app = App(app_ui, server, debug=True)

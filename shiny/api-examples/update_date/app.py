from datetime import date, timedelta

from shiny import App, Inputs, Outputs, Session, reactive, ui

app_ui = ui.page_fluid(
    ui.input_slider("n", "Day of month", min=1, max=30, value=10),
    ui.input_date("inDate", "Input date"),
)


def server(input: Inputs, output: Outputs, session: Session):
    @reactive.Effect
    def _():
        d = date(2013, 4, input.n())
        ui.update_date(
            "inDate",
            label="Date label " + str(input.n()),
            value=d,
            min=d - timedelta(days=3),
            max=d + timedelta(days=3),
        )


app = App(app_ui, server)

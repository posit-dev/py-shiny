from shiny import App, Inputs, Outputs, Session, ui

# `datesdisabled` is always given as yyyy-mm-dd, whatever the display `format` is.
dates = ["2012-03-01", "2012-03-02"]

app_ui = ui.page_fluid(
    ui.input_date(
        "long",
        "dd/mm/yyyy + datesdisabled",
        value="2012-02-29",
        format="dd/mm/yyyy",
        datesdisabled=dates,
    ),
    ui.input_date(
        "yy_plain",
        "mm/dd/yy, no datesdisabled",
        value="2012-02-29",
        format="mm/dd/yy",
    ),
    ui.input_date(
        "yy_dd",
        "mm/dd/yy + datesdisabled",
        value="2012-02-29",
        format="mm/dd/yy",
        datesdisabled=dates,
    ),
)


def server(input: Inputs, output: Outputs, session: Session):
    pass


app = App(app_ui, server)

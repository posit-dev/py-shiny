from shiny import App, Inputs, Outputs, Session, render, ui

app_ui = ui.page_fluid(
    ui.input_slider("slider", "s", 0, 10, 1),
    ui.input_slider("big", "b", 0, 5000, 1000),
    ui.input_slider("range", "r", 0, 10, (1, 2)),
    ui.input_select("select", "s", ["a", "b"], selectize=False),
    ui.input_selectize("selectize", "s", ["a", "b"]),
    ui.input_numeric("numeric", "n", 1),
    ui.input_text("text", "t"),
    ui.input_text_area("textarea", "t"),
    ui.input_password("password", "p"),
    ui.input_checkbox("checkbox", "c"),
    ui.input_switch("switch", "s"),
    ui.input_checkbox_group("group", "g", ["a", "b"]),
    ui.input_radio_buttons("radio", "r", ["a", "b"]),
    ui.input_date("date", "d", value="2024-01-01"),
    ui.input_date_range("daterange", "d", start="2024-01-01", end="2024-01-02"),
    ui.input_action_button("button", "b"),
    ui.input_action_link("link", "l"),
    ui.input_task_button("task", "t"),
    ui.output_text("text_out"),
    ui.output_code("verbatim_out"),
)


def server(input: Inputs, output: Outputs, session: Session):
    @render.text
    def text_out():
        return f"text={input.text()}"

    @render.code
    def verbatim_out():
        return f"n={input.numeric()}"


app = App(app_ui, server)

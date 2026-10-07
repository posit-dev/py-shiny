from shiny import App, Inputs, Outputs, Session, reactive, render, ui

app_ui = ui.page_fluid(
    ui.input_slider("n", "N", 1, 10, 3),
    ui.output_text("out"),
    ui.input_password("pw", "PW"),
    ui.input_text("txt", "TXT"),
    ui.input_checkbox_group("cg", "CG", ["x", "y", "z"]),
    ui.output_text("cg_out"),
    ui.input_date("d", "D", value="2024-01-01", format="mm/dd/yyyy"),
    ui.input_date_range(
        "dr", "DR", start="2024-01-01", end="2024-01-02", format="mm/dd/yyyy"
    ),
    ui.output_text("dates_out"),
    ui.output_code("code_out"),
)


def server(input: Inputs, output: Outputs, session: Session):
    @reactive.calc
    def doubled() -> int:
        return input.n() * 2

    @render.text
    def out():
        return str(doubled())

    @render.text
    def cg_out():
        return f"cg={input.cg()}"

    @render.text
    def dates_out():
        return f"d={input.d()} dr={input.dr()}"

    @render.code
    def code_out():
        return f"n={input.n()}"


app = App(app_ui, server)

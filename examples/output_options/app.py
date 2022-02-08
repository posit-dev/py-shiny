from shiny import *

ui_ = ui.page_fluid(
    ui.navs_tab(
        ui.nav("A", ui.output_ui("a")),
        ui.nav("B", ui.output_ui("b")),
    )
)


def server(input: Inputs, output: Outputs, session: Session):
    @output()
    @render_ui()
    def a():
        print("a")
        return "a"

    @output()
    @render_ui()
    def b():
        print("b")
        return "b"


App(ui_, server).run()

from shiny import App, Inputs, Outputs, Session, reactive, ui


def make_panel(letter: str) -> ui.AccordionPanel:
    return ui.accordion_panel(
        f"Section {letter}",
        f"Some narrative for section {letter}",
        value=f"sec_{letter}",
    )


items = [make_panel(letter) for letter in "ABCDE"]

app_ui = ui.page_fluid(
    ui.input_switch("update_panel", "Update (and open) Sections"),
    ui.accordion(*items, id="acc", multiple=True),
)


def server(input: Inputs, output: Outputs, session: Session):
    @reactive.effect
    @reactive.event(input.update_panel)
    def _():
        txt = " (updated)" if input.update_panel() else ""
        show = bool(input.update_panel() % 2 == 1)
        for letter in "ABCDE":
            ui.update_accordion_panel(
                "acc",
                f"sec_{letter}",
                f"Some{txt} narrative for section {letter}",
                title=f"Section {letter}{txt}",
                # Open Accordion Panel to see updated contents
                show=show,
            )
        next_show_txt = "close" if show else "open"

        ui.update_switch("update_panel", label=f"Update (and {next_show_txt}) Sections")


app = App(app_ui, server)

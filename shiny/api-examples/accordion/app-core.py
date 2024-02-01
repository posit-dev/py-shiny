from shiny import App, Inputs, Outputs, Session, render, ui


def make_items():
    return [
        ui.accordion_panel(f"Section {letter}", f"Some narrative for section {letter}")
        for letter in "ABCDE"
    ]


# # First shown by default
# ui.accordion(*make_items())

# # Nothing shown by default
# ui.accordion(*make_items(), open=False)
# # Everything shown by default
# ui.accordion(*make_items(), open=True)

# # Show particular sections
# ui.accordion(*make_items(), open="Section B")
# ui.accordion(*make_items(), open=["Section A", "Section B"])


app_ui = ui.page_fluid(
    ui.markdown("#### Accordion: (`multiple=False`)"),
    # Provide an id to create a shiny input binding
    ui.accordion(*make_items(), id="acc_single", multiple=False),
    ui.output_text_verbatim("acc_single_val", placeholder=True),
    ui.tags.br(),
    ui.markdown("#### Accordion: (`multiple=True`)"),
    ui.accordion(*make_items(), id="acc_multiple"),
    ui.output_text_verbatim("acc_multiple_val", placeholder=True),
)


def server(input: Inputs, output: Outputs, session: Session):
    @render.text
    def acc_single_val():
        return "input.acc_single(): " + str(input.acc_single())

    @render.text
    def acc_multiple_val():
        return "input.acc_multiple(): " + str(input.acc_multiple())


app = App(app_ui, server)

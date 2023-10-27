from shiny import App, Inputs, Outputs, Session, render, ui

scenarios = dict(
    out1="The following output should be empty",
    out2='The following output should have the word "One"',
    out3='The following output should have the word "Two"',
    out4='The following output should also have the word "Two"',
)

app_ui = ui.page_fluid(
    [
        ui.p(ui.div(desc), ui.output_text_verbatim(id, placeholder=True))
        for id, desc in scenarios.items()
    ]
)


def server(input: Inputs, output: Outputs, session: Session):
    # When @output(id="out2") is added to the function, it should
    # un-register the implicit @output(id="out1") that @render.text
    # does internally.

    @output(id="out2")
    @render.text
    def out1():
        return "One"

    @render.text
    def out3():
        return "Two"

    # Only implicit registration can be revoked. Since out3 was
    # explicitly registered, registering it again should result
    # in both registrations being active.
    output(out3)
    output(id="out4")(out3)


app = App(app_ui, server)

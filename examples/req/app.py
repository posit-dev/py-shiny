from shiny import *

ui = page_fluid(
    input_action_button("safe", "Throw a safe error"),
    output_ui("safe"),
    input_action_button("unsafe", "Throw an unsafe error"),
    output_ui("unsafe"),
    input_text(
        "txt",
        "Enter some text below, then remove it. Notice how the text is never fully removed.",
    ),
    output_ui("txt_out"),
)


def server(session: Session):
    @reactive()
    def safe_click():
        req(session.input["safe"])
        return session.input["safe"]

    @session.output("safe")
    @render_ui()
    def _():
        raise SafeException(f"You've clicked {str(safe_click())} times")

    @session.output("unsafe")
    @render_ui()
    def _():
        req(session.input["unsafe"])
        raise Exception(
            f"Super secret number of clicks: {str(session.input['unsafe'])}"
        )

    @observe()
    def _():
        req(session.input["unsafe"])
        print("unsafe clicks:", session.input["unsafe"])
        # raise Exception("Observer exception: this should cause a crash")

    @session.output("txt_out")
    @render_ui()
    def _():
        req(session.input["txt"], cancel_output=True)
        return session.input["txt"]


app = ShinyApp(ui, server)
app.SANITIZE_ERRORS = True
app.run()

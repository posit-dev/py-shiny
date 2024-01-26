from shiny import App, Inputs, Outputs, Session, reactive, ui

app_ui = ui.page_fluid(
    ui.input_text("msg", "Enter a message"),
    ui.input_action_button("submit", "Submit the message"),
    # It'd be better to use ui.insert_ui() in order to implement this kind of
    # functionality...this is just a basic demo of how custom message handling works.
    ui.tags.div(id="messages"),
    ui.tags.script(
        """
        $(function() {
            Shiny.addCustomMessageHandler("append_msg", function(message) {
                $("<p>").text(message.msg).appendTo("#messages");
            });
        });
        """
    ),
)


def server(input: Inputs, output: Outputs, session: Session):
    @reactive.Effect
    @reactive.event(input.submit)
    async def _():
        await session.send_custom_message("append_msg", {"msg": input.msg()})


app = App(app_ui, server, debug=True)

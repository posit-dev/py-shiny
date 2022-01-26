from shiny import *

ui = page_fluid(
    tags.p(
        """
      The first time you click the button, you should see a 1 appear below the button,
      as well as 3 messages in the python console (all reporting 1 click). After
      clicking once, clicking again should increment the number below the button and
      print the number of clicks in the console twice.
      """
    ),
    input_action_button("btn", "Click me"),
    output_ui("foo"),
)


def server(session: ShinySession):

    # i.e., observeEvent(once=True)
    @bind_event(lambda: session.input["btn"], once=True)
    @observe()
    def _():
        print("Observer once event: ", str(session.input["btn"]))

    # i.e., observeEvent(once=False)
    @bind_event(lambda: session.input["btn"])
    @observe()
    def _():
        print("Observer event: ", str(session.input["btn"]))

    # i.e., eventReactive()
    @bind_event(lambda: session.input["btn"])
    @reactive()
    def btn():
        return session.input["btn"]

    @observe()
    def _():
        print("Reactive event: ", str(btn()))

    @session.output("foo")
    @bind_event(lambda: session.input["btn"])
    @render_ui()
    def _():
        return session.input["btn"]


ShinyApp(ui, server).run()

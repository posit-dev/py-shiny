from shiny import *

ui = page_fluid(
    tags.p(
        """
      The first time you click the button, you should see a 1 appear below the button,
      as well as 2 messages in the python console (all reporting 1 click). After
      clicking once, clicking again should increment the number below the button and
      print the number of clicks in the console twice.
      """
    ),
    navs_tab_card(
        nav(
            "Sync",
            input_action_button("btn", "Click me"),
            output_ui("foo"),
        ),
        nav(
            "Async",
            input_action_button("btn_async", "Click me"),
            output_ui("foo_async"),
        ),
    ),
)


def server(session: ShinySession):

    # i.e., observeEvent(once=False)
    @observe()
    @event(lambda: session.input["btn"])
    def _():
        print("@observe() event: ", str(session.input["btn"]))

    # i.e., eventReactive()
    @reactive()
    @event(lambda: session.input["btn"])
    def btn() -> int:
        return session.input["btn"]

    @observe()
    def _():
        print("@reactive() event: ", str(btn()))

    @session.output("foo")
    @render_ui()
    @event(lambda: session.input["btn"])
    def _():
        return session.input["btn"]

    # -----------------------------------------------------------------------------
    # Async
    # -----------------------------------------------------------------------------
    @observe_async()
    @event(lambda: session.input["btn_async"])
    async def _():
        print("@observe_async() event: ", str(session.input["btn_async"]))

    @reactive_async()
    @event(lambda: session.input["btn_async"])
    async def btn_async() -> int:
        return session.input["btn_async"]

    @observe_async()
    async def _():
        val = await btn_async()
        print("@reactive_async() event: ", str(val))

    @session.output("foo_async")
    @render_ui()
    @event(lambda: session.input["btn_async"])
    async def _():
        return session.input["btn_async"]


ShinyApp(ui, server).run()

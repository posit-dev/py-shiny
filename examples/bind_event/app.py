import asyncio
from shiny import *
from htmltools import tags

app_ui = ui.page_fluid(
    tags.p(
        """
      The first time you click the button, you should see a 1 appear below the button,
      as well as 2 messages in the python console (all reporting 1 click). After
      clicking once, clicking again should increment the number below the button and
      print the number of clicks in the console twice.
      """
    ),
    ui.navs_tab_card(
        ui.nav(
            "Sync",
            ui.input_action_button("btn", "Click me"),
            ui.output_ui("btn_value"),
        ),
        ui.nav(
            "Async",
            ui.input_action_button("btn_async", "Click me"),
            ui.output_ui("btn_async_value"),
        ),
    ),
)


def server(input: Inputs, output: Outputs, session: Session):

    # i.e., observeEvent(once=False)
    @reactive.effect()
    @event(input.btn)
    def _():
        print("@effect() event: ", str(input.btn()))

    # i.e., eventReactive()
    @reactive.calc()
    @event(input.btn)
    def btn() -> int:
        return input.btn()

    @reactive.effect()
    def _():
        print("@calc() event: ", str(btn()))

    @output()
    @render_ui()
    @event(input.btn)
    def btn_value():
        return str(input.btn())

    # -----------------------------------------------------------------------------
    # Async
    # -----------------------------------------------------------------------------
    @reactive.effect()
    @event(input.btn_async)
    async def _():
        await asyncio.sleep(0)
        print("async @effect() event: ", str(input.btn_async()))

    @reactive.calc()
    @event(input.btn_async)
    async def btn_async_r() -> int:
        await asyncio.sleep(0)
        return input.btn_async()

    @reactive.effect()
    async def _():
        val = await btn_async_r()
        print("async @calc() event: ", str(val))

    @output()
    @render_ui()
    @event(btn_async_r)
    async def btn_async_value():
        val = await btn_async_r()
        print("== " + str(val))
        return str(val)


app = App(app_ui, server, debug=True)

import asyncio

from shiny import App, Inputs, Outputs, Session, reactive, render, ui

app_ui = ui.page_fluid(
    ui.tags.p(
        """
      The first time you click the button, you should see a 1 appear below the button,
      as well as 2 messages in the python console (all reporting 1 click). After
      clicking once, clicking again should increment the number below the button and
      print the number of clicks in the console twice.
      """
    ),
    ui.navset_card_tab(
        ui.nav_panel(
            "Sync",
            ui.input_action_button("btn", "Click me"),
            ui.output_ui("btn_value"),
        ),
        ui.nav_panel(
            "Async",
            ui.input_action_button("btn_async", "Click me"),
            ui.output_ui("btn_async_value"),
        ),
    ),
)


def server(input: Inputs, output: Outputs, session: Session):
    @reactive.effect
    @reactive.event(input.btn)
    def _():
        print("@effect() event: ", str(input.btn()))

    @reactive.calc
    @reactive.event(input.btn)
    def btn() -> int:
        return input.btn()

    @reactive.effect
    def _():
        print("@calc() event:   ", str(btn()))

    @render.ui
    @reactive.event(input.btn)
    def btn_value():
        return str(input.btn())

    # -----------------------------------------------------------------------------
    # Async
    # -----------------------------------------------------------------------------
    @reactive.effect
    @reactive.event(input.btn_async)
    async def _():
        await asyncio.sleep(0)
        print("async @effect() event: ", str(input.btn_async()))

    @reactive.calc
    @reactive.event(input.btn_async)
    async def btn_async_r() -> int:
        await asyncio.sleep(0)
        return input.btn_async()

    @reactive.effect
    async def _():
        val = await btn_async_r()
        print("async @calc() event:   ", str(val))

    @render.ui
    @reactive.event(btn_async_r)
    async def btn_async_value():
        val = await btn_async_r()
        print("== " + str(val))
        return str(val)


app = App(app_ui, server)

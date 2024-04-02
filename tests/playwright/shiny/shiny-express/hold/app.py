from shiny.express import input, render, ui

with ui.card(id="card"):
    ui.input_slider("s1", "A", 1, 100, 20)

    with ui.hold():

        @render.code
        def hidden():
            return input.s1()

    ui.input_slider("s2", "B", 1, 100, 40)

    # from shiny.express import ui_kwargs
    # @ui_kwargs(placeholder=False)
    # @ui_kwargs(placeholder=True)
    with ui.hold() as held:

        @render.code()
        def visible():
            # from shiny import req

            # req(False)
            return input.s2()

    "Some text here"
    held  # pyright: ignore[reportUnusedExpression]

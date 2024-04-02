from shiny.express import input, render, ui

ui.input_text_area(
    "caption_regular",
    "Caption:",
    "Data summary\nwith\nmultiple\nlines",
)


@render.text
def value_regular():
    return input.caption_regular()


ui.input_text_area(
    "caption_autoresize",
    ui.markdown("Caption (w/ `autoresize=True`):"),
    "Data summary\nwith\nmultiple\nlines",
    autoresize=True,
)


@render.text
def value_autoresize():
    return input.caption_autoresize()

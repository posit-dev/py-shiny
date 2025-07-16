from shiny import reactive, req
from shiny.express import input, render, ui
from shiny.types import SafeException

ui.input_action_button("safe", "Throw a safe error")


@render.ui
def safe():
    # This error _won't_ be sanitized when deployed (i.e., it's "safe")
    raise SafeException(f"You've clicked {str(safe_click())} times")


ui.input_action_button("unsafe", "Throw an unsafe error")


@render.ui
def unsafe():
    req(input.unsafe())
    # This error _will_ be sanitized when deployed (i.e., it's "unsafe")
    raise Exception(f"Super secret number of clicks: {str(input.unsafe())}")


ui.input_text(
    "txt",
    "Enter some text below, then remove it. Notice how the text is never fully removed.",
)


@render.ui
def txt_out():
    req(input.txt(), cancel_output=True)
    return input.txt()


@reactive.calc
def safe_click():
    req(input.safe())
    return input.safe()


@reactive.effect
def _():
    req(input.unsafe())
    print("unsafe clicks:", input.unsafe())
    # raise Exception("Observer exception: this should cause a crash")

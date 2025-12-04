from shiny import reactive, render
from shiny.express import input, ui

ui.input_submit_textarea(
    "comment",
    label="Your Comment",
    placeholder="Type your comment here...",
    rows=2,
    toolbar=[
        ui.input_action_button("clear", "Clear", class_="btn-sm btn-danger"),
        ui.input_action_button("template", "Use Template", class_="btn-sm"),
    ],
)


@reactive.effect
@reactive.event(input.clear)
def _():
    ui.update_submit_textarea(
        "comment",
        value="",
        placeholder="Type your comment here...",
    )


@reactive.effect
@reactive.event(input.template)
def _():
    ui.update_submit_textarea(
        "comment",
        value="Thank you for your feedback. We appreciate your input!",
        placeholder="",
        label="Your Comment (Template Applied)",
    )


@render.text
def submitted_comment():
    if "comment" in input:
        return f"Submitted: {input.comment()}"
    return "No comment submitted yet."

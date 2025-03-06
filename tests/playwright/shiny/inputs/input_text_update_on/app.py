from __future__ import annotations

from typing import Literal, overload

from shiny import App, Inputs, Outputs, Session, module, reactive, render, ui

random_values: dict[str, list[str | float]] = {
    "word": [
        "serendipity",
        "ephemeral",
        "mellifluous",
        "nebulous",
        "quintessential",
        "ethereal",
        "luminescent",
        "cascade",
        "zenith",
        "labyrinth",
    ],
    "sentence": [
        "The old oak tree whispered secrets to the wind.",
        "Clouds painted shadows on the mountain peaks.",
        "Stars danced across the midnight canvas.",
        "Time flows like honey on a summer day.",
        "Music filled the empty spaces between thoughts.",
    ],
    "number": [
        42,
        3.14159,
        1729,
        2.71828,
        1.41421,
        987654321,
        123.456,
        7.77777,
        9999.99,
        0.12345,
    ],
    "password": [
        "Tr0ub4dor&3",
        "P@ssw0rd123!",
        "C0mpl3x1ty#",
        "S3cur3P@ss",
        "Str0ngP@55w0rd",
        "Un1qu3C0d3!",
        "K3yM@st3r99",
        "P@ssPhr@s3",
    ],
}


@overload
def random_value(category: Literal["number"], index: int) -> float: ...


@overload
def random_value(
    category: Literal["word", "sentence", "password"], index: int
) -> str: ...


def random_value(
    category: Literal["word", "sentence", "number", "password"], index: int
) -> str | float:
    selected_list = random_values[category]
    wrapped_index = (index - 1) % len(selected_list)
    return selected_list[wrapped_index]


@module.ui
def text_input_ui(update_on: Literal["change", "blur"] = "change"):
    return ui.TagList(
        ui.h2(f'updateOn="{update_on}"'),
        ui.layout_columns(
            ui.input_text("txt", "Text", value="Hello", update_on=update_on),
            ui.div("Text", ui.output_text_verbatim("value_txt")),
            ui.input_text_area("txtarea", "Text Area", update_on=update_on),
            ui.div("Text Area", ui.output_text_verbatim("value_txtarea")),
            ui.input_numeric("num", "Numeric", value=1, update_on=update_on),
            ui.div("Numeric", ui.output_text_verbatim("value_num")),
            ui.input_password("pwd", "Password", update_on=update_on),
            ui.div("Password", ui.output_text_verbatim("value_pwd")),
            col_widths=6,
        ),
        ui.input_action_button("update_text", "Update Text"),
        ui.input_action_button("update_text_area", "Update Text Area"),
        ui.input_action_button("update_number", "Update Number"),
        ui.input_action_button("update_pwd", "Update Password"),
    )


@module.server
def text_input_server(input: Inputs, output: Outputs, session: Session):
    @render.text
    def value_txt() -> str:
        return input.txt()

    @render.text
    def value_txtarea() -> str:
        return input.txtarea()

    @render.text
    def value_num() -> str:
        return str(input.num())

    @render.text
    def value_pwd() -> str:
        return input.pwd()

    @reactive.effect
    @reactive.event(input.update_text)
    def _():
        ui.update_text(
            "txt",
            value=" ".join(
                [random_value("word", input.update_text() + i) for i in range(2)]
            ),
        )

    @reactive.effect
    @reactive.event(input.update_text_area)
    def _():
        ui.update_text_area(
            "txtarea",
            value="\n".join(
                [
                    random_value("sentence", input.update_text_area() + i)
                    for i in range(2)
                ]
            ),
        )

    @reactive.Effect
    @reactive.event(input.update_number)
    def _():
        ui.update_numeric("num", value=random_value("number", input.update_number()))

    @reactive.Effect
    @reactive.event(input.update_pwd)
    def _():
        ui.update_text("pwd", value=random_value("password", input.update_pwd()))


app_ui = ui.page_fluid(
    ui.row(
        ui.column(
            6,
            ui.div({"class": "col-sm-12"}, text_input_ui("change", update_on="change")),
        ),
        ui.column(
            6, ui.div({"class": "col-sm-12"}, text_input_ui("blur", update_on="blur"))
        ),
    )
)


def server(input: Inputs):
    text_input_server("change")
    text_input_server("blur")


app = App(app_ui, server)

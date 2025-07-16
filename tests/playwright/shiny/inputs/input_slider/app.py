from __future__ import annotations

import datetime
import typing

from shiny import App, Inputs, Outputs, Session, render, ui

slider_nums: list[int] = []


def slider_row(
    label: str,
    **kwargs: typing.Any,
) -> ui.Tag:
    id_num = len(slider_nums)
    slider_nums.append(id_num)
    return ui.row(
        ui.column(
            6,
            ui.input_slider(
                f"s{id_num}",
                label,
                **kwargs,
            ),
        ),
        ui.column(
            6,
            ui.output_text_verbatim(f"txt{id_num}", placeholder=True),
        ),
    )


app_ui = ui.page_fluid(
    ui.h2("Sliders!"),
    slider_row(
        "Integer",
        min=0,
        max=1000,
        value=500,
    ),
    slider_row(
        "Range",
        min=1,
        max=1000,
        value=(200, 500),
    ),
    slider_row(
        "Custom Format",
        min=0,
        max=10000,
        value=0,
        step=2500,
        pre="$",
        post=".00",
        sep=",",
        animate=True,
        ticks=True,
    ),
    slider_row(
        "Looping Animation",
        min=1,
        max=2000,
        value=1000,
        step=10,
        animate=ui.AnimationOptions(interval=300, loop=True),
    ),
    slider_row(
        "Single Animation",
        min=0,
        max=5,
        value=1,
        step=1,
        animate=ui.AnimationOptions(interval=100, loop=False),
    ),
    slider_row(
        "Date format",
        min=(datetime.date(2024, 1, 1)),
        max=(datetime.date(2024, 1, 10)),
        value=(datetime.date(2024, 1, 5)),
        time_format="%m/%d/%y",
        timezone="0000",
    ),
    slider_row(
        "Time format",
        min=(datetime.datetime(2024, 1, 1, 0, 0, tzinfo=datetime.timezone.utc)),
        max=(datetime.datetime(2024, 1, 10, 23, 59, tzinfo=datetime.timezone.utc)),
        value=(datetime.datetime(2024, 1, 5, 12, 00, tzinfo=datetime.timezone.utc)),
        width="600px",
        timezone="0000",
    ),
    slider_row(
        "Drag Range (Disabled)",
        min=0,
        max=1000,
        value=(200, 500),
        drag_range=False,
    ),
)


def server(input: Inputs, output: Outputs, session: Session):
    def make_output(id_num: int):
        name = f"txt{id_num}"

        @output(id=name)
        @render.text
        def _():
            return input[f"s{id_num}"]()

    for id_num in slider_nums:
        make_output(id_num)


app = App(app_ui, server)

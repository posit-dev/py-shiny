from __future__ import annotations

import datetime
from typing import Any, Optional, Union

from shiny import App, Inputs, Outputs, Session, module, reactive, render, ui

start_time = datetime.datetime(2023, 7, 1, 0, 0, 0, 0, tzinfo=datetime.timezone.utc)
end_time = start_time + datetime.timedelta(hours=1)


@module.ui
def slider_with_reset_ui(
    label: str,
    value: Union[
        datetime.datetime,
        tuple[datetime.datetime, datetime.datetime],
        list[datetime.datetime],
    ],
) -> ui.TagChild:
    return ui.card(
        ui.input_slider(
            "times",
            "Times",
            start_time,
            end_time,
            value,
            timezone="UTC",
            time_format="%H:%M:%S",
        ),
        ui.output_text_verbatim("txt"),
        ui.div(ui.input_action_button("reset", label)),
    )


@module.server
def slider_with_reset_server(
    input: Inputs,
    output: Outputs,
    session: Session,
    *,
    min: Optional[datetime.datetime] = None,
    max: Optional[datetime.datetime] = None,
    value: Any = None,
):
    @render.text
    def txt():
        if isinstance(input.times(), (tuple, list)):
            return " - ".join([str(x) for x in input.times()])
        else:
            return input.times()

    @reactive.effect
    @reactive.event(input.reset)
    def reset_time():
        ui.update_slider("times", min=min, max=max, value=value)


app_ui = ui.page_fluid(
    ui.layout_column_wrap(
        "400px",
        slider_with_reset_ui("one", "Jump to end", start_time),
        slider_with_reset_ui("two", "Select all", (start_time, start_time)),
        slider_with_reset_ui("three", "Select all", [start_time, start_time]),
        slider_with_reset_ui("four", "Extend min", [start_time, end_time]),
        slider_with_reset_ui("five", "Extend max", [start_time, end_time]),
        slider_with_reset_ui("six", "Extend min and max", [start_time, end_time]),
    ),
    class_="p-3",
)


def server(input: Inputs, output: Outputs, session: Session):
    slider_with_reset_server("one", value=end_time)
    slider_with_reset_server("two", value=(start_time, end_time))
    slider_with_reset_server("three", value=[start_time, end_time])
    slider_with_reset_server("four", min=start_time - datetime.timedelta(hours=1))
    slider_with_reset_server("five", max=end_time + datetime.timedelta(hours=1))
    slider_with_reset_server(
        "six",
        min=start_time - datetime.timedelta(hours=1),
        max=end_time + datetime.timedelta(hours=1),
    )


app = App(app_ui, server)

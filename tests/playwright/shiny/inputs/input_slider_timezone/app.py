"""Slider date/datetime values must survive a round trip to the browser.

The app deliberately runs in `Pacific/Kiritimati` (UTC+14, the furthest-forward
offset on Earth) so that the test is meaningful no matter what timezone CI runs
in. Encoding slider values against the server's local timezone -- rather than
UTC, which is how the client reads them back -- shifted them by that offset, and
at +14:00 it also moved them onto the previous calendar day. See #2398.
"""

import os
import time

# Must happen before the values below are encoded by `input_slider()`.
if hasattr(time, "tzset"):
    os.environ["TZ"] = "Pacific/Kiritimati"
    time.tzset()

import datetime  # noqa: E402

from shiny import App, Inputs, Outputs, Session, reactive, render, ui  # noqa: E402

DATE_VALUE = datetime.date(2024, 6, 1)
DATE_UPDATED = datetime.date(2024, 9, 15)

# A *naive* datetime: it carries no offset of its own, so it is the case that the
# server's timezone could shift. Midnight makes an offset move the date as well.
DATETIME_VALUE = datetime.datetime(2024, 6, 1, 0, 0, 0)
DATETIME_UPDATED = datetime.datetime(2024, 6, 15, 6, 0, 0)

app_ui = ui.page_fluid(
    ui.input_slider(
        "date_slider",
        "Date",
        min=datetime.date(2024, 1, 1),
        max=datetime.date(2024, 12, 31),
        value=DATE_VALUE,
        # A whole-day step keeps the selectable values on UTC midnights, so the
        # test can pick an exact date in the browser.
        step=datetime.timedelta(days=1),
        time_format="%F",
    ),
    ui.output_code("date_value"),
    ui.input_slider(
        "datetime_slider",
        "Datetime",
        min=datetime.datetime(2024, 6, 1, 0, 0, 0),
        max=datetime.datetime(2024, 6, 30, 0, 0, 0),
        value=DATETIME_VALUE,
        # Few enough steps that the test can drag the handle to an exact value.
        step=datetime.timedelta(hours=6),
        time_format="%F %T",
        # Pin the display to UTC so it does not depend on the browser's timezone.
        timezone="+0000",
    ),
    ui.output_code("datetime_value"),
    ui.input_action_button("update", "Update both sliders"),
)


def server(input: Inputs, output: Outputs, session: Session):
    @render.code
    def date_value():
        return str(input.date_slider())

    @render.code
    def datetime_value():
        return str(input.datetime_slider())

    @reactive.effect
    @reactive.event(input.update)
    def _():
        ui.update_slider("date_slider", value=DATE_UPDATED)
        ui.update_slider("datetime_slider", value=DATETIME_UPDATED)


app = App(app_ui, server)

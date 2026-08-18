from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.run import ShinyAppProc


def test_slider_date_and_datetime_round_trip(
    page: Page, local_app: ShinyAppProc
) -> None:
    """Slider `date` / naive `datetime` values survive the trip to the client.

    The app runs in `Pacific/Kiritimati` (UTC+14). Encoding against the server's
    local timezone instead of UTC shifted both the label the client renders and
    the value it sends back -- at +14:00, onto the previous calendar day. See
    #2398.
    """
    page.goto(local_app.url)

    date_slider = controller.InputSlider(page, "date_slider")
    datetime_slider = controller.InputSlider(page, "datetime_slider")
    date_value = controller.OutputCode(page, "date_value")
    datetime_value = controller.OutputCode(page, "datetime_value")

    # The initial values the app passed to `input_slider()`, as rendered by the
    # client and as read back by the server.
    date_slider.expect_value("2024-06-01")
    date_value.expect_value("2024-06-01")
    datetime_slider.expect_value("2024-06-01 00:00:00")
    datetime_value.expect_value("2024-06-01 00:00:00")

    # The same, after `update_slider()`.
    controller.InputActionButton(page, "update").click()
    date_slider.expect_value("2024-09-15")
    date_value.expect_value("2024-09-15")
    datetime_slider.expect_value("2024-06-15 06:00:00")
    datetime_value.expect_value("2024-06-15 06:00:00")

    # And for a value chosen in the browser: what the client shows is what the
    # server receives.
    date_slider.set("2024-03-08")
    date_slider.expect_value("2024-03-08")
    date_value.expect_value("2024-03-08")

    datetime_slider.set("2024-06-08 12:00:00")
    datetime_slider.expect_value("2024-06-08 12:00:00")
    datetime_value.expect_value("2024-06-08 12:00:00")

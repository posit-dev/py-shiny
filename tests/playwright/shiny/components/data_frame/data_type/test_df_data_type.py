import re

from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.run import ShinyAppProc


def test_data_frame_data_type(
    page: Page,
    local_app: ShinyAppProc,
) -> None:
    page.goto(local_app.url)

    controller.OutputCode(page, "pd_type").expect_value(re.compile(r"pandas"))
    controller.OutputCode(page, "pd_data").expect_value(re.compile(r"pandas"))
    controller.OutputCode(page, "pd_data_view").expect_value(re.compile(r"pandas"))
    controller.OutputCode(page, "pd_data_view_selected").expect_value(
        re.compile(r"pandas")
    )

    controller.OutputCode(page, "nw_type").expect_value(re.compile(r"narwhals"))
    controller.OutputCode(page, "nw_data").expect_value(re.compile(r"narwhals"))
    controller.OutputCode(page, "nw_data_view").expect_value(re.compile(r"narwhals"))
    controller.OutputCode(page, "nw_data_view_selected").expect_value(
        re.compile(r"narwhals")
    )

    controller.OutputCode(page, "pd_type").expect_value(re.compile(r"pandas"))
    controller.OutputCode(page, "pd_data").expect_value(re.compile(r"pandas"))
    controller.OutputCode(page, "pd_data_view").expect_value(re.compile(r"pandas"))
    controller.OutputCode(page, "pd_data_view_selected").expect_value(
        re.compile(r"pandas")
    )

    # modin tests
    controller.OutputCode(page, "mpd_type").expect_value(re.compile(r"modin"))
    controller.OutputCode(page, "mpd_data").expect_value(re.compile(r"modin"))
    controller.OutputCode(page, "mpd_data_view").expect_value(re.compile(r"modin"))
    controller.OutputCode(page, "mpd_data_view_selected").expect_value(
        re.compile(r"modin")
    )

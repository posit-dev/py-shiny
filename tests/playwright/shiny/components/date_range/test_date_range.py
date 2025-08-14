import datetime

from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.run import ShinyAppProc


def test_dynamic_navs(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    # Check the normal date range input
    date1 = controller.InputDateRange(page, "standard_date_picker")
    date1.expect_value(("2011-11-04", "2011-11-14"))
    date1.expect_max_date("2011-11-14")
    date1.expect_min_date("2011-11-04")
    date_output = controller.OutputText(page, "standard")
    date_output.expect_value("Date Picker Value: 2011-11-04 to 2011-11-14")

    # Check the None date range input
    date2 = controller.InputDateRange(page, "none_date_picker")
    input = datetime.date.today().strftime("%Y-%m-%d")
    date2.expect_value((input, input))
    date2.expect_max_date(None)
    date2.expect_min_date(None)
    date_output_none = controller.OutputText(page, "none")
    date_output_none.expect_value("Date Picker Value: " + input + " to " + input)

    # Check the empty date range input
    date3 = controller.InputDateRange(page, "empty_date_picker")
    date3.expect_value(("", ""))
    date3.expect_max_date(None)
    date3.expect_min_date(None)
    date_output_empty = controller.OutputText(page, "empty")
    date_output_empty.expect_value("Date Picker Value: None to None")

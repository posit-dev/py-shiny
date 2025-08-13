from playwright.sync_api import Page, expect

from shiny.playwright import controller
from shiny.run import ShinyAppProc
import datetime


def test_dynamic_navs(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    # Check the initial state of the date picker where value = max
    date1 = controller.InputDate(page, "start_date_picker")
    date1.expect_value("14.11.2011")

    # Can't find a way to inspect the actual display date in the datepicker,
    # as even in the broken example, the correct attribute was still set.
    # To work around this, we will check the displayed value to ensure the
    # correct value is being passed to the server.
    date_output = controller.OutputText(page, "start")
    date_output.expect_value("Date Picker Value: 2011-11-14")

    # Test the date picker with the min date = initial value (unchanged case)
    date2 = controller.InputDate(page, "min_date_picker")
    date2.expect_value("04.11.2011")

    date_output2 = controller.OutputText(page, "min")
    date_output2.expect_value("Date Picker Value: 2011-11-04")

    # Test the date picker with the date set as a string instead of as a date object
    date3 = controller.InputDate(page, "str_date_picker")
    date3.expect_value("01-10-2023")

    date_output3 = controller.OutputText(page, "str_format")
    date_output3.expect_value("Date Picker Value: 2023-10-01")

    # Test the date picker with a None value inputted
    # None defaults to today's date
    input = datetime.date.today().strftime("%Y-%m-%d")
    date4 = controller.InputDate(page, "none_date_picker")
    date4.expect_value(input)

    date_output4 = controller.OutputText(page, "none_format")
    date_output4.expect_value("Date Picker Value: " + input)

    # Test the default value when an empty string is passed is correctly blank
    date5 = controller.InputDate(page, "empty_date_picker")
    date5.expect_value("")

    date_output5 = controller.OutputText(page, "empty_format")
    date_output5.expect_value("Date Picker Value: None")

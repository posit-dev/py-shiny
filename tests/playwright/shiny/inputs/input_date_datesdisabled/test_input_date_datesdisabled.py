from playwright.sync_api import Page, expect

from shiny.playwright import controller
from shiny.run import ShinyAppProc


def disabled_days_in_next_month(page: Page, id: str) -> list[str]:
    """Open the picker, go to March 2012, and return the disabled in-month days."""
    page.locator(f"#{id}").click()
    picker = page.locator(".datepicker-dropdown:visible .datepicker-days")
    picker.locator("th.next").click()
    expect(picker.locator("th.datepicker-switch")).to_have_text("March 2012")
    days = picker.locator("td.day.disabled:not(.old):not(.new)").all_inner_texts()
    page.keyboard.press("Escape")
    return days


def test_datesdisabled_with_non_default_format(
    page: Page, local_app: ShinyAppProc
) -> None:
    page.goto(local_app.url)

    # The value must survive for every format, including 2-digit years.
    controller.InputDate(page, "long").expect_value("29/02/2012")
    controller.InputDate(page, "yy_plain").expect_value("02/29/12")
    controller.InputDate(page, "yy_dd").expect_value("02/29/12")

    controller.InputDate(page, "long").expect_datesdisabled(
        ["2012-03-01", "2012-03-02"]
    )
    controller.InputDate(page, "yy_plain").expect_datesdisabled(None)

    assert disabled_days_in_next_month(page, "long") == ["1", "2"]
    assert disabled_days_in_next_month(page, "yy_dd") == ["1", "2"]
    assert disabled_days_in_next_month(page, "yy_plain") == []

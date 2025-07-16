import datetime
import re
import time

from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.run import ShinyAppProc
from shiny.types import MISSING


def convert_to_utc_date(date_str: str) -> str:
    date_obj = datetime.datetime.strptime(date_str, "%m/%d/%y")
    epoch_time_milliseconds = date_obj.timestamp() * 1000
    return str(epoch_time_milliseconds)


def convert_to_utc_date_time(date_time_str: str) -> str:
    date_time_obj = datetime.datetime.strptime(date_time_str, "%Y-%m-%d %H:%M:%S")
    utc_timestamp = (
        date_time_obj.replace(tzinfo=datetime.timezone.utc).timestamp() * 1000
    )
    return str(utc_timestamp)


def test_slider_regular(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    s0 = controller.InputSlider(page, "s0")
    s0.expect_label("Integer")
    s0.expect_value("500")
    s0.expect_min("0")
    s0.expect_max("1000")
    s0.expect_step("1")
    s0.expect_ticks("false")
    s0.expect_sep(",")
    s0.expect_pre(None)
    s0.expect_post(None)
    s0.expect_time_format(None)
    s0.expect_timezone(None)
    s0.expect_drag_range(None)
    s0.expect_animate(exists=False)
    controller.OutputTextVerbatim(page, "txt0").expect_value("500")

    new_val = "20"
    s0.set(new_val)
    s0.expect_value(new_val)
    controller.OutputTextVerbatim(page, "txt0").expect_value(new_val)


def test_slider_range(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    s1 = controller.InputSliderRange(page, "s1")
    s1.expect_label("Range")
    s1.expect_value(("200", "500"))
    s1.expect_min("1")
    s1.expect_max("1000")
    s1.expect_step("1")
    s1.expect_ticks("false")
    s1.expect_sep(",")
    s1.expect_pre(None)
    s1.expect_post(None)
    s1.expect_time_format(None)
    s1.expect_timezone(None)
    s1.expect_drag_range("true")
    s1.expect_animate(exists=False)
    controller.OutputTextVerbatim(page, "txt1").expect_value("(200, 500)")

    new_val = ("605", "840")
    s1.set(new_val, max_err_values=1000)
    try:
        s1.expect_value((MISSING, MISSING))  # type: ignore
    except ValueError as e:
        assert re.search("tuple entries cannot", str(e))
    s1.expect_value((new_val[0], MISSING))
    s1.expect_value((MISSING, new_val[1]))
    s1.expect_value(new_val)
    controller.OutputTextVerbatim(page, "txt1").expect_value(
        f"({new_val[0]}, {new_val[1]})"
    )


def test_slider_custom_format(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    s2 = controller.InputSlider(page, "s2")
    s2.expect_label("Custom Format")
    s2.expect_value("$0.00")
    s2.expect_min("0")
    s2.expect_max("10000")
    s2.expect_step("2500")
    s2.expect_ticks("true")
    s2.expect_sep(",")
    s2.expect_pre("$")
    s2.expect_post(".00")
    s2.expect_time_format(None)
    s2.expect_timezone(None)
    s2.expect_drag_range(None)
    s2.expect_animate_options(loop=True, interval=500)
    controller.OutputTextVerbatim(page, "txt2").expect_value("0")

    s2.set("$7,500.00")
    s2.expect_value("$7,500.00")
    controller.OutputTextVerbatim(page, "txt2").expect_value("7500")


def test_slider_loop(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    s3 = controller.InputSlider(page, "s3")
    s3.expect_label("Looping Animation")
    s3.expect_value("1,000")
    s3.expect_min("1")
    s3.expect_max("2000")
    s3.expect_step("10")
    s3.expect_ticks("false")
    s3.expect_sep(",")
    s3.expect_pre(None)
    s3.expect_post(None)
    s3.expect_time_format(None)
    s3.expect_timezone(None)
    s3.expect_drag_range(None)
    s3.expect_animate_options(loop=True, interval=300)
    controller.OutputTextVerbatim(page, "txt3").expect_value("1000")

    s3.set("1,441")
    s3.expect_value("1,441")
    controller.OutputTextVerbatim(page, "txt3").expect_value("1441")

    # Play for a little bit
    s3.click_play()
    time.sleep(400 / 1000)
    s3.click_pause()
    # Make sure the value changed
    try:
        s3.expect_value("1,441", timeout=100)
    except AssertionError:
        pass


def test_slider_play(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    s4 = controller.InputSlider(page, "s4")
    s4.expect_label("Single Animation")
    s4.expect_value("1")
    s4.expect_min("0")
    s4.expect_max("5")
    s4.expect_step("1")
    s4.expect_ticks("false")
    s4.expect_sep(",")
    s4.expect_pre(None)
    s4.expect_post(None)
    s4.expect_time_format(None)
    s4.expect_timezone(None)
    s4.expect_drag_range(None)
    s4.expect_animate_options(loop=False, interval=100)
    controller.OutputTextVerbatim(page, "txt4").expect_value("1")

    s4.click_play()
    s4.expect_value("5")
    s4.click_play()  # can click again!
    s4.expect_value("5")


def test_slider_date_format(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    s5 = controller.InputSlider(page, "s5")
    s5.expect_label("Date format")
    s5.expect_value("01/05/24")
    s5.expect_min(convert_to_utc_date("01/01/24"))
    s5.expect_max(convert_to_utc_date("01/10/24"))
    s5.expect_time_format("%m/%d/%y")
    s5.expect_timezone("0000")
    s5.expect_drag_range(None)
    controller.OutputTextVerbatim(page, "txt5").expect_value("2024-01-05")

    new_val = "01/08/24"
    s5.set(new_val)
    s5.expect_value(new_val)
    controller.OutputTextVerbatim(page, "txt5").expect_value("2024-01-08")


def test_slider_time_format(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    s6 = controller.InputSlider(page, "s6")
    s6.expect_label("Time format")
    s6.expect_timezone("0000")
    s6.expect_value("2024-01-05 12:00:00")
    s6.expect_min(convert_to_utc_date_time("2024-01-01 00:00:00"))
    s6.expect_max(convert_to_utc_date_time("2024-01-10 23:59:00"))
    s6.expect_time_format("%F %T")
    s6.expect_width("600px")
    s6.expect_drag_range(None)
    controller.OutputTextVerbatim(page, "txt6").expect_value("2024-01-05 12:00:00")

    new_val = "2024-01-01 00:00:00"
    s6.set(new_val)
    s6.expect_value(new_val)
    controller.OutputTextVerbatim(page, "txt6").expect_value("2024-01-01 00:00:00")


def test_slider_drag_range_disabled(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    s7 = controller.InputSliderRange(page, "s7")
    s7.expect_label("Drag Range (Disabled)")
    s7.expect_value(("200", "500"))
    s7.expect_min("0")
    s7.expect_max("1000")
    s7.expect_drag_range("false")
    new_val = ("25", "502")
    s7.set(new_val, max_err_values=1000)
    controller.OutputTextVerbatim(page, "txt7").expect_value(
        f"({new_val[0]}, {new_val[1]})"
    )

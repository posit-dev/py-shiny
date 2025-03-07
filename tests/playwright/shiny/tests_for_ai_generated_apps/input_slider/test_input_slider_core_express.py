from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.pytest import create_app_fixture
from shiny.run import ShinyAppProc

app = create_app_fixture(["app-core.py", "app-express.py"])


def test_slider_parameters(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    # Test basic numeric slider
    slider1 = controller.InputSlider(page, "slider1")
    value1 = controller.OutputText(page, "value1")
    value1.expect_value("Value: 50")
    slider1.expect_label("Min, max, value")
    slider1.expect_min("0")
    slider1.expect_max("100")
    slider1.expect_value("50")

    # Test slider with step
    slider2 = controller.InputSlider(page, "slider2")
    value2 = controller.OutputText(page, "value2")
    value2.expect_value("Value: 50")
    slider2.expect_label("Step size = 10")
    slider2.expect_min("0")
    slider2.expect_max("100")
    slider2.expect_value("50")
    slider2.expect_step("10")

    # Test range slider
    slider3 = controller.InputSliderRange(page, "slider3")
    value3 = controller.OutputText(page, "value3")
    value3.expect_value("Value: (30, 70)")
    slider3.expect_label("Select a range")
    slider3.expect_min("0")
    slider3.expect_max("100")
    slider3.expect_value(("30", "70"))

    # Test date slider
    slider4 = controller.InputSlider(page, "slider4")
    value4 = controller.OutputText(page, "value4")
    value4.expect_value("Value: 2023-06-15 12:30:00")
    slider4.expect_label("Select a date")
    slider4.expect_min("1672531200000.0")  # 2023-01-01
    slider4.expect_max("1703980800000.0")  # 2023-12-31
    slider4.expect_value("2023-06-15")

    # Test animated slider
    slider5 = controller.InputSlider(page, "slider5")
    value5 = controller.OutputText(page, "value5")
    value5.expect_value("Value: 50")
    slider5.expect_label("With animation")
    slider5.expect_min("0")
    slider5.expect_max("100")
    slider5.expect_value("50")

    # Test formatted slider
    slider6 = controller.InputSlider(page, "slider6")
    value6 = controller.OutputText(page, "value6")
    value6.expect_value("Value: 50")
    slider6.expect_label("With prefix and suffix")
    slider6.expect_min("0")
    slider6.expect_max("100")
    slider6.expect_value("$50%")
    slider6.expect_pre("$")
    slider6.expect_post("%")
    slider6.expect_sep(",")

    # Test slider with ticks
    slider7 = controller.InputSlider(page, "slider7")
    value7 = controller.OutputText(page, "value7")
    value7.expect_value("Value: 50")
    slider7.expect_label("With tick marks")
    slider7.expect_min("0")
    slider7.expect_max("100")
    slider7.expect_value("50")
    slider7.expect_ticks("true")

    # Test date range slider
    slider9 = controller.InputSliderRange(page, "slider9")
    value9 = controller.OutputText(page, "value9")
    value9.expect_value(
        "Value: (datetime.datetime(2023, 3, 1, 0, 0), datetime.datetime(2023, 9, 30, 0, 0))"
    )
    slider9.expect_label("Draggable range")
    slider9.expect_min("1672531200000.0")  # 2023-01-01
    slider9.expect_max("1703980800000.0")  # 2023-12-31
    slider9.expect_value(("2023-03-01", "2023-09-30"))
    slider9.expect_drag_range("true")

    # Test datetime slider
    slider10 = controller.InputSlider(page, "slider10")
    value10 = controller.OutputText(page, "value10")
    value10.expect_value("Value: 2023-06-15 12:30:00")
    slider10.expect_label("With time format")
    slider10.expect_min("1672531200000.0")  # 2023-01-01 00:00
    slider10.expect_max("1704067140000.0")  # 2023-12-31 23:59
    slider10.expect_value("2023-06-15 12:30")
    slider10.expect_time_format("%Y-%m-%d %H:%M")
    slider10.expect_timezone("UTC")

from pathlib import Path

from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.reactive._reactlog._record import record_session

APP = Path(__file__).parent / "probe_app" / "app.py"

EXPECTED = {
    "slider": "shiny.sliderInput",
    "range": "shiny.sliderInput",
    "select": "shiny.selectInput",
    "selectize": "shiny.selectInput",
    "numeric": "shiny.numberInput",
    "text": "shiny.textInput",
    "textarea": "shiny.textareaInput",
    "password": "shiny.passwordInput",
    "checkbox": "shiny.checkboxInput",
    "switch": "shiny.checkboxInput",
    "group": "shiny.checkboxGroupInput",
    "radio": "shiny.radioInput",
    "date": "shiny.dateInput",
    "daterange": "shiny.dateRangeInput",
    "button": "shiny.actionButtonInput",
    "link": "shiny.actionButtonInput",
    "task": "bslib.task-button",
}


def test_recorder_captures_binding_names() -> None:
    def script(page: Page, url: str) -> None:
        page.goto(url)
        controller.InputSlider(page, "slider").set("5")
        controller.InputSliderRange(page, "range").set(("3", "4"))
        controller.InputSelect(page, "select").set("b")
        controller.InputSelectize(page, "selectize").set("b")
        controller.InputNumeric(page, "numeric").set("7")
        controller.InputText(page, "text").set("hi")
        controller.InputTextArea(page, "textarea").set("long")
        controller.InputPassword(page, "password").set("pw")
        controller.InputCheckbox(page, "checkbox").set(True)
        controller.InputSwitch(page, "switch").set(True)
        controller.InputCheckboxGroup(page, "group").set(["a"])
        controller.InputRadioButtons(page, "radio").set("b")
        controller.InputDate(page, "date").set("2024-02-02")
        controller.InputDateRange(page, "daterange").set(("2024-03-01", "2024-03-02"))
        controller.InputActionButton(page, "button").click()
        controller.InputActionLink(page, "link").click()
        controller.InputTaskButton(page, "task").click()
        controller.OutputText(page, "text_out").expect_value("text=hi")

    rec = record_session(APP, video_path=None, script=script)
    bindings = {
        a["name"]: a.get("binding")
        for a in rec.actions
        if a.get("type") == "input" and a["name"] in EXPECTED
    }
    assert bindings == EXPECTED
    texts = {
        a["name"]: a.get("value") for a in rec.actions if a.get("type") == "output"
    }
    assert texts.get("text_out") == "text=hi"
    switch = next(a for a in rec.actions if a.get("name") == "switch")
    checkbox = next(a for a in rec.actions if a.get("name") == "checkbox")
    # Switch vs checkbox: `container` is identical; `classes` tells them apart.
    assert "form-check-input" in switch["classes"]
    assert "shiny-input-checkbox" not in switch["classes"]
    assert "shiny-input-checkbox" in checkbox["classes"]
    assert "form-check-input" not in checkbox["classes"]
    link = next(a for a in rec.actions if a.get("name") == "link")
    assert link["tag"] == "A"

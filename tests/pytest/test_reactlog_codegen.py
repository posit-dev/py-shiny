from __future__ import annotations

from typing import Any

import pytest

from shiny.reactive._reactlog._codegen import generate_controller_test


def inp(name: str, value: Any, binding: str | None, **el: str) -> dict[str, Any]:
    return {
        "type": "input",
        "name": name,
        "value": value,
        "binding": binding,
        "tag": el.get("tag", "INPUT"),
        "elType": el.get("elType", ""),
        "classes": el.get("classes", ""),
        "container": el.get("container", ""),
    }


def out(
    name: str,
    value: str | None = None,
    *,
    tag: str = "DIV",
    binding: str = "shiny.textOutput",
) -> dict[str, Any]:
    return {
        "type": "output",
        "name": name,
        "binding": binding,
        "tag": tag,
        "value": value,
    }


@pytest.mark.parametrize(
    "action,expected",
    [
        (
            inp("n", 7, "shiny.sliderInput"),
            'controller.InputSlider(page, "n").set("7")',
        ),
        (
            inp("r", [3, 4], "shiny.sliderInput"),
            'controller.InputSliderRange(page, "r").set(("3", "4"))',
        ),
        (
            inp("s", "b", "shiny.selectInput", classes="selectized"),
            'controller.InputSelectize(page, "s").set("b")',
        ),
        (
            inp("s", "b", "shiny.selectInput", tag="SELECT"),
            'controller.InputSelect(page, "s").set("b")',
        ),
        (
            inp("x", 2, "shiny.numberInput"),
            'controller.InputNumeric(page, "x").set("2")',
        ),
        (
            inp("t", "hi", "shiny.textInput"),
            'controller.InputText(page, "t").set("hi")',
        ),
        (
            inp("t", "hi", "shiny.textareaInput", tag="TEXTAREA"),
            'controller.InputTextArea(page, "t").set("hi")',
        ),
        (
            inp("p", "pw", "shiny.passwordInput"),
            'controller.InputPassword(page, "p").set("pw")',
        ),
        (
            inp("c", True, "shiny.checkboxInput", classes="form-check-input"),
            'controller.InputSwitch(page, "c").set(True)',
        ),
        (
            inp("c", True, "shiny.checkboxInput", classes="shiny-input-checkbox"),
            'controller.InputCheckbox(page, "c").set(True)',
        ),
        (
            inp("g", ["a"], "shiny.checkboxGroupInput"),
            'controller.InputCheckboxGroup(page, "g").set(["a"])',
        ),
        (
            inp("r", "b", "shiny.radioInput"),
            'controller.InputRadioButtons(page, "r").set("b")',
        ),
        (
            inp("d", "2024-02-02", "shiny.dateInput"),
            'controller.InputDate(page, "d").set("2024-02-02")',
        ),
        (
            inp("dr", ["2024-03-01", "2024-03-02"], "shiny.dateRangeInput"),
            'controller.InputDateRange(page, "dr").set(("2024-03-01", "2024-03-02"))',
        ),
        (
            inp("go", 1, "shiny.actionButtonInput", tag="BUTTON"),
            'controller.InputActionButton(page, "go").click()',
        ),
        (
            inp("go", 1, "shiny.actionButtonInput", tag="A"),
            'controller.InputActionLink(page, "go").click()',
        ),
        (
            inp("task", 1, "bslib.task-button", tag="BUTTON"),
            'controller.InputTaskButton(page, "task").click()',
        ),
    ],
)
def test_codegen_maps_bindings_to_controllers(
    action: dict[str, Any], expected: str
) -> None:
    assert expected in generate_controller_test([action], test_name="app")


@pytest.mark.parametrize(
    "action,expected",
    [
        (
            inp("w", "v", "my.widget", tag="INPUT", elType="text"),
            'page.locator("#w").fill("v")',
        ),
        (
            inp("w", True, "my.widget", tag="INPUT", elType="checkbox"),
            'page.locator("#w").set_checked(True)',
        ),
        (
            inp("w", "v", "my.widget", tag="SELECT"),
            'page.locator("#w").select_option("v")',
        ),
        (inp("w", 1, "my.widget", tag="BUTTON"), 'page.locator("#w").click()'),
        (inp("w", {"a": 1}, "my.widget", tag="DIV"), "Shiny.setInputValue"),
    ],
)
def test_codegen_falls_back_to_locators(action: dict[str, Any], expected: str) -> None:
    code = generate_controller_test([action], test_name="app")
    assert expected in code
    assert "# no controller for my.widget" in code


def test_codegen_fallback_output_compiles() -> None:
    actions = [inp("w", {"a": [1, "x"]}, None, tag="DIV"), out("o", "y")]
    compile(generate_controller_test(actions, test_name="app"), "<generated>", "exec")


def test_codegen_collapses_repeated_values_but_not_clicks() -> None:
    actions = [
        inp("n", 1, "shiny.sliderInput"),
        out("o", "1"),
        inp("n", 2, "shiny.sliderInput"),
        out("o", "2"),
        inp("go", 1, "shiny.actionButtonInput", tag="BUTTON"),
        inp("go", 2, "shiny.actionButtonInput", tag="BUTTON"),
    ]
    code = generate_controller_test(actions, test_name="app")
    assert code.count("InputSlider") == 1 and '.set("2")' in code
    assert code.count(".click()") == 2
    assert 'expect_value("1")' not in code and 'expect_value("2")' in code


def test_codegen_asserts_outputs_after_their_action() -> None:
    actions = [
        out("o", "start"),
        inp("t", "a", "shiny.textInput"),
        out("o", "A"),
        out("v", "n=1", tag="PRE"),
        out("plot", None, binding="shiny.imageOutput"),
    ]
    code = generate_controller_test(actions, test_name="app")
    goto, first_expect, set_t, second_expect = (
        code.index("page.goto"),
        code.index('expect_value("start")'),
        code.index('InputText(page, "t")'),
        code.index('expect_value("A")'),
    )
    assert goto < first_expect < set_t < second_expect
    assert 'controller.OutputTextVerbatim(page, "v").expect_value("n=1")' in code
    assert "# plot updated" in code


def test_codegen_redacted_values_become_todos() -> None:
    code = generate_controller_test(
        [inp("p", "[REDACTED]", "shiny.passwordInput")], test_name="app"
    )
    assert "# TODO: value for 'p' was redacted" in code
    assert "InputPassword" not in code


def test_codegen_file_shape() -> None:
    code = generate_controller_test([], test_name="my app!", app_path="../app.py")
    assert "from shiny.playwright import controller" in code
    assert "from shiny.run import ShinyAppProc" in code
    assert '@pytest.mark.parametrize("local_app", ["../app.py"], indirect=True)' in code
    assert "def test_my_app(page: Page, local_app: ShinyAppProc) -> None:" in code
    assert "page.goto(local_app.url)" in code
    compile(code, "<generated>", "exec")


def test_codegen_output_is_black_formatted() -> None:
    black = pytest.importorskip("black")
    actions = [
        out("o", "start"),
        inp("t", "a\n\u00e9", "shiny.textInput"),
        out("o", "A"),
        inp("go", 1, "shiny.actionButtonInput", tag="BUTTON"),
    ]
    for app_path in (None, "../app.py"):
        code = generate_controller_test(actions, test_name="app", app_path=app_path)
        assert black.format_str(code, mode=black.Mode()) == code

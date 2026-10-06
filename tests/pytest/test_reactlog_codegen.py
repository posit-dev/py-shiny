from __future__ import annotations

import ast
from typing import Any

import pytest

from shiny.reactive._reactlog._codegen import REDACTED, generate_controller_test

IDLE = {"type": "idle"}


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
            {**inp("d", "2024-02-02", "shiny.dateInput"), "display": "02/02/2024"},
            'controller.InputDate(page, "d").set("02/02/2024")',
        ),
        (
            {
                **inp("dr", ["2024-03-01", "2024-03-02"], "shiny.dateRangeInput"),
                "display": ["03/01/2024", "03/02/2024"],
            },
            'controller.InputDateRange(page, "dr").set(("03/01/2024", "03/02/2024"))',
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
            'page.locator(\'[id="w"]\').fill("v")',
        ),
        (
            inp("w", True, "my.widget", tag="INPUT", elType="checkbox"),
            "page.locator('[id=\"w\"]').set_checked(True)",
        ),
        (
            inp("w", "v", "my.widget", tag="SELECT"),
            'page.locator(\'[id="w"]\').select_option("v")',
        ),
        (inp("w", 1, "my.widget", tag="BUTTON"), "page.locator('[id=\"w\"]').click()"),
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
    assert 'controller.OutputCode(page, "v").expect_value("n=1")' in code
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
        out("o", "A" * 100),
        inp("go", 1, "shiny.actionButtonInput", tag="BUTTON"),
    ]
    for app_path in (None, "../" * 30 + "app.py"):
        code = generate_controller_test(actions, test_name="app", app_path=app_path)
        assert black.format_str(code, mode=black.Mode()) == code


def test_codegen_comments_cannot_inject_code() -> None:
    actions = [
        inp("w", 1, "my.widget\nimport os", tag="DIV"),
        out("o\nimport sys", None, binding="shiny.imageOutput"),
        inp("p\nimport re", REDACTED, "shiny.passwordInput"),
    ]
    code = generate_controller_test(actions, test_name="app")
    tree = ast.parse(code)
    assert not [n for n in ast.walk(tree) if isinstance(n, ast.Import)]
    (func,) = [n for n in tree.body if isinstance(n, ast.FunctionDef)]
    assert len(func.body) == 2  # goto + the setInputValue evaluate


def test_codegen_uses_slider_display_label() -> None:
    code = generate_controller_test(
        [
            {**inp("n", 1500, "shiny.sliderInput"), "display": "1,500"},
            {
                **inp("r", [1000, 2000], "shiny.sliderInput"),
                "display": ["1,000", "2,000"],
            },
        ],
        test_name="app",
    )
    assert 'InputSlider(page, "n").set("1,500")' in code
    assert 'InputSliderRange(page, "r").set(("1,000", "2,000"))' in code


def test_codegen_does_not_collapse_fallback_button_clicks() -> None:
    actions = [
        inp("w", 1, "my.widget", tag="BUTTON"),
        inp("w", 2, "my.widget", tag="BUTTON"),
    ]
    assert generate_controller_test(actions, test_name="app").count(".click()") == 2


def test_codegen_fallback_locator_handles_special_ids() -> None:
    code = generate_controller_test(
        [inp("a.b:c", "v", "my.widget", tag="INPUT", elType="text")], test_name="app"
    )
    assert 'page.locator(\'[id="a.b:c"]\').fill("v")' in code


def test_codegen_incomplete_range_becomes_todo() -> None:
    code = generate_controller_test(
        [inp("dr", ["2024-03-01", None], "shiny.dateRangeInput")], test_name="app"
    )
    assert "# TODO: incomplete value for 'dr'" in code
    assert "None" not in code.replace("-> None", "")


def test_codegen_asserts_only_settled_values_at_idle() -> None:
    actions = [
        IDLE,
        out("o", "start"),
        inp("t", "a", "shiny.textInput"),
        out("o", "A"),
        inp("n", 5, "shiny.numberInput"),
        out("o", "A5"),
        out("p", "P"),
        IDLE,
    ]
    code = generate_controller_test(actions, test_name="app")
    assert 'expect_value("A")' not in code
    set_n = code.index('InputNumeric(page, "n")')
    assert code.index('expect_value("start")') < code.index('InputText(page, "t")')
    assert set_n < code.index('expect_value("A5")')
    assert set_n < code.index('expect_value("P")')


def test_codegen_asserts_each_idle_cycle_after_its_action() -> None:
    actions = [
        inp("t", "a", "shiny.textInput"),
        out("o", "A"),
        IDLE,
        inp("n", 5, "shiny.numberInput"),
        IDLE,
        # py-shiny sends `idle` before the flush's values.
        out("o", "B"),
    ]
    code = generate_controller_test(actions, test_name="app")
    assert (
        code.index('InputText(page, "t")')
        < code.index('expect_value("A")')
        < code.index('InputNumeric(page, "n")')
        < code.index('expect_value("B")')
    )


def test_codegen_idle_values_land_on_the_settled_step() -> None:
    # Two quick checkbox events; the first flush's values arrive after the second.
    actions = [
        inp("cg", ["x"], "shiny.checkboxGroupInput"),
        inp("cg", ["x", "z"], "shiny.checkboxGroupInput"),
        IDLE,
        out("o", "x"),
        IDLE,
        out("o", "xz"),
        inp("t", "a", "shiny.textInput"),
        IDLE,
        out("q", "Q"),
    ]
    code = generate_controller_test(actions, test_name="app")
    assert 'expect_value("x")' not in code
    assert (
        code.index('InputCheckboxGroup(page, "cg").set(["x", "z"])')
        < code.index('expect_value("xz")')
        < code.index('InputText(page, "t")')
        < code.index('expect_value("Q")')
    )


def test_codegen_without_idle_asserts_latest_value_per_step() -> None:
    actions = [
        inp("t", "a", "shiny.textInput"),
        out("o", "A"),
        out("o", "A2"),
        inp("n", 1, "shiny.numberInput"),
        out("q", "Q1"),
        inp("n", 2, "shiny.numberInput"),
        out("o", "B"),
    ]
    code = generate_controller_test(actions, test_name="app")
    assert 'expect_value("A")' not in code and 'expect_value("A2")' in code
    assert 'expect_value("Q1")' not in code  # from the superseded n=1
    assert code.index('InputNumeric(page, "n").set("2")') < code.index(
        'expect_value("B")'
    )


def test_codegen_cleared_value_becomes_todo() -> None:
    code = generate_controller_test(
        [inp("d\nx", None, "shiny.dateInput")], test_name="app"
    )
    assert "# TODO: 'd\\\\nx' was cleared" in code
    assert ".set(" not in code


def test_codegen_redacted_recording_keeps_clicks_and_hides_outputs() -> None:
    actions = [
        inp("go", REDACTED, "shiny.actionButtonInput", tag="BUTTON"),
        inp("w", REDACTED, "my.widget", tag="BUTTON"),
        out("o", "secret"),
        out("v", "secret", tag="PRE"),
    ]
    code = generate_controller_test(actions, test_name="app")
    assert 'controller.InputActionButton(page, "go").click()' in code
    assert "page.locator('[id=\"w\"]').click()" in code
    assert "secret" not in code
    assert "# o updated" in code and "# v updated" in code
    flagged = generate_controller_test(
        [inp("t", "a", "shiny.textInput"), out("o", "secret")],
        test_name="app",
        redact_outputs=True,
    )
    assert "secret" not in flagged and "# o updated" in flagged


def test_codegen_formats_with_black_when_available() -> None:
    pytest.importorskip("black")
    code = generate_controller_test([], test_name="x" * 80)
    # Unformatted, the signature is one line far past black's 88 columns.
    assert "\n    page: Page, local_app: ShinyAppProc\n" in code


def test_codegen_collapsed_step_waits_for_the_next_idle() -> None:
    actions = [
        inp("cg", ["x"], "shiny.checkboxGroupInput"),
        IDLE,
        out("o", "x"),
        out("p", "P"),
        inp("cg", ["x", "z"], "shiny.checkboxGroupInput"),
    ]
    # The recording ended before the server settled the new value.
    code = generate_controller_test(actions, test_name="app")
    assert "expect_value" not in code
    # Once it settles, values it didn't change are still asserted.
    code = generate_controller_test(actions + [IDLE, out("o", "xz")], test_name="app")
    assert 'expect_value("x")' not in code
    assert 'expect_value("xz")' in code and 'expect_value("P")' in code


def test_codegen_identical_repeat_keeps_settled_outputs() -> None:
    actions = [
        inp("t", "a", "shiny.textInput"),
        IDLE,
        out("o", "A"),
        inp("t", "a", "shiny.textInput"),
    ]
    code = generate_controller_test(actions, test_name="app")
    assert code.count("InputText") == 1 and 'expect_value("A")' in code

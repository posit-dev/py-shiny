"""Generate a Shiny Playwright controller test from recorded browser actions."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any, Callable

_REDACTED = "[REDACTED]"

Action = dict[str, Any]


def _s(value: Any) -> str:
    """A Python string literal (double-quoted) for `value`."""
    return json.dumps(str(value))


def _comment_text(value: Any) -> str:
    """Recorded text made safe for a one-line `#` comment (no raw newlines)."""
    return json.dumps(str(value))[1:-1]


class _Incomplete(ValueError):
    """The recorded value lacks a part the controller needs."""


def _call(controller: str, input_id: str, method: str, arg: str = "") -> str:
    return f"controller.{controller}(page, {_s(input_id)}).{method}({arg})"


def _pair(value: Any) -> str:
    a, b = value
    if a is None or b is None:
        raise _Incomplete
    return f"({_s(a)}, {_s(b)})"


def _strings(value: Any) -> str:
    return "[" + ", ".join(_s(v) for v in value) + "]"


@dataclass(frozen=True)
class ControllerMapping:
    """One row of the binding to controller table; the first matching row wins."""

    binding: str
    matches: Callable[[Action], bool]
    emit: Callable[[Action], str]
    click: bool = False


def _always(action: Action) -> bool:
    return True


def _is_range(action: Action) -> bool:
    return isinstance(action["value"], list)


def _is_selectize(action: Action) -> bool:
    return "selectized" in action.get("classes", "")


def _is_switch(action: Action) -> bool:
    classes = action.get("classes", "")
    return "form-check-input" in classes and "shiny-input-checkbox" not in classes


def _is_link(action: Action) -> bool:
    return action.get("tag") == "A"


def _set(controller: str, arg: Callable[[Any], str] = _s) -> Callable[[Action], str]:
    return lambda a: _call(controller, a["name"], "set", arg(a["value"]))


def _click(controller: str) -> Callable[[Action], str]:
    return lambda a: _call(controller, a["name"], "click")


def _select_arg(value: Any) -> str:
    return _strings(value) if isinstance(value, list) else _s(value)


def _slider(controller: str) -> Callable[[Action], str]:
    # Sliders are dragged until the label text matches, so prefer the recorded
    # formatted label (`display`, e.g. "1,500") over the raw value.
    def emit(a: Action) -> str:
        shown = a.get("display")
        value = a["value"] if shown is None else shown
        arg = _pair if controller == "InputSliderRange" else _s
        return _call(controller, a["name"], "set", arg(value))

    return emit


MAPPINGS: list[ControllerMapping] = [
    ControllerMapping("shiny.sliderInput", _is_range, _slider("InputSliderRange")),
    ControllerMapping("shiny.sliderInput", _always, _slider("InputSlider")),
    ControllerMapping(
        "shiny.selectInput", _is_selectize, _set("InputSelectize", _select_arg)
    ),
    ControllerMapping("shiny.selectInput", _always, _set("InputSelect", _select_arg)),
    ControllerMapping("shiny.numberInput", _always, _set("InputNumeric")),
    ControllerMapping("shiny.textInput", _always, _set("InputText")),
    ControllerMapping("shiny.textareaInput", _always, _set("InputTextArea")),
    ControllerMapping("shiny.passwordInput", _always, _set("InputPassword")),
    ControllerMapping(
        "shiny.checkboxInput",
        _is_switch,
        _set("InputSwitch", lambda v: repr(bool(v))),
    ),
    ControllerMapping(
        "shiny.checkboxInput", _always, _set("InputCheckbox", lambda v: repr(bool(v)))
    ),
    ControllerMapping(
        "shiny.checkboxGroupInput",
        _always,
        _set("InputCheckboxGroup", lambda v: _strings(v or [])),
    ),
    ControllerMapping("shiny.radioInput", _always, _set("InputRadioButtons")),
    ControllerMapping("shiny.dateInput", _always, _set("InputDate")),
    ControllerMapping("shiny.dateRangeInput", _always, _set("InputDateRange", _pair)),
    ControllerMapping(
        "shiny.actionButtonInput", _is_link, _click("InputActionLink"), click=True
    ),
    ControllerMapping(
        "shiny.actionButtonInput", _always, _click("InputActionButton"), click=True
    ),
    ControllerMapping(
        "bslib.task-button", _always, _click("InputTaskButton"), click=True
    ),
]

_TEXT_LIKE = {"", "text", "number", "email", "search", "tel", "url", "password", "date"}


def _fallback(action: Action) -> str:
    i, v, tag = action["name"], action["value"], action.get("tag", "")
    selector = "[id=" + json.dumps(str(i)) + "]"  # CSS-quoted, so `.`/`:` are fine
    literal = "'" + selector.replace("\\", "\\\\").replace("'", "\\'") + "'"
    loc = f"page.locator({literal})"
    note = f"  # no controller for {_comment_text(action.get('binding') or 'unknown binding')}"
    if tag == "TEXTAREA" or (tag == "INPUT" and action.get("elType", "") in _TEXT_LIKE):
        return f"{loc}.fill({_s(v)}){note}"
    if tag == "INPUT" and action.get("elType") in ("checkbox", "radio"):
        return f"{loc}.set_checked({bool(v)!r}){note}"
    if tag == "SELECT":
        return f"{loc}.select_option({_s(v)}){note}"
    if tag in ("BUTTON", "A"):
        return f"{loc}.click(){note}"
    # Bypasses the widget's UI, but reproduces the same reactive input.
    return (
        f'page.evaluate("([id, v]) => Shiny.setInputValue(id, v)", [{_s(i)}, {v!r}])'
        f"{note}"
    )


def _find_mapping(action: Action) -> ControllerMapping | None:
    for mapping in MAPPINGS:
        if mapping.binding == action.get("binding") and mapping.matches(action):
            return mapping
    return None


def _is_click(action: Action) -> bool:
    if action["value"] == _REDACTED:
        return False
    mapping = _find_mapping(action)
    if mapping is not None:
        return mapping.click
    return action.get("tag") in ("BUTTON", "A")


def _statement(action: Action) -> str:
    name = _comment_text(repr(action["name"]))
    if action["value"] == _REDACTED:
        return f"# TODO: value for {name} was redacted"
    mapping = _find_mapping(action)
    if mapping is None:
        return _fallback(action)
    try:
        return mapping.emit(action)
    except _Incomplete:
        return f"# TODO: incomplete value for {name}"


def _assertion(name: str, output: Action) -> str:
    if output.get("binding") == "shiny.textOutput" and isinstance(
        output.get("value"), str
    ):
        controller = (
            "OutputTextVerbatim" if output.get("tag") == "PRE" else "OutputText"
        )
        return _call(controller, name, "expect_value", _s(output["value"]))
    return f"# {_comment_text(name)} updated"


def _identifier(name: str) -> str:
    ident = re.sub(r"\W+", "_", name.strip().lower()).strip("_")
    return ident or "app"


def generate_controller_test(
    actions: list[Action], *, test_name: str, app_path: str | None = None
) -> str:
    """A pytest file replaying `actions` with Shiny Playwright controllers."""
    steps: list[tuple[Action | None, dict[str, Action]]] = [(None, {})]
    for action in actions:
        if action.get("type") == "output":
            steps[-1][1][action["name"]] = action
        elif action.get("type") == "input":
            last = steps[-1][0]
            repeat = (
                last is not None
                and last["name"] == action["name"]
                and not _is_click(action)
            )
            if repeat:
                steps[-1] = (action, steps[-1][1])
            else:
                steps.append((action, {}))

    body = ["page.goto(local_app.url)"]
    for action, outputs in steps:
        if action is not None:
            body.append(_statement(action))
        body.extend(_assertion(name, out) for name, out in outputs.items())

    header = [
        "import pytest" if app_path is not None else None,
        "from playwright.sync_api import Page",
        "",
        "from shiny.playwright import controller",
        "from shiny.run import ShinyAppProc",
        "",
        "",
    ]
    marker: list[str] = (
        [f'@pytest.mark.parametrize("local_app", [{_s(app_path)}], indirect=True)']
        if app_path is not None
        else []
    )
    signature = f"def test_{_identifier(test_name)}(page: Page, local_app: ShinyAppProc) -> None:"
    lines = [x for x in header if x is not None] + marker + [signature]
    lines += ["    " + line for line in body]
    return "\n".join(lines) + "\n"

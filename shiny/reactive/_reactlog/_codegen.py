"""Generate a Shiny Playwright controller test from recorded browser actions."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any, Callable

_REDACTED = "[REDACTED]"
_CLICK_BINDINGS = ("shiny.actionButtonInput", "bslib.task-button")

Action = dict[str, Any]


def _s(value: Any) -> str:
    """A Python string literal (double-quoted) for `value`."""
    return json.dumps(str(value))


def _call(controller: str, input_id: str, method: str, arg: str = "") -> str:
    return f"controller.{controller}(page, {_s(input_id)}).{method}({arg})"


def _pair(value: Any) -> str:
    a, b = value
    return f"({_s(a)}, {_s(b)})"


def _strings(value: Any) -> str:
    return "[" + ", ".join(_s(v) for v in value) + "]"


@dataclass(frozen=True)
class ControllerMapping:
    """One row of the binding → controller table; the first matching row wins."""

    binding: str
    matches: Callable[[Action], bool]
    emit: Callable[[str, Any], str]


def _always(action: Action) -> bool:
    return True


MAPPINGS: list[ControllerMapping] = [
    ControllerMapping(
        "shiny.sliderInput",
        lambda a: isinstance(a["value"], list),
        lambda i, v: _call("InputSliderRange", i, "set", _pair(v)),
    ),
    ControllerMapping(
        "shiny.sliderInput", _always, lambda i, v: _call("InputSlider", i, "set", _s(v))
    ),
    ControllerMapping(
        "shiny.selectInput",
        lambda a: "selectized" in a.get("classes", ""),
        lambda i, v: _call(
            "InputSelectize", i, "set", _strings(v) if isinstance(v, list) else _s(v)
        ),
    ),
    ControllerMapping(
        "shiny.selectInput",
        _always,
        lambda i, v: _call(
            "InputSelect", i, "set", _strings(v) if isinstance(v, list) else _s(v)
        ),
    ),
    ControllerMapping(
        "shiny.numberInput",
        _always,
        lambda i, v: _call("InputNumeric", i, "set", _s(v)),
    ),
    ControllerMapping(
        "shiny.textInput", _always, lambda i, v: _call("InputText", i, "set", _s(v))
    ),
    ControllerMapping(
        "shiny.textareaInput",
        _always,
        lambda i, v: _call("InputTextArea", i, "set", _s(v)),
    ),
    ControllerMapping(
        "shiny.passwordInput",
        _always,
        lambda i, v: _call("InputPassword", i, "set", _s(v)),
    ),
    ControllerMapping(
        "shiny.checkboxInput",
        lambda a: "form-check-input" in a.get("classes", "")
        and "shiny-input-checkbox" not in a.get("classes", ""),
        lambda i, v: _call("InputSwitch", i, "set", repr(bool(v))),
    ),
    ControllerMapping(
        "shiny.checkboxInput",
        _always,
        lambda i, v: _call("InputCheckbox", i, "set", repr(bool(v))),
    ),
    ControllerMapping(
        "shiny.checkboxGroupInput",
        _always,
        lambda i, v: _call("InputCheckboxGroup", i, "set", _strings(v or [])),
    ),
    ControllerMapping(
        "shiny.radioInput",
        _always,
        lambda i, v: _call("InputRadioButtons", i, "set", _s(v)),
    ),
    ControllerMapping(
        "shiny.dateInput", _always, lambda i, v: _call("InputDate", i, "set", _s(v))
    ),
    ControllerMapping(
        "shiny.dateRangeInput",
        _always,
        lambda i, v: _call("InputDateRange", i, "set", _pair(v)),
    ),
    ControllerMapping(
        "shiny.actionButtonInput",
        lambda a: a.get("tag") == "A",
        lambda i, v: _call("InputActionLink", i, "click"),
    ),
    ControllerMapping(
        "shiny.actionButtonInput",
        _always,
        lambda i, v: _call("InputActionButton", i, "click"),
    ),
    ControllerMapping(
        "bslib.task-button", _always, lambda i, v: _call("InputTaskButton", i, "click")
    ),
]

_TEXT_LIKE = {"", "text", "number", "email", "search", "tel", "url", "password", "date"}


def _fallback(action: Action) -> str:
    i, v, tag = action["name"], action["value"], action.get("tag", "")
    loc = f"page.locator({_s('#' + i)})"
    note = f"  # no controller for {action.get('binding') or 'unknown binding'}"
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


def _statement(action: Action) -> str:
    if action["value"] == _REDACTED:
        return f"# TODO: value for {action['name']!r} was redacted"
    for mapping in MAPPINGS:
        if mapping.binding == action.get("binding") and mapping.matches(action):
            return mapping.emit(action["name"], action["value"])
    return _fallback(action)


def _assertion(name: str, output: Action) -> str:
    if output.get("binding") == "shiny.textOutput" and isinstance(
        output.get("value"), str
    ):
        controller = (
            "OutputTextVerbatim" if output.get("tag") == "PRE" else "OutputText"
        )
        return _call(controller, name, "expect_value", _s(output["value"]))
    return f"# {name} updated"


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
                and action.get("binding") not in _CLICK_BINDINGS
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

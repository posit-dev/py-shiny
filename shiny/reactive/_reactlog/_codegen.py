"""Generate a Shiny Playwright controller test from recorded browser actions."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any, Callable

REDACTED = "[REDACTED]"
"""Stands in for a recorded input value that must not be written out."""

Action = dict[str, Any]


def _s(value: Any) -> str:
    """A Python string literal (double-quoted) for `value`."""
    return json.dumps(str(value))


def _comment_text(value: Any) -> str:
    """Recorded text made safe for a one-line `#` comment (no raw newlines)."""
    return json.dumps(str(value))[1:-1]


class _Incomplete(ValueError):
    """The recorded value lacks a part the controller needs."""


def _call(controller: str, input_id: str, *, method: str, arg: str = "") -> str:
    return f"controller.{controller}(page, {_s(input_id)}).{method}({arg})"


def _pair(value: Any) -> str:
    a, b = value
    if a in (None, "") or b in (None, ""):
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
    # Sliders are dragged, and date fields typed, until the visible text matches, so
    # prefer the recorded `display` text (e.g. "1,500", "02/03/2024") to the value.
    def emit(a: Action) -> str:
        shown = a.get("display")
        value = a["value"] if shown is None else shown
        return _call(controller, a["name"], method="set", arg=arg(value))

    return emit


def _click(controller: str) -> Callable[[Action], str]:
    return lambda a: _call(controller, a["name"], method="click")


def _select_arg(value: Any) -> str:
    return _strings(value) if isinstance(value, list) else _s(value)


def _bool_arg(value: Any) -> str:
    return repr(bool(value))


MAPPINGS: list[ControllerMapping] = [
    ControllerMapping(
        "shiny.sliderInput", matches=_is_range, emit=_set("InputSliderRange", arg=_pair)
    ),
    ControllerMapping("shiny.sliderInput", matches=_always, emit=_set("InputSlider")),
    ControllerMapping(
        "shiny.selectInput",
        matches=_is_selectize,
        emit=_set("InputSelectize", arg=_select_arg),
    ),
    ControllerMapping(
        "shiny.selectInput", matches=_always, emit=_set("InputSelect", arg=_select_arg)
    ),
    ControllerMapping("shiny.numberInput", matches=_always, emit=_set("InputNumeric")),
    ControllerMapping("shiny.textInput", matches=_always, emit=_set("InputText")),
    ControllerMapping(
        "shiny.textareaInput", matches=_always, emit=_set("InputTextArea")
    ),
    ControllerMapping(
        "shiny.passwordInput", matches=_always, emit=_set("InputPassword")
    ),
    ControllerMapping(
        "shiny.checkboxInput",
        matches=_is_switch,
        emit=_set("InputSwitch", arg=_bool_arg),
    ),
    ControllerMapping(
        "shiny.checkboxInput",
        matches=_always,
        emit=_set("InputCheckbox", arg=_bool_arg),
    ),
    ControllerMapping(
        "shiny.checkboxGroupInput",
        matches=_always,
        emit=_set("InputCheckboxGroup", arg=lambda v: _strings(v or [])),
    ),
    ControllerMapping(
        "shiny.radioInput", matches=_always, emit=_set("InputRadioButtons")
    ),
    ControllerMapping("shiny.dateInput", matches=_always, emit=_set("InputDate")),
    ControllerMapping(
        "shiny.dateRangeInput", matches=_always, emit=_set("InputDateRange", arg=_pair)
    ),
    ControllerMapping(
        "shiny.actionButtonInput",
        matches=_is_link,
        emit=_click("InputActionLink"),
        click=True,
    ),
    ControllerMapping(
        "shiny.actionButtonInput",
        matches=_always,
        emit=_click("InputActionButton"),
        click=True,
    ),
    ControllerMapping(
        "bslib.task-button",
        matches=_always,
        emit=_click("InputTaskButton"),
        click=True,
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
    # Clicks carry no meaningful value, so a redacted one still replays.
    mapping = _find_mapping(action)
    if mapping is not None:
        return mapping.click
    return action.get("tag") in ("BUTTON", "A")


def _statement(action: Action) -> str:
    name = _comment_text(repr(action["name"]))
    if not _is_click(action):
        if action["value"] == REDACTED:
            return f"# TODO: value for {name} was redacted"
        if action["value"] is None:
            return f"# TODO: {name} was cleared"
    mapping = _find_mapping(action)
    if mapping is None:
        return _fallback(action)
    try:
        return mapping.emit(action)
    except _Incomplete:
        return f"# TODO: incomplete value for {name}"


def _assertion(name: str, output: Action, *, redact: bool) -> str:
    if (
        not redact
        and output.get("binding") == "shiny.textOutput"
        and isinstance(output.get("value"), str)
    ):
        controller = "OutputCode" if output.get("tag") == "PRE" else "OutputText"
        return _call(controller, name, method="expect_value", arg=_s(output["value"]))
    return f"# {_comment_text(name)} updated"


def _identifier(name: str) -> str:
    ident = re.sub(r"\W+", "_", name.strip().lower()).strip("_")
    return ident or "app"


Step = tuple[Action | None, dict[str, Action]]


def _steps(actions: list[Action]) -> list[Step]:
    """
    Group `actions` into (input action, outputs to assert after it) steps.

    Repeated values of one input collapse into a single step. With `idle` markers
    (sent when the server finishes a flush) only the values outputs had when the
    app went idle are asserted, so a fast next input can't leave an assertion for a
    transient value; a collapsed step's outputs wait for the next idle again, where
    newer values replace them. Without idle markers (older recordings) each step
    asserts the latest value of the outputs that updated before the next input, and
    a collapsed step drops the outputs of the superseded values.
    """
    steps: list[Step] = [(None, {})]
    by_idle = any(a.get("type") == "idle" for a in actions)
    pending: dict[str, Action] = {}  # output values not yet seen settled
    settled = False  # py-shiny sends `idle` just before the flush's values
    for action in actions:
        kind = action.get("type")
        if kind == "output":
            target = pending if by_idle and not settled else steps[-1][1]
            target[action["name"]] = action
        elif kind == "idle":
            steps[-1][1].update(pending)
            pending.clear()
            settled = True
        elif kind == "input":
            settled = False
            last, outputs = steps[-1]
            if last is None or last["name"] != action["name"] or _is_click(action):
                steps.append((action, {}))
            elif (last["value"], last.get("display")) != (
                action["value"],
                action.get("display"),
            ):
                if by_idle:
                    pending = {**outputs, **pending}
                steps[-1] = (action, dict[str, Action]())
    return steps


def _format(code: str) -> str:
    """`code` formatted with black when it is installed (best effort)."""
    try:
        import black
    except ImportError:
        return code
    try:
        return black.format_str(code, mode=black.Mode())
    except ValueError:  # black's InvalidInput; generated code should always parse
        return code


def generate_controller_test(
    actions: list[Action],
    *,
    test_name: str,
    app_path: str | None = None,
    redact_outputs: bool = False,
) -> str:
    """
    A pytest file replaying `actions` with Shiny Playwright controllers.

    Text output assertions become `# <id> updated` comments with `redact_outputs`,
    or when any recorded value was redacted, so redacted text can't leak.
    """
    redact = redact_outputs or any(a.get("value") == REDACTED for a in actions)
    body = ["page.goto(local_app.url)"]
    for action, outputs in _steps(actions):
        if action is not None:
            body.append(_statement(action))
        body.extend(
            _assertion(name, out, redact=redact) for name, out in outputs.items()
        )

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
    return _format("\n".join(lines) + "\n")

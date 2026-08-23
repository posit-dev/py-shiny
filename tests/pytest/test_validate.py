from __future__ import annotations

from typing import Any, cast

import pytest

from shiny import render
from shiny._namespaces import ResolvedId
from shiny._validate import validate_shiny_code
from shiny.session._session import Inputs, Outputs, Session


def test_validate_direct_input_assignment() -> None:
    code = "from shiny.express import input, ui\ninput.x = 10"
    report = validate_shiny_code(code)
    assert not report["valid"]
    assert any(err["code"] == "INPUT_ASSIGNMENT" for err in report["errors"])
    assert any("read-only" in err["message"] for err in report["errors"])


def test_validate_uncalled_input() -> None:
    code = "from shiny import render, input\n@render.text\ndef txt():\n    return input.val"
    report = validate_shiny_code(code)
    assert any(warn["code"] == "UNCALLED_INPUT" for warn in report["warnings"])
    assert any("parentheses" in warn["message"] for warn in report["warnings"])


def test_validate_duplicate_input_ids() -> None:
    code = 'from shiny import ui\nui.input_text("name", "Label 1")\nui.input_text("name", "Label 2")'
    report = validate_shiny_code(code)
    assert any(warn["code"] == "DUPLICATE_ID" for warn in report["warnings"])


def test_validate_duplicate_output_ids() -> None:
    code = 'from shiny import ui\nui.output_text("txt")\nui.output_text("txt")'
    report = validate_shiny_code(code)
    assert any(warn["code"] == "DUPLICATE_ID" for warn in report["warnings"])


def test_validate_multiple_renderers() -> None:
    code = "from shiny import render\n@render.text\n@render.ui\ndef out():\n    return 'hello'"
    report = validate_shiny_code(code)
    assert not report["valid"]
    assert any(err["code"] == "MULTIPLE_RENDERERS" for err in report["errors"])


def test_validate_r_idioms() -> None:
    code = "from shiny import shinyApp, fluidPage"
    report = validate_shiny_code(code)
    assert not report["valid"]
    assert any(err["code"] == "R_SHINY_IDIOM" for err in report["errors"])


def test_runtime_inputs_assignment_error() -> None:
    inputs = Inputs({})
    with pytest.raises(TypeError, match="Cannot assign directly to 'input.count'"):
        inputs.count = 5  # type: ignore


class _StubSession:
    def __init__(self) -> None:
        self.ns = ResolvedId("")

    def _is_hidden(self, name: str) -> bool:
        return False

    def is_stub_session(self) -> bool:
        return False


def test_runtime_outputs_duplicate_warning() -> None:
    session = cast(Session, _StubSession())
    outputs_map: dict[str, Any] = {}
    outputs = Outputs(session, ns=ResolvedId(""), outputs=outputs_map)

    @outputs
    @render.text
    def result() -> str:
        return "first"

    with pytest.warns(RuntimeWarning, match="Duplicate output 'result'"):

        @outputs
        @render.text
        def result() -> str:  # noqa: F811
            return "second"


def test_core_shiny_output_id_order_independent() -> None:
    server_first_code = """from shiny import App, render, ui

def server(input, output, session):
    @render.text
    def summary():
        return "Summary"

app_ui = ui.page_fluid(
    ui.output_text("summary")
)

app = App(app_ui, server)
"""
    res1 = validate_shiny_code(server_first_code)
    assert res1["valid"] is True
    assert len([w for w in res1["warnings"] if w["code"] == "DUPLICATE_ID"]) == 0

    ui_first_code = """from shiny import App, render, ui

app_ui = ui.page_fluid(
    ui.output_text("summary")
)

def server(input, output, session):
    @render.text
    def summary():
        return "Summary"

app = App(app_ui, server)
"""
    res2 = validate_shiny_code(ui_first_code)
    assert res2["valid"] is True
    assert len([w for w in res2["warnings"] if w["code"] == "DUPLICATE_ID"]) == 0


def test_duplicate_output_id_detected() -> None:
    dup_code = """from shiny import App, ui

app_ui = ui.page_fluid(
    ui.output_text("summary"),
    ui.output_text("summary")
)
"""
    res = validate_shiny_code(dup_code)
    dup_warnings = [w for w in res["warnings"] if w["code"] == "DUPLICATE_ID"]
    assert len(dup_warnings) == 1

from __future__ import annotations

from pathlib import Path
from typing import Any, cast

import pytest

from shiny import render
from shiny._namespaces import ResolvedId
from shiny._validate import validate_shiny_code
from shiny.session._session import Inputs, Outputs, Session


def test_validate_direct_input_assignment() -> None:
    code = "from shiny.express import input, ui\ninput.x = 10"
    report = validate_shiny_code(code)
    assert not report.valid
    assert any(err["code"] == "INPUT_ASSIGNMENT" for err in report.errors)
    assert any("read-only" in err["message"] for err in report.errors)


def test_validate_uncalled_input() -> None:
    code = "from shiny import render, input\n@render.text\ndef txt():\n    return input.val"
    report = validate_shiny_code(code)
    assert report.valid is False
    assert any(warn["code"] == "UNCALLED_INPUT" for warn in report.warnings)
    assert any("parentheses" in warn["message"] for warn in report.warnings)
    assert (
        "Code structure matches Python Shiny best practices." not in report.suggestions
    )


def test_validate_duplicate_input_ids() -> None:
    code = 'from shiny import ui\nui.input_text("name", "Label 1")\nui.input_text("name", "Label 2")'
    report = validate_shiny_code(code)
    assert report.valid is False
    assert any(warn["code"] == "DUPLICATE_ID" for warn in report.warnings)


def test_validate_duplicate_output_ids() -> None:
    code = 'from shiny import ui\nui.output_text("txt")\nui.output_text("txt")'
    report = validate_shiny_code(code)
    assert report.valid is False
    assert any(warn["code"] == "DUPLICATE_ID" for warn in report.warnings)


def test_validate_assignment_does_not_report_uncalled_input() -> None:
    code = """from shiny import reactive
@reactive.effect
def reset():
    input.count = 0
"""
    report = validate_shiny_code(code)
    assert [err["code"] for err in report.errors] == ["INPUT_ASSIGNMENT"]
    assert not report.warnings


def test_validate_multiple_renderers() -> None:
    code = "from shiny import render\n@render.text\n@render.ui\ndef out():\n    return 'hello'"
    report = validate_shiny_code(code)
    assert not report.valid
    assert any(err["code"] == "MULTIPLE_RENDERERS" for err in report.errors)


def test_validate_r_idioms() -> None:
    code = "from shiny import shinyApp, fluidPage"
    report = validate_shiny_code(code)
    assert not report.valid
    assert any(err["code"] == "R_SHINY_IDIOM" for err in report.errors)


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
    assert res1.valid is True
    assert len([w for w in res1.warnings if w["code"] == "DUPLICATE_ID"]) == 0

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
    assert res2.valid is True
    assert len([w for w in res2.warnings if w["code"] == "DUPLICATE_ID"]) == 0


def test_duplicate_output_id_detected() -> None:
    dup_code = """from shiny import App, ui

app_ui = ui.page_fluid(
    ui.output_text("summary"),
    ui.output_text("summary")
)
"""
    res = validate_shiny_code(dup_code)
    dup_warnings = [w for w in res.warnings if w["code"] == "DUPLICATE_ID"]
    assert len(dup_warnings) == 1


def test_typed_result_and_subclass_validation() -> None:
    import ast

    import shiny.validate as validation

    assert hasattr(validation, "ValidateResult")

    class ProjectValidator(validation.ShinyCodeValidator):
        def visit_Call(self, node: ast.Call) -> None:
            if isinstance(node.func, ast.Name) and node.func.id == "print":
                self.result.add_error(
                    node.lineno, "Use project logging", "PROJECT_LOGGING"
                )
            super().visit_Call(node)

    result = validation.validate_shiny_code(
        "from shiny import ui\nprint('hello')", validator_class=ProjectValidator
    )
    assert isinstance(result, validation.ValidateResult)
    assert not result.valid
    assert result.errors[0]["code"] == "PROJECT_LOGGING"
    assert result.to_dict()["valid"] is False
    assert validation.validate_shiny_code("from shiny import ui").valid


@pytest.mark.parametrize("directive", ["ignore", "ignore-next-line"])
@pytest.mark.parametrize(
    "rules", ["", " INPUT_ASSIGNMENT", " INPUT_ASSIGNMENT, UNCALLED_INPUT"]
)
def test_comment_suppression(directive: str, rules: str) -> None:
    comment = f"# shiny: {directive}{rules}"
    code = (
        f"input.x = 10  {comment}"
        if directive == "ignore"
        else f"{comment}\ninput.x = 10"
    )
    report = validate_shiny_code(code)
    assert report.valid
    assert not report.errors


def test_suppression_is_specific_and_only_reads_comments() -> None:
    report = validate_shiny_code('message = "# shiny: ignore-next-line"\ninput.x = 10')
    assert not report.valid
    report = validate_shiny_code("input.x = 10  # shiny: ignore UNCALLED_INPUT")
    assert not report.valid
    report = validate_shiny_code("input.x = 10  # shiny: ignore\ninput.y = 20")
    assert [issue["line"] for issue in report.errors] == [2]


def test_suppression_reaches_cli_and_startup(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    from click.testing import CliRunner

    from shiny._main import main
    from shiny._main._run import _validate_app_file

    code = "input.x = 10  # shiny: ignore INPUT_ASSIGNMENT"
    result = CliRunner().invoke(main, ["validate", "--code", code, "--json"])
    assert result.exit_code == 0
    path = tmp_path / "app.py"
    path.write_text(code)
    _validate_app_file(path)
    assert not capsys.readouterr().err


def test_shared_editor_suppression_fixtures() -> None:
    import json
    from pathlib import Path

    fixtures = json.loads(
        (Path(__file__).parent / "fixtures/validation-suppressions.json").read_text()
    )
    for fixture in fixtures:
        result = validate_shiny_code(fixture["code"])
        assert [issue["line"] for issue in result.warnings] == fixture[
            "lines"
        ], fixture["name"]
        assert not result.errors


def test_file_validation_uses_custom_validator(tmp_path: Path) -> None:
    import ast

    from shiny.validate import ShinyCodeValidator, validate_shiny_file

    class ProjectValidator(ShinyCodeValidator):
        def visit_Call(self, node: ast.Call) -> None:
            self.result.add_warning(node.lineno, "Project call", "PROJECT_CALL")
            super().visit_Call(node)

    path = tmp_path / "app.py"
    path.write_text("print('hello') # shiny: ignore PROJECT_CALL")
    assert validate_shiny_file(path, validator_class=ProjectValidator).valid
    path.write_text("print('hello')")
    result = validate_shiny_file(path, validator_class=ProjectValidator)
    assert not result.valid
    assert result.warnings[0]["code"] == "PROJECT_CALL"


def test_error_results_use_same_report_shape(tmp_path: Path) -> None:
    from shiny.validate import validate_shiny_file

    syntax = validate_shiny_code("def broken( # shiny: ignore")
    missing = validate_shiny_file(tmp_path / "missing.py")
    assert not syntax.valid and not missing.valid
    assert syntax.errors[0]["code"] == "SYNTAX_ERROR"
    assert missing.errors[0]["code"] == "FILE_NOT_FOUND"
    assert syntax.to_dict().keys() == validate_shiny_code("pass").to_dict().keys()
    assert missing.to_dict().keys() == syntax.to_dict().keys()

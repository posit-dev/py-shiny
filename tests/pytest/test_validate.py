from __future__ import annotations

import sys
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
    assert not report.valid
    assert any(err["code"] == "UNCALLED_INPUT" for err in report.errors)
    assert any("parentheses" in err["message"] for err in report.errors)
    assert (
        "Code structure matches Python Shiny best practices." not in report.suggestions
    )
    assert validate_shiny_code(
        "from shiny import render, input\n@render.text\ndef txt():\n    return input.val.is_set()"
    ).clean


def test_validate_duplicate_input_ids() -> None:
    code = 'from shiny import ui\nui.input_text("name", "Label 1")\nui.input_text("name", "Label 2")'
    report = validate_shiny_code(code)
    assert report.valid and not report.clean
    assert any(warn["code"] == "DUPLICATE_ID" for warn in report.warnings)


def test_validate_duplicate_output_ids() -> None:
    code = 'from shiny import ui\nui.output_text("txt")\nui.output_text("txt")'
    report = validate_shiny_code(code)
    assert report.valid and not report.clean
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


def test_python_level_mistakes_are_left_to_type_checkers() -> None:
    # Unknown imports, redeclared function names, and attribute access on a
    # reactive object are all reported by pyright/pylance already.
    assert validate_shiny_code("from shiny import shinyApp, fluidPage").clean
    report = validate_shiny_code(
        "from shiny import render\n"
        "@render.text\ndef dup():\n    return 'one'\n"
        "@render.text\ndef dup():\n    return 'two'\n"
    )
    assert report.clean
    assert report.detected_outputs == ["dup"]
    assert validate_shiny_code(
        "from shiny import reactive\nstate = reactive.value([])\n"
        "@reactive.effect\ndef grow():\n    state.append(1)\n    state[0]\n"
    ).clean


def test_duplicate_ids_are_scoped_to_their_function() -> None:
    module_code = (
        "from shiny import module, ui\n"
        "@module.ui\ndef first():\n    return ui.input_text('name', 'Name')\n"
        "@module.ui\ndef second():\n    return ui.input_text('name', 'Name')\n"
        "app_ui = ui.page_fluid(ui.input_text('name', 'Name'))\n"
    )
    assert validate_shiny_code(module_code).clean
    report = validate_shiny_code(
        "from shiny import module, ui\n"
        "@module.ui\ndef first():\n"
        "    return ui.div(ui.input_text('name', 'A'), ui.input_text('name', 'B'))\n"
    )
    assert [(w["code"], w["line"]) for w in report.warnings] == [("DUPLICATE_ID", 4)]


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


def test_runtime_outputs_duplicate_warning(tmp_path: Path) -> None:
    import warnings

    from shiny.express import wrap_express_app
    from shiny.express._stub_session import ExpressStubSession
    from shiny.session._utils import session_context

    session = cast(Session, _StubSession())
    outputs_map: dict[str, Any] = {}
    outputs = Outputs(session, ns=ResolvedId(""), outputs=outputs_map)

    @outputs
    @render.text
    def result() -> str:
        return "first"

    with pytest.warns(RuntimeWarning, match="Duplicate output 'result'") as record:

        @outputs
        @render.text
        def result() -> str:  # noqa: F811
            return "second"

    assert record[0].filename == __file__

    # The legacy `@output` above `@render.*` re-registers the same renderer
    # that `@render.*` auto-registered, which is not a duplicate.
    with warnings.catch_warnings():
        warnings.simplefilter("error", RuntimeWarning)

        @outputs
        @render.text
        def legacy() -> str:
            return "legacy"

        outputs(legacy)

    app_file = tmp_path / "app.py"
    app_file.write_text(
        "from shiny.express import render\n"
        "@render.text\n"
        "def dup():\n"
        "    return 'one'\n"
        "@render.text\n"
        "def dup():\n"
        "    return 'two'\n"
    )
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always", RuntimeWarning)
        app = wrap_express_app(app_file)
        s2 = ExpressStubSession()
        with session_context(s2):
            assert app.server is not None
            app.server(s2.input, s2.output, s2)

    dup_warnings = [w for w in caught if "Duplicate output 'dup'" in str(w.message)]
    assert len(dup_warnings) == 1
    assert Path(dup_warnings[0].filename).resolve() == app_file.resolve()
    assert dup_warnings[0].lineno == 6


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


@pytest.mark.parametrize(
    "decorators, below",
    [
        ("@reactive.event(input.go)\n@reactive.effect", "reactive.effect"),
        ("@reactive.event(input.go)\n@reactive.calc", "reactive.calc"),
        ("@reactive.event(input.go)\n@render.text", "render.text"),
        ("@event(input.go)\n@effect", "reactive.effect"),
    ],
)
def test_reactive_event_above_its_wrapper_is_an_error(
    decorators: str, below: str
) -> None:
    code = (
        "from shiny import reactive, render\n"
        "from shiny.reactive import effect, event\n"
        f"{decorators}\ndef handler():\n    return 1\n"
    )
    report = validate_shiny_code(code)
    assert [(e["code"], e["line"]) for e in report.errors] == [("DECORATOR_ORDER", 5)]
    assert f"below '@{below}'" in report.errors[0]["message"]
    assert validate_shiny_code(
        "from shiny import reactive\n"
        "@reactive.effect\n@reactive.event(input.go)\ndef handler():\n    pass\n"
    ).clean


def test_effect_returning_a_value_is_a_warning() -> None:
    report = validate_shiny_code(
        "from shiny import reactive\n"
        "@reactive.effect\ndef compute():\n    if True:\n        return 1\n"
    )
    assert [(w["code"], w["line"]) for w in report.warnings] == [
        ("EFFECT_RETURNS_VALUE", 5)
    ]
    for body in (
        "    return\n",
        "    return None\n",
        "    return state.set(1)\n",
        "    def inner():\n        return 1\n",
        "    callback = lambda: 1\n",
    ):
        assert validate_shiny_code(
            "from shiny import reactive\nstate = reactive.value(0)\n"
            f"@reactive.effect\ndef compute():\n{body}"
        ).clean, body


def test_output_and_renderer_pairing_in_core_mode() -> None:
    report = validate_shiny_code(
        "from shiny import App, render, ui\n"
        "app_ui = ui.page_fluid(\n"
        "    ui.output_text('shown'),\n"
        "    ui.output_plot('never_rendered'),\n"
        "    ui.download_button('report', 'Download'),\n"
        ")\n"
        "def server(input, output, session):\n"
        "    @render.text\n    def shown():\n        return 'x'\n"
        "    @render.text\n    def never_shown():\n        return 'y'\n"
        "    @output(id='report')\n    @render.download\n    def download():\n"
        "        yield 'x'\n"
        "app = App(app_ui, server)\n"
    )
    assert [(w["code"], w["line"]) for w in report.warnings] == [
        ("OUTPUT_WITHOUT_RENDERER", 4),
        ("RENDERER_WITHOUT_OUTPUT", 12),
    ]


@pytest.mark.parametrize(
    "code",
    [
        # Express apps place renderers themselves.
        "from shiny.express import render, ui\nui.input_text('x', 'X')\n"
        "@render.text\ndef shown():\n    return 'x'\n",
        # Module UI/server IDs are namespaced, so they are not paired.
        "from shiny import App, module, render, ui\n"
        "@module.ui\ndef panel_ui():\n    return ui.output_text('inner')\n"
        "@module.server\ndef panel_server(input, output, session):\n"
        "    @render.text\n    def other():\n        return 'x'\n"
        "app_ui = ui.page_fluid(panel_ui('a'), ui.output_text('top'))\n"
        "def server(input, output, session):\n"
        "    panel_server('a')\n"
        "    @render.text\n    def top():\n        return 'x'\n",
        # UI lives elsewhere (no placeholders found), so renderers are not judged.
        "from shiny import render\n"
        "def server(input, output, session):\n"
        "    @render.text\n    def anything():\n        return 'x'\n",
        # Server lives elsewhere (no renderers found), so placeholders are not judged.
        "from shiny import ui\napp_ui = ui.page_fluid(ui.output_text('anything'))\n",
        # A custom renderer decorator still backs the placeholder.
        "from shiny import App, render, ui\nfrom my_renderers import render_caps\n"
        "app_ui = ui.page_fluid(ui.output_text('caps'), ui.output_text('plain'))\n"
        "def server(input, output, session):\n"
        "    @render_caps\n    def caps():\n        return 'x'\n"
        "    @render.text\n    def plain():\n        return 'x'\n",
        # A renderer returned from render.ui places itself.
        "from shiny import App, render, ui\n"
        "app_ui = ui.page_fluid(ui.output_ui('dynamic'))\n"
        "def server(input, output, session):\n"
        "    @render.ui\n    def dynamic():\n"
        "        @render.text\n        def inner():\n            return 'x'\n"
        "        return inner\n",
    ],
)
def test_output_pairing_is_not_reported_when_it_cannot_be_judged(code: str) -> None:
    assert validate_shiny_code(code).clean


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
        issues = result.errors + result.warnings
        assert [issue["line"] for issue in issues] == fixture["lines"], fixture["name"]


def test_file_validation_uses_custom_validator(tmp_path: Path) -> None:
    import ast

    from shiny.validate import ShinyCodeValidator, validate_shiny_file

    class ProjectValidator(ShinyCodeValidator):
        def visit_Call(self, node: ast.Call) -> None:
            self.result.add_warning(node.lineno, "Project call", "PROJECT_CALL")
            super().visit_Call(node)

    path = tmp_path / "app.py"
    path.write_text("print('hello') # shiny: ignore PROJECT_CALL")
    assert validate_shiny_file(path, validator_class=ProjectValidator).clean
    path.write_text("print('hello')")
    result = validate_shiny_file(path, validator_class=ProjectValidator)
    assert not result.clean
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


class _FakeEntryPoint:
    def __init__(self, name: str, obj: object) -> None:
        self.name = name
        self.value = f"fake:{name}"
        self._obj = obj

    def load(self) -> object:
        if isinstance(self._obj, Exception):
            raise self._obj
        return self._obj


def _print_rule_class() -> type[Any]:
    import ast

    from shiny.validate import ValidationRule

    class NoPrintRule(ValidationRule):
        def visit_Call(self, node: ast.Call) -> None:
            if isinstance(node.func, ast.Name) and node.func.id == "print":
                self.result.add_warning(node.lineno, "No print", "PLUGIN_PRINT")
            self.generic_visit(node)

    return NoPrintRule


class _Plugins:
    def __init__(self, monkeypatch: pytest.MonkeyPatch) -> None:
        self.monkeypatch = monkeypatch
        self.calls: list[str] = []

    def __call__(self, *eps: _FakeEntryPoint) -> None:
        import shiny._validate as validate_mod

        def fake_entry_points(*, group: str) -> list[_FakeEntryPoint]:
            self.calls.append(group)
            return list(eps)

        self.monkeypatch.setattr(validate_mod, "entry_points", fake_entry_points)
        validate_mod._clear_installed_rules()


@pytest.fixture
def fake_plugins(monkeypatch: pytest.MonkeyPatch):
    from shiny._validate import _clear_installed_rules

    yield _Plugins(monkeypatch)
    _clear_installed_rules()


def test_installed_plugins_compose_and_run_once(fake_plugins: _Plugins) -> None:
    import ast

    from shiny.validate import ValidateResult, installed_validation_rules

    def no_global_rule(tree: ast.Module, result: ValidateResult) -> None:
        for node in ast.walk(tree):
            if isinstance(node, ast.Global):
                result.add_error(node.lineno, "No global", "PLUGIN_GLOBAL")

    fake_plugins(
        _FakeEntryPoint("prints", _print_rule_class()),
        _FakeEntryPoint("globals", no_global_rule),
    )
    result = validate_shiny_code("def f():\n    global x\nprint('hi')")
    assert [e["code"] for e in result.errors] == ["PLUGIN_GLOBAL"]
    assert [w["code"] for w in result.warnings] == ["PLUGIN_PRINT"]

    validate_shiny_code("pass")
    installed_validation_rules()
    assert fake_plugins.calls == ["shiny.validators"]


def test_explicit_rules_override_installed_plugins(fake_plugins: _Plugins) -> None:
    fake_plugins(_FakeEntryPoint("prints", _print_rule_class()))
    assert validate_shiny_code("print('hi')", rules=()).clean
    assert not validate_shiny_code("print('hi')").clean


def test_plugin_findings_are_suppressible(fake_plugins: _Plugins) -> None:
    fake_plugins(_FakeEntryPoint("prints", _print_rule_class()))
    assert validate_shiny_code("print('hi')  # shiny: ignore PLUGIN_PRINT").clean


@pytest.mark.parametrize(
    "obj, fragment",
    [
        (ImportError("missing dep"), "ImportError: missing dep"),
        (int, "must subclass"),
        (42, "not a ValidationRule"),
    ],
)
def test_broken_plugin_is_reported_loudly(
    fake_plugins: _Plugins, obj: object, fragment: str
) -> None:
    fake_plugins(
        _FakeEntryPoint("broken", obj), _FakeEntryPoint("ok", _print_rule_class())
    )
    result = validate_shiny_code("print('hi')")
    codes = [w["code"] for w in result.warnings]
    assert codes == ["VALIDATOR_PLUGIN_ERROR", "PLUGIN_PRINT"]
    assert "broken (fake:broken)" in result.warnings[0]["message"]
    assert fragment in result.warnings[0]["message"]


def test_plugin_crash_does_not_stop_validation() -> None:
    import ast

    from shiny.validate import ValidateResult

    def crashing(tree: ast.Module, result: ValidateResult) -> None:
        raise RuntimeError("boom")

    result = validate_shiny_code("input.x = 1", rules=[crashing])
    assert [e["code"] for e in result.errors] == ["INPUT_ASSIGNMENT"]
    assert result.warnings[0]["code"] == "VALIDATOR_PLUGIN_ERROR"
    assert "RuntimeError: boom" in result.warnings[0]["message"]


def test_load_validation_rule(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from shiny.validate import ValidationRule, load_validation_rule

    (tmp_path / "local_rules_mod.py").write_text(
        "from shiny.validate import ValidationRule\n"
        "class Rules:\n"
        "    class Inner(ValidationRule):\n"
        "        pass\n"
        "def func(tree, result):\n"
        "    pass\n"
        "NOT_A_RULE = 1\n"
    )
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(sys, "path", list(sys.path))
    inner = load_validation_rule("local_rules_mod:Rules.Inner")
    assert isinstance(inner, type) and issubclass(inner, ValidationRule)
    assert callable(load_validation_rule("local_rules_mod:func"))
    with pytest.raises(TypeError):
        load_validation_rule("local_rules_mod:NOT_A_RULE")
    with pytest.raises(ValueError):
        load_validation_rule("local_rules_mod")
    with pytest.raises(AttributeError):
        load_validation_rule("local_rules_mod:missing")


def test_startup_validation_runs_plugins(
    fake_plugins: _Plugins, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    from shiny._main._run import _validate_app_file

    fake_plugins(_FakeEntryPoint("prints", _print_rule_class()))
    path = tmp_path / "app.py"
    path.write_text("print('hi')")
    _validate_app_file(path)
    assert "No print" in capsys.readouterr().err


def test_plugin_ids_share_namespace_with_core() -> None:
    import ast

    from shiny.validate import ValidateResult

    def rule(tree: ast.Module, result: ValidateResult) -> None:
        result.register_id("output", "w", 2)

    result = validate_shiny_code(
        "from shiny import ui\nui.output_text('w')", rules=[rule]
    )
    assert [w["code"] for w in result.warnings] == ["DUPLICATE_ID"]


@pytest.mark.parametrize(
    "imports, render_dec, calc_dec, ui_call",
    [
        (
            "import shiny",
            "shiny.render.text",
            "shiny.reactive.calc",
            "shiny.ui.input_slider",
        ),
        (
            "import shiny as s",
            "s.render.text",
            "s.reactive.calc",
            "s.ui.input_slider",
        ),
        (
            "from shiny import render as r, reactive as rx, ui as u",
            "r.text",
            "rx.calc",
            "u.input_slider",
        ),
        (
            "from shiny.render import text\nfrom shiny.reactive import calc\nfrom shiny.ui import input_slider",
            "text",
            "calc",
            "input_slider",
        ),
    ],
)
def test_validate_import_styles_and_aliases(
    imports: str, render_dec: str, calc_dec: str, ui_call: str
) -> None:
    code = (
        f"{imports}\n"
        f'{ui_call}("n", "N", 1, 10, 5)\n'
        f"@{calc_dec}\n"
        "def doubled():\n"
        "    return input.n() * 2\n"
        f"@{render_dec}\n"
        "def out():\n"
        "    return input.n\n"
    )
    result = validate_shiny_code(code, rules=())
    assert result.detected_inputs == ["n"]
    assert result.detected_reactives == ["doubled"]
    assert result.detected_outputs == ["out"]
    assert [err["code"] for err in result.errors] == ["UNCALLED_INPUT"]

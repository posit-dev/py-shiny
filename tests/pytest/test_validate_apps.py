from pathlib import Path

import pytest

from shiny.validate import validate_shiny_code, validate_shiny_file


def test_existing_ai_apps_have_no_validation_findings() -> None:
    app_dir = Path(__file__).resolve().parents[1] / "playwright/ai_generated_apps"
    apps = sorted(app_dir.rglob("app*.py"))
    assert apps, "No AI app fixtures found"
    for app in apps:
        result = validate_shiny_file(app, rules=())
        assert result.clean, (app, result.errors + result.warnings)


def test_exception_targets_hide_input_in_both_validators() -> None:
    result = validate_shiny_code(
        "from shiny import reactive\nfrom shiny.express import input, render\n"
        "class Failure(Exception):\n    def status(self):\n        return 'failed'\n"
        "@reactive.extended_task\nasync def work():\n"
        "    try:\n        raise Failure()\n"
        "    except Failure as input:\n        return input.status()\n"
        "@render.text\ndef shown():\n"
        "    try:\n        raise LookupError('missing')\n"
        "    except LookupError as input:\n        return str(input.args)\n",
        rules=(),
    )
    assert result.clean, result.errors + result.warnings


@pytest.mark.parametrize(
    "code",
    [
        pytest.param(
            "def server(input, output, session):\n"
            "    def helper(value=input.n()):\n        return value\n",
            id="function-default",
        ),
        pytest.param(
            "def server(input, output, session):\n"
            "    def helper(*, value=input.n()):\n        return value\n",
            id="keyword-default",
        ),
        pytest.param(
            "from shiny import reactive\nstate = reactive.value(0)\n"
            "callback = lambda value=state(): value\n",
            id="lambda-default",
        ),
    ],
)
def test_reactive_reads_in_defaults_use_the_enclosing_context(code: str) -> None:
    result = validate_shiny_code(code, rules=())
    assert [issue["code"] for issue in result.errors] == [
        "REACTIVE_READ_OUTSIDE_CONTEXT"
    ]


def test_generic_value_constructors_are_detected() -> None:
    result = validate_shiny_code(
        "from shiny.reactive import Value as Cell\n"
        "state = Cell[int](0)\nvalue = state.get()\n",
        rules=(),
    )
    assert result.detected_reactives == ["state"]
    assert [issue["code"] for issue in result.errors] == [
        "REACTIVE_READ_OUTSIDE_CONTEXT"
    ]


def test_uncalled_input_subscripts_are_reported() -> None:
    result = validate_shiny_code(
        "from shiny.express import input as form, render\n"
        "@render.text\ndef shown():\n    return f\"{form['n']}\"\n",
        rules=(),
    )
    assert result.valid
    assert [issue["code"] for issue in result.warnings] == ["UNCALLED_INPUT"]

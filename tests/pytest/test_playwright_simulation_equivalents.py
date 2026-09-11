from __future__ import annotations

from pathlib import Path

from shiny.testserver import test_server

HERE = Path(__file__).parent.parent
REPO_ROOT = HERE.parent


def test_sim_output_text():
    app_path = REPO_ROOT / "shiny" / "api-examples" / "output_text" / "app-core.py"

    with test_server(app_path) as ts:
        ts.set_inputs(txt="delete me")
        assert ts.is_ok is True
        assert ts.get_output("text") == "delete me"
        assert ts.get_output("verb") == "delete me"
        assert ts.get_output("verb_no_placeholder") == "delete me"

        ts.set_inputs(txt="test value 42")
        assert ts.is_ok is True
        assert ts.get_output("text") == "test value 42"
        assert ts.get_output("verb") == "test value 42"
        assert ts.get_output("verb_no_placeholder") == "test value 42"


def test_sim_output_code():
    app_path = REPO_ROOT / "shiny" / "api-examples" / "output_code" / "app-core.py"

    with test_server(app_path) as ts:
        ts.set_inputs(source="")
        assert ts.is_ok is True
        assert ts.get_output("code_default") == ""
        assert ts.get_output("code_no_placeholder") == ""

        new_val = "print('testing output_code')\nfor i in range(2):\n    print(i)"
        ts.set_inputs(source=new_val)
        assert ts.is_ok is True
        assert ts.get_output("code_default") == new_val
        assert ts.get_output("code_no_placeholder") == new_val


def test_sim_numeric_kitchensink():
    app_path = (
        REPO_ROOT
        / "tests"
        / "playwright"
        / "shiny"
        / "inputs"
        / "input_kitchensink"
        / "input_numeric_kitchensink"
        / "app.py"
    )

    with test_server(app_path) as ts:
        ts.set_inputs(default=10, min_max=50, step=2.5, width=15)
        assert ts.is_ok is True
        assert ts.get_output("default_txt") == "10"
        assert ts.get_output("min_max_txt") == "50"
        assert ts.get_output("step_txt") == "2.5"
        assert ts.get_output("width_txt") == "15"

        ts.set_inputs(default=20, width=20)
        assert ts.is_ok is True
        assert ts.get_output("default_txt") == "20"
        assert ts.get_output("width_txt") == "20"


def test_sim_action_button_kitchensink():
    app_path = (
        REPO_ROOT
        / "tests"
        / "playwright"
        / "shiny"
        / "inputs"
        / "input_kitchensink"
        / "input_action_button_kitchensink"
        / "app.py"
    )

    with test_server(app_path) as ts:
        ts.set_inputs(default=0)
        assert ts.is_ok is True
        assert ts.get_output("default_txt") == "Button clicked 0 times"

        ts.set_inputs(default=1)
        assert ts.is_ok is True
        assert ts.get_output("default_txt") == "Button clicked 1 times"


def test_sim_app_test_values():
    app_path = REPO_ROOT / "tests" / "playwright" / "shiny" / "test_mode" / "app.py"

    with test_server(app_path) as ts:
        ts.set_inputs(name="abc", secret="hunter2", n=20)
        assert ts.is_ok is True
        assert ts.get_output("double_txt") == "doubled = 40"
        assert ts.get_export("doubled") == 40

        ts.set_inputs(name="xyz", n=30)
        assert ts.is_ok is True
        assert ts.get_output("double_txt") == "doubled = 60"
        assert ts.get_export("doubled") == 60

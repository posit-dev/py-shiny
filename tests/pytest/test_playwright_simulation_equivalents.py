from __future__ import annotations

from pathlib import Path

from shiny.pytest import test_server

HERE = Path(__file__).parent.parent
REPO_ROOT = HERE.parent


def test_sim_output_text():
    app_path = REPO_ROOT / "shiny" / "api-examples" / "output_text" / "app-core.py"

    res_default = test_server(app_path, inputs={"txt": "delete me"})
    assert res_default.success is True
    assert res_default.outputs["text"] == "delete me"
    assert res_default.outputs["verb"] == "delete me"
    assert res_default.outputs["verb_no_placeholder"] == "delete me"

    res_updated = test_server(app_path, inputs={"txt": "test value 42"})
    assert res_updated.success is True
    assert res_updated.outputs["text"] == "test value 42"
    assert res_updated.outputs["verb"] == "test value 42"
    assert res_updated.outputs["verb_no_placeholder"] == "test value 42"


def test_sim_output_code():
    app_path = REPO_ROOT / "shiny" / "api-examples" / "output_code" / "app-core.py"

    res_default = test_server(app_path, inputs={"source": ""})
    assert res_default.success is True
    assert res_default.outputs["code_default"] == ""
    assert res_default.outputs["code_no_placeholder"] == ""

    new_val = "print('testing output_code')\nfor i in range(2):\n    print(i)"
    res = test_server(app_path, inputs={"source": new_val})
    assert res.success is True
    assert res.outputs["code_default"] == new_val
    assert res.outputs["code_no_placeholder"] == new_val


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

    res_init = test_server(
        app_path, inputs={"default": 10, "min_max": 50, "step": 2.5, "width": 15}
    )
    assert res_init.success is True
    assert res_init.outputs["default_txt"] == "10"
    assert res_init.outputs["min_max_txt"] == "50"
    assert res_init.outputs["step_txt"] == "2.5"
    assert res_init.outputs["width_txt"] == "15"

    res_updated = test_server(app_path, inputs={"default": 20, "width": 20})
    assert res_updated.success is True
    assert res_updated.outputs["default_txt"] == "20"
    assert res_updated.outputs["width_txt"] == "20"


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

    res_init = test_server(app_path, inputs={"default": 0})
    assert res_init.success is True
    assert res_init.outputs["default_txt"] == "Button clicked 0 times"

    res_clicked = test_server(app_path, inputs={"default": 1})
    assert res_clicked.success is True
    assert res_clicked.outputs["default_txt"] == "Button clicked 1 times"


def test_sim_app_test_values():
    app_path = REPO_ROOT / "tests" / "playwright" / "shiny" / "test_mode" / "app.py"

    res_init = test_server(
        app_path, inputs={"name": "abc", "secret": "hunter2", "n": 20}
    )
    assert res_init.success is True
    assert res_init.outputs["double_txt"] == "doubled = 40"
    assert res_init.exports["doubled"] == 40

    res_updated = test_server(app_path, inputs={"name": "xyz", "n": 30})
    assert res_updated.success is True
    assert res_updated.outputs["double_txt"] == "doubled = 60"
    assert res_updated.exports["doubled"] == 60

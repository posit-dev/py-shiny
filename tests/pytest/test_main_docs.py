from __future__ import annotations

import json
from typing import Any, cast

from click.testing import CliRunner

from shiny._main import main


def test_docs_single_function() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["docs", "shiny.ui.value_box"])

    assert result.exit_code == 0
    lines = result.output.strip().splitlines()
    first_line = lines[0]
    assert first_line.startswith("def value_box(")
    assert first_line.endswith(":")
    assert "title: TagChild" in first_line
    assert "-> Tag" in first_line
    assert "Value box" in result.output
    assert "categories" not in result.output.lower()


def test_docs_multiple_functions() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["docs", "shiny.ui.value_box", "shiny.ui.card"])

    assert result.exit_code == 0
    assert "\n\n---\n\n" in result.output
    blocks = result.output.strip().split("\n\n---\n\n")
    assert len(blocks) == 2

    assert blocks[0].splitlines()[0].startswith("def value_box(")
    assert "Value box" in blocks[0]

    assert blocks[1].splitlines()[0].startswith("def card(")
    assert "A Bootstrap card component" in blocks[1]


def test_docs_controller_class() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["docs", "shiny.playwright.controller.Accordion"])

    assert result.exit_code == 0
    lines = result.output.strip().splitlines()
    assert lines[0].startswith("class Accordion")
    assert "Controller for :func:`shiny.ui.accordion`." in result.output
    assert "Methods" in result.output
    assert "def accordion_panel(" in result.output
    assert "def set(" in result.output
    assert "def expect_class(" in result.output


def test_docs_controller_method() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["docs", "shiny.playwright.controller.Accordion.set"])

    assert result.exit_code == 0
    lines = result.output.strip().splitlines()
    assert lines[0].startswith("def set(")
    assert "open: str | list[str]" in lines[0]
    assert "-> None" in lines[0]
    assert "Sets the state of the accordion panel." in result.output


def test_docs_json_mode() -> None:
    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "docs",
            "--json",
            "shiny.ui.value_box",
            "shiny.playwright.controller.Accordion",
        ],
    )

    assert result.exit_code == 0
    data: list[dict[str, Any]] = json.loads(result.output)
    assert isinstance(data, list)
    assert len(data) == 2

    vb = data[0]
    assert vb["name"] == "shiny.ui.value_box"
    assert vb["type"] == "function"
    assert vb["return_type"] == "Tag"
    assert str(vb["signature"]).startswith("def value_box(")
    assert "Value box" in str(vb["docstring"])
    assert isinstance(vb["parameters"], list)
    parameters = cast("list[dict[str, Any]]", vb["parameters"])
    param_names = [p["name"] for p in parameters]
    assert "title" in param_names
    assert "value" in param_names
    assert "*args" in param_names
    assert "**kwargs" in param_names
    title_param = next(p for p in parameters if p["name"] == "title")
    assert title_param["type"] == "TagChild"
    assert "category" not in vb
    assert "categories" not in vb

    acc = data[1]
    assert acc["name"] == "shiny.playwright.controller.Accordion"
    assert acc["type"] == "class"
    assert str(acc["signature"]).startswith("class Accordion")
    assert isinstance(acc["methods"], list)
    methods = cast("list[dict[str, Any]]", acc["methods"])
    method_names = [m["name"] for m in methods]

    assert "accordion_panel" in method_names
    assert "set" in method_names
    assert "expect_class" in method_names

    set_method = next(m for m in methods if m["name"] == "set")
    assert set_method["return_type"] == "None"
    assert str(set_method["signature"]).startswith("def set(")


def test_docs_implied_shiny_prefix() -> None:
    runner = CliRunner()

    res_ui = runner.invoke(main, ["docs", "ui.value_box"])
    assert res_ui.exit_code == 0
    assert "def value_box(" in res_ui.output

    res_ctrl = runner.invoke(main, ["docs", "playwright.controller.Accordion"])
    assert res_ctrl.exit_code == 0
    assert "class Accordion" in res_ctrl.output

    res_calc = runner.invoke(main, ["docs", "reactive.calc"])
    assert res_calc.exit_code == 0
    assert "def calc(" in res_calc.output


def test_docs_no_bare_magic_lookups() -> None:
    runner = CliRunner()

    res_ctrl = runner.invoke(main, ["docs", "Accordion"])
    assert res_ctrl.exit_code != 0
    assert "Could not find documentation for 'Accordion'." in res_ctrl.output

    res_calc = runner.invoke(main, ["docs", "calc"])
    assert res_calc.exit_code != 0
    assert "Could not find documentation for 'calc'." in res_calc.output

    res_method = runner.invoke(main, ["docs", "Accordion.expect_height"])
    assert res_method.exit_code != 0
    assert (
        "Could not find documentation for 'Accordion.expect_height'."
        in res_method.output
    )


def test_docs_method_path() -> None:
    runner = CliRunner()

    res_full = runner.invoke(
        main, ["docs", "shiny.playwright.controller.Accordion.expect_height"]
    )
    assert res_full.exit_code == 0
    assert "def expect_height(" in res_full.output
    assert "Expects the accordion to have the specified height." in res_full.output

    res_implied = runner.invoke(
        main, ["docs", "playwright.controller.Accordion.expect_height"]
    )
    assert res_implied.exit_code == 0
    assert "def expect_height(" in res_implied.output


def test_docs_autocomplete_flag() -> None:
    runner = CliRunner()
    result = runner.invoke(
        main, ["docs", "--complete", "playwright.controller.Accordion.expect"]
    )

    assert result.exit_code == 0
    assert "playwright.controller.Accordion.expect_height" in result.output
    assert "playwright.controller.Accordion.expect_class" in result.output


def test_docs_autocomplete_json() -> None:
    runner = CliRunner()
    result = runner.invoke(
        main,
        ["docs", "--complete", "playwright.controller.Accordion.expect", "--json"],
    )

    assert result.exit_code == 0
    items = json.loads(result.output)
    assert isinstance(items, list)
    assert "playwright.controller.Accordion.expect_height" in items
    assert "playwright.controller.Accordion.expect_class" in items


def test_shell_complete_symbol_names() -> None:
    from click import Argument, Context

    from shiny._main._docs import _complete_symbol_names

    ctx = Context(main)
    param = Argument(["names"])
    items = _complete_symbol_names(ctx, param, "playwright.controller.Accordion.exp")
    values = [item.value for item in items]
    assert "playwright.controller.Accordion.expect_height" in values
    assert "playwright.controller.Accordion.expect_class" in values
    assert "shiny.playwright.controller.Accordion.expect_height" not in values


def test_docs_unknown_symbol() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["docs", "non_existent_symbol_xyz"])

    assert result.exit_code != 0
    assert (
        "Could not find documentation for 'non_existent_symbol_xyz'." in result.output
    )


def test_docs_three_with_one_error_at_start() -> None:
    runner = CliRunner()
    result = runner.invoke(
        main,
        ["docs", "non_existent_symbol", "shiny.ui.card", "shiny.ui.value_box"],
    )

    assert result.exit_code != 0
    error_idx = result.output.find(
        "Could not find documentation for 'non_existent_symbol'."
    )
    card_idx = result.output.find("def card(")
    value_box_idx = result.output.find("def value_box(")

    assert error_idx != -1
    assert card_idx != -1
    assert value_box_idx != -1
    assert error_idx < card_idx
    assert error_idx < value_box_idx


def test_docs_three_with_one_error_in_middle() -> None:
    runner = CliRunner()
    result = runner.invoke(
        main,
        ["docs", "shiny.ui.card", "non_existent_symbol", "shiny.ui.value_box"],
    )

    assert result.exit_code != 0
    error_idx = result.output.find(
        "Could not find documentation for 'non_existent_symbol'."
    )
    card_idx = result.output.find("def card(")
    value_box_idx = result.output.find("def value_box(")

    assert error_idx != -1
    assert card_idx != -1
    assert value_box_idx != -1
    assert error_idx < card_idx
    assert error_idx < value_box_idx


def test_docs_three_with_one_error_at_end() -> None:
    runner = CliRunner()
    result = runner.invoke(
        main,
        ["docs", "shiny.ui.card", "shiny.ui.value_box", "non_existent_symbol"],
    )

    assert result.exit_code != 0
    error_idx = result.output.find(
        "Could not find documentation for 'non_existent_symbol'."
    )
    card_idx = result.output.find("def card(")
    value_box_idx = result.output.find("def value_box(")

    assert error_idx != -1
    assert card_idx != -1
    assert value_box_idx != -1
    assert error_idx < card_idx
    assert error_idx < value_box_idx


def test_docs_three_with_one_error_json_mode() -> None:
    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "docs",
            "--json",
            "shiny.ui.card",
            "non_existent_symbol",
            "shiny.ui.value_box",
        ],
    )

    assert result.exit_code != 0
    assert "Could not find documentation for 'non_existent_symbol'." in result.output
    error_idx = result.output.find(
        "Could not find documentation for 'non_existent_symbol'."
    )
    json_start_idx = result.output.find("[")
    assert error_idx != -1
    assert json_start_idx != -1
    assert error_idx < json_start_idx

    json_str = result.output[json_start_idx:]
    data = json.loads(json_str)
    assert len(data) == 2
    assert data[0]["name"] == "shiny.ui.card"
    assert data[1]["name"] == "shiny.ui.value_box"


def test_docs_fuzzy_suggestion_single() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["docs", "ui.value_bx"])

    assert result.exit_code != 0
    assert "Could not find documentation for 'ui.value_bx'." in result.output
    assert "Did you mean 'ui.value_box'?" in result.output


def test_docs_fuzzy_suggestion_multiple() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["docs", "Accordion"])

    assert result.exit_code != 0
    assert "Could not find documentation for 'Accordion'." in result.output
    assert "Did you mean" in result.output
    assert "'playwright.controller.Accordion'" in result.output


def test_docs_fuzzy_suggestion_method() -> None:
    runner = CliRunner()
    result = runner.invoke(
        main, ["docs", "playwright.controller.Accordion.expect_hight"]
    )

    assert result.exit_code != 0
    assert (
        "Could not find documentation for 'playwright.controller.Accordion.expect_hight'."
        in result.output
    )
    assert (
        "Did you mean 'playwright.controller.Accordion.expect_height'?" in result.output
    )


def test_docs_fuzzy_suggestion_shiny_prefix() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["docs", "shiny.ui.value_bx"])

    assert result.exit_code != 0
    assert "Could not find documentation for 'shiny.ui.value_bx'." in result.output
    assert "Did you mean 'shiny.ui.value_box'?" in result.output


def test_docs_no_args() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["docs"])

    assert result.exit_code != 0
    assert "Missing argument" in result.output

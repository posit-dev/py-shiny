from __future__ import annotations

from urllib.parse import urlencode

import pytest
from bs4 import BeautifulSoup
from htmltools import Tag
from starlette.requests import Request
from starlette.testclient import TestClient

from shiny import App, module, ui
from shiny.ui._input_select import SelectChoicesArg


@pytest.mark.parametrize("namespaced", [False, True], ids=["root", "module"])
@pytest.mark.parametrize("grouped", [False, True], ids=["list", "groups"])
@pytest.mark.parametrize(
    "multiple,saved,expected_selected",
    [
        pytest.param(False, '"Week"', ["Week"], id="single"),
        pytest.param(False, '"Quarter"', [], id="single-stale"),
        pytest.param(False, "null", ["Day"], id="single-null"),
        pytest.param(False, None, ["Month"], id="single-default"),
        pytest.param(True, '["Week"]', ["Week"], id="multiple-one"),
        pytest.param(True, '["Week","Day"]', ["Day", "Week"], id="multiple-two"),
        pytest.param(True, "null", [], id="multiple-null"),
        pytest.param(True, "[]", [], id="multiple-empty"),
        pytest.param(True, '["Quarter"]', [], id="multiple-stale"),
        pytest.param(True, None, ["Month"], id="multiple-default"),
    ],
)
def test_input_selectize_bookmark_restores_selection_without_replacing_choices(
    namespaced: bool,
    grouped: bool,
    multiple: bool,
    saved: str | None,
    expected_selected: list[str],
) -> None:
    choices: SelectChoicesArg = (
        {"Short": {"Day": "Daily", "Week": "Weekly"}, "Long": {"Month": "Monthly"}}
        if grouped
        else ["Day", "Week", "Month"]
    )

    def selectize_ui() -> Tag:
        return ui.input_selectize(
            "res",
            label="Resolution",
            choices=choices,
            selected=["Month"] if multiple else "Month",
            multiple=multiple,
        )

    namespaced_ui = module.ui(selectize_ui)

    def app_ui(request: Request) -> Tag:
        return ui.page_fluid(
            namespaced_ui("m") if namespaced else selectize_ui(),
            ui.input_text("other", label="Other", value="default"),
        )

    app = App(app_ui, server=None, bookmark_store="url")
    input_id = "m-res" if namespaced else "res"
    url = "/"
    if saved is not None:
        url += "?_inputs_&" + urlencode({input_id: saved, "other": '"restored"'})

    with TestClient(app, raise_server_exceptions=False) as client:
        response = client.get(url)

    assert response.status_code == 200
    soup = BeautifulSoup(response.text, "html.parser")
    options = soup.select(f"select#{input_id} option")
    assert [option.get("value") for option in options] == ["Day", "Week", "Month"]
    assert [option.text for option in options] == (
        ["Daily", "Weekly", "Monthly"] if grouped else ["Day", "Week", "Month"]
    )
    # Check the explicit HTML selection. A stale single value leaves no marked
    # option; the browser may subsequently select the first available option.
    assert [
        option.get("value") for option in options if option.has_attr("selected")
    ] == (expected_selected)
    if grouped:
        assert [
            group.get("label") for group in soup.select(f"select#{input_id} optgroup")
        ] == ["Short", "Long"]
    other = soup.select_one("input#other")
    assert other is not None
    assert other.get("value") == ("restored" if saved is not None else "default")

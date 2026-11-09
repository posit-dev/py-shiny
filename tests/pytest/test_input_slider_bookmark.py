"""Exercise slider bookmark restoration during the initial HTTP request."""

from __future__ import annotations

from datetime import date, datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlencode

import pytest
from htmltools import Tag
from starlette.requests import Request
from starlette.testclient import TestClient

from shiny import App, module, ui
from shiny.bookmark._types import BookmarkStore
from shiny.bookmark._utils import to_json_str


class SliderMarkup(HTMLParser):
    def __init__(self, html: str):
        super().__init__()
        self.inputs: list[dict[str, str | None]] = []
        self.feed(html)

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if tag == "input" and attributes.get("class") == "js-range-slider":
            self.inputs.append(attributes)


@pytest.mark.parametrize(
    "store,bookmarked", [("url", False), ("url", True), ("server", True)]
)
@pytest.mark.parametrize("namespaced", [False, True], ids=["root", "module"])
@pytest.mark.parametrize("ranged", [False, True], ids=["single", "range"])
@pytest.mark.parametrize("kind", ["date", "datetime", "number"])
def test_slider_bookmark_root_get(
    store: BookmarkStore,
    namespaced: bool,
    bookmarked: bool,
    ranged: bool,
    kind: str,
    tmp_path: Path,
) -> None:
    def control() -> Tag:
        if kind == "date":
            return ui.input_slider(
                "x",
                "X",
                date(2026, 1, 1),
                date(2026, 12, 31),
                (date(2026, 2, 1), date(2026, 3, 1)) if ranged else date(2026, 2, 1),
            )
        if kind == "datetime":
            return ui.input_slider(
                "x",
                "X",
                datetime(2026, 1, 1),
                datetime(2026, 12, 31),
                (
                    (datetime(2026, 2, 1), datetime(2026, 3, 1))
                    if ranged
                    else datetime(2026, 2, 1)
                ),
            )
        return ui.input_slider("x", "X", 0, 10, (2, 3) if ranged else 2)

    namespaced_control = module.ui(control)

    def app_ui(request: Request) -> Tag:
        return ui.page_fluid(namespaced_control("m") if namespaced else control())

    app = App(app_ui, server=None, bookmark_store=store)
    input_id = "m-x" if namespaced else "x"
    if kind == "date":
        saved = [date(2026, 6, 15), date(2026, 9, 20)] if ranged else date(2026, 6, 15)
        values = (
            [datetime(2026, 6, 15), datetime(2026, 9, 20)]
            if bookmarked
            else [datetime(2026, 2, 1), datetime(2026, 3, 1)]
        )
        expected = [
            value.replace(tzinfo=timezone.utc).timestamp() * 1000 for value in values
        ]
    elif kind == "datetime":
        saved = (
            [datetime(2026, 6, 15, 12, 34, 56), datetime(2026, 9, 20, 1, 2, 3)]
            if ranged
            else datetime(2026, 6, 15, 12, 34, 56)
        )
        values = (
            [datetime(2026, 6, 15, 12, 34, 56), datetime(2026, 9, 20, 1, 2, 3)]
            if bookmarked
            else [datetime(2026, 2, 1), datetime(2026, 3, 1)]
        )
        expected = [
            value.replace(tzinfo=timezone.utc).timestamp() * 1000 for value in values
        ]
    else:
        saved = [7, 9] if ranged else 7
        expected = [7, 9] if bookmarked else [2, 3]

    query = ""
    if bookmarked:
        if store == "server":
            (tmp_path / "input.json").write_text(
                to_json_str({input_id: saved}), encoding="utf-8"
            )
            app.set_bookmark_restore_dir_fn(lambda state_id: tmp_path)
            query = "_state_id_=bookmark"
        else:
            query = "_inputs_&" + urlencode({input_id: to_json_str(saved)})

    with TestClient(app) as client:
        response = client.get("/?" + query)
    assert response.status_code == 200
    markup = SliderMarkup(response.text)
    assert len(markup.inputs) == 1
    attrs = markup.inputs[0]
    assert attrs["id"] == input_id
    assert attrs["data-data-type"] == kind
    assert float(str(attrs["data-from"])) == expected[0]
    if ranged:
        assert attrs["data-type"] == "double"
        assert float(str(attrs["data-to"])) == expected[1]
    else:
        assert "data-to" not in attrs
    # Restoring a value must not change the app's bounds or step.
    default_attrs = SliderMarkup(str(control())).inputs[0]
    for key in ("data-min", "data-max", "data-step"):
        assert attrs[key] == default_attrs[key]


@pytest.mark.parametrize("kind", ["date", "datetime"])
@pytest.mark.parametrize("ranged", [False, True], ids=["single", "range"])
def test_malformed_date_bookmark_still_renders(kind: str, ranged: bool) -> None:
    """Decoding restored dates must not turn malformed strings into HTTP errors."""
    value_type = date if kind == "date" else datetime

    def app_ui(request: Request) -> Tag:
        return ui.page_fluid(
            ui.input_slider(
                "x",
                "X",
                value_type(2026, 1, 1),
                value_type(2026, 12, 31),
                (
                    (value_type(2026, 2, 1), value_type(2026, 3, 1))
                    if ranged
                    else value_type(2026, 2, 1)
                ),
            )
        )

    saved = ["invalid", "also-invalid"] if ranged else "invalid"
    app = App(app_ui, server=None, bookmark_store="url")
    with TestClient(app) as client:
        response = client.get("/?_inputs_&" + urlencode({"x": to_json_str(saved)}))
    assert response.status_code == 200
    attrs = SliderMarkup(response.text).inputs[0]
    assert attrs["data-from"] == "invalid"
    if ranged:
        assert attrs["data-to"] == "also-invalid"

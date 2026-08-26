"""Tests for `App(ui=PageDocument(...))` -- a complete, author-owned document."""

import pathlib

import pytest
from htmltools import HTMLDependency, HTMLDocument, HTMLTextDocument, TagList, tags
from starlette.requests import Request
from starlette.testclient import TestClient

from shiny import App
from shiny.ui import PageDocument

PLACEHOLDER = PageDocument.DEPS_PLACEHOLDER
HTML = f"<html><head>{PLACEHOLDER}</head><body>hello</body></html>"


def test_document_ui_gets_shiny_deps():
    app = App(PageDocument(HTML), None)

    assert not callable(app.ui)
    html = app.ui["html"]
    # Served as-is: no nested <html>, Shiny's deps at the placeholder.
    assert html.count("<html>") == 1
    assert PLACEHOLDER not in html
    assert "require.min.js" in html and "jquery" in html and "shiny.js" in html
    assert {"requirejs", "jquery", "shiny"} <= {d.name for d in app.ui["dependencies"]}


def test_document_ui_keeps_extra_deps_in_one_manifest():
    dep = HTMLDependency("my-dep", "1.0.0", script={"src": "my-dep.js"})
    app = App(PageDocument(HTML, extra_deps=[dep]), None)

    assert not callable(app.ui)
    html = app.ui["html"]
    # Two manifest tags would be concatenated without a separator by the client.
    assert html.count('type="application/html-dependencies"') == 1
    assert "my-dep[1.0.0]" in html and "shiny[" in html
    # Shiny's deps come first, so shiny.js is loaded before the author's script.
    assert html.index("shiny.js") < html.index("my-dep.js")
    # The extra dep got a route registered, not just markup.
    assert "my-dep" in {d.name for d in app.ui["dependencies"]}


def test_document_ui_custom_replace_pattern():
    app = App(
        PageDocument(
            "<html><head><!-- deps --></head><body></body></html>",
            deps_replace_pattern="<!-- deps -->",
        ),
        None,
    )

    assert not callable(app.ui)
    assert "shiny.js" in app.ui["html"]


def test_document_ui_without_placeholder_errors():
    doc = PageDocument("<html><head></head><body>hello</body></html>")
    with pytest.raises(ValueError, match="could not be inserted"):
        App(doc, None)


def test_plain_page_document_errors():
    with pytest.raises(TypeError, match="must be a `ui.PageDocument`"):
        App(HTMLTextDocument(HTML), None)  # pyright: ignore[reportArgumentType]


def test_path_ui_from_a_ui_function_errors(tmp_path: pathlib.Path):
    # A `Path` is read once at startup, so it is not a UI function return value.
    index = tmp_path / "index.html"
    index.write_text(HTML)

    def ui(request: Request) -> pathlib.Path:
        return index

    app = App(ui, None, bookmark_store="url")  # pyright: ignore[reportArgumentType]

    with pytest.raises(TypeError, match="cannot return a `Path`"):
        TestClient(app).get("/")


def test_html_document_errors():
    doc = HTMLDocument(tags.body("hello"))

    with pytest.raises(TypeError, match="cannot be used as a UI"):
        App(doc, None)  # pyright: ignore[reportArgumentType]


def test_html_document_from_a_ui_function_errors():
    def ui(request: Request) -> HTMLDocument:
        return HTMLDocument(tags.body("hello"))

    app = App(ui, None, bookmark_store="url")  # pyright: ignore[reportArgumentType]

    with pytest.raises(TypeError, match="cannot be used as a UI"):
        TestClient(app).get("/")


def test_page_deps_match_between_a_document_and_a_tag_tree():
    # The two page forms must carry the same dependencies, in the same order.
    app = App(TagList("hello"), None)
    assert not callable(app.ui)

    doc_deps = PageDocument(HTML).render()["dependencies"]
    tag_deps = app.ui["dependencies"]

    assert [d.name for d in doc_deps] == [d.name for d in tag_deps]


def test_document_ui_from_a_ui_function():
    # A UI function is what bookmarking requires, and it may return a document.
    def ui(request: Request) -> PageDocument:
        return PageDocument(HTML.replace("hello", request.url.path))

    app = App(ui, None, bookmark_store="url")

    assert callable(app.ui)
    client = TestClient(app)
    body = client.get("/").text
    assert body.count("<html>") == 1
    assert body.count('type="application/html-dependencies"') == 1
    assert "shiny.js" in body

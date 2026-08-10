from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType
from typing import Any, Callable

import pytest
from playwright.sync_api import Error as PlaywrightError

from shiny.playwright.controller import OutputDataFrame

PLAYWRIGHT_TESTS = Path(__file__).parents[1] / "playwright"


def _load_module(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_new_shared_page_does_not_repeat_initial_blank_navigation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    playwright_conftest = _load_module(
        "playwright_conftest_for_reliability_test", PLAYWRIGHT_TESTS / "conftest.py"
    )

    class NewPage:
        def goto(self, url: str) -> None:
            raise AssertionError(f"new page redundantly navigated to {url}")

        def set_viewport_size(self, size: dict[str, int]) -> None:
            assert size == {"width": 1920, "height": 1080}

    new_page = NewPage()

    def new_session_page(browser: object) -> NewPage:
        return new_page

    monkeypatch.setattr(playwright_conftest, "_new_session_page", new_session_page)

    page_fixture: Callable[..., Any] = playwright_conftest.page.__wrapped__
    assert page_fixture(object(), []) is new_page


def test_dataframe_scroll_reacquires_a_cell_detached_during_render() -> None:
    class Cell:
        def __init__(self, *, detached: bool = False) -> None:
            self.detached = detached
            self.scrolled = False

        def is_visible(self, *, timeout: float | None) -> bool:
            return True

        def scroll_into_view_if_needed(self, *, timeout: float | None) -> None:
            if self.detached:
                raise PlaywrightError("Element is not attached to the DOM")
            self.scrolled = True

    detached_cell = Cell(detached=True)
    replacement_cell = Cell()
    cells = iter([detached_cell, replacement_cell])
    dataframe = object.__new__(OutputDataFrame)
    dataframe.cell_locator = lambda row, col: next(cells)  # type: ignore[method-assign]

    dataframe._cell_scroll_if_needed(row=0, col=1, timeout=1000)

    assert replacement_cell.scrolled


def test_example_404_diagnostic_includes_failed_request_url(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    example_apps = _load_module(
        "example_apps_for_reliability_test",
        PLAYWRIGHT_TESTS / "examples" / "example_apps.py",
    )
    missing_url = "http://127.0.0.1:8000/static/app.js"

    class AppProcess:
        stderr = ""
        url = "http://127.0.0.1:8000"

        def __enter__(self) -> AppProcess:
            return self

        def __exit__(self, *args: object) -> None:
            return None

    class ConsoleMessage:
        type = "error"
        text = "Failed to load resource: the server responded with a status of 404"
        location = {"url": ""}

    class Response:
        status = 404
        url = missing_url

    class Page:
        def __init__(self) -> None:
            self.handlers: dict[str, Callable[[Any], None]] = {}

        def on(self, event: str, handler: Callable[[Any], None]) -> None:
            self.handlers[event] = handler

        def goto(self, url: str, *, wait_until: str) -> None:
            if "response" in self.handlers:
                self.handlers["response"](Response())
            self.handlers["console"](ConsoleMessage())

    def run_shiny_app(*args: object, **kwargs: object) -> AppProcess:
        return AppProcess()

    def wait_for_idle_app(*args: object, **kwargs: object) -> None:
        return None

    monkeypatch.setattr(example_apps, "run_shiny_app", run_shiny_app)
    monkeypatch.setattr(example_apps, "wait_for_idle_app", wait_for_idle_app)

    with pytest.raises(AssertionError, match=missing_url):
        example_apps.validate_example(
            Page(), "shiny/api-examples/todo_list/app-core.py"
        )


def test_example_retries_one_transient_http_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    example_apps = _load_module(
        "example_apps_for_transient_http_error_test",
        PLAYWRIGHT_TESTS / "examples" / "example_apps.py",
    )

    class AppProcess:
        stderr = ""
        url = "http://127.0.0.1:8000"

        def __enter__(self) -> AppProcess:
            return self

        def __exit__(self, *args: object) -> None:
            return None

    class ConsoleMessage:
        type = "error"
        text = "Failed to load resource: the server responded with a status of 404"
        location = {"url": ""}

    class Response:
        status = 404
        url = "http://127.0.0.1:8000/static/app.js"

    class Page:
        def __init__(self) -> None:
            self.handlers: dict[str, Callable[[Any], None]] = {}
            self.goto_count = 0

        def on(self, event: str, handler: Callable[[Any], None]) -> None:
            self.handlers[event] = handler

        def goto(self, url: str, *, wait_until: str) -> None:
            self.goto_count += 1
            if self.goto_count == 1:
                self.handlers["response"](Response())
                self.handlers["console"](ConsoleMessage())

        def locator(self, selector: str) -> object:
            return object()

    class Expectation:
        def to_have_count(self, count: int) -> None:
            assert count == 0

    page = Page()

    def run_shiny_app(*args: object, **kwargs: object) -> AppProcess:
        return AppProcess()

    def wait_for_idle_app(*args: object, **kwargs: object) -> None:
        return None

    def expect(locator: object) -> Expectation:
        return Expectation()

    monkeypatch.setattr(example_apps, "run_shiny_app", run_shiny_app)
    monkeypatch.setattr(example_apps, "wait_for_idle_app", wait_for_idle_app)
    monkeypatch.setattr(example_apps, "expect", expect)

    example_apps.validate_example(page, "shiny/api-examples/todo_list/app-core.py")

    assert page.goto_count == 2

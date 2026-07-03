"""Unit tests for the `AppTestValues` Playwright controller (no browser)."""

from __future__ import annotations

from typing import Any, cast
from unittest.mock import MagicMock

import pytest
from playwright.sync_api import Error as PlaywrightError

from shiny.playwright.controller import AppTestValues


def test_expect_values_rejects_invalid_match() -> None:
    # `match` validation happens before any page access, so a real Playwright
    # `Page` is not needed to exercise it.
    av = AppTestValues(cast(Any, None))

    with pytest.raises(ValueError, match="subset.*exact"):
        av.expect_inputs({"a": 1}, match=cast(Any, "nope"))
    with pytest.raises(ValueError):
        av.expect_outputs({"a": 1}, match=cast(Any, ""))
    with pytest.raises(ValueError):
        av.expect_exports({"a": 1}, match=cast(Any, "SUBSET"))


def _fake_page(*, ok: bool = True, json_error: bool = False) -> MagicMock:
    page = MagicMock()
    # `wait_for_function` returns a JSHandle whose `.json_value()` is the URL.
    page.wait_for_function.return_value.json_value.return_value = (
        "http://x/session/1/dataobj/shinytest?nonce=1"
    )
    response = MagicMock()
    response.ok = ok
    response.status = 200 if ok else 404
    if json_error:
        response.json.side_effect = ValueError("not json")
    else:
        response.json.return_value = {"input": {}, "output": {}, "export": {}}
    page.request.get.return_value = response
    return page


def test_get_raises_when_response_not_ok() -> None:
    # A non-OK response (e.g. 404 when test mode is off) raises a clear error.
    av = AppTestValues(_fake_page(ok=False))
    with pytest.raises(RuntimeError, match="test mode|SHINY_TESTMODE"):
        av.get()


def test_get_raises_on_non_json_body() -> None:
    # A 200 with a non-JSON body raises a clear error, not an opaque decode error.
    av = AppTestValues(_fake_page(ok=True, json_error=True))
    with pytest.raises(RuntimeError, match="non-JSON body"):
        av.get()


def test_get_raises_when_app_never_loads() -> None:
    # If the client API never appears, `wait_for_function` times out; we surface a
    # clear error (not a raw Playwright timeout) and make no HTTP request.
    page = MagicMock()
    page.wait_for_function.side_effect = PlaywrightError("Timeout 30000ms exceeded")
    av = AppTestValues(page)
    with pytest.raises(RuntimeError, match="Timed out waiting for the Shiny app"):
        av.get()
    page.request.get.assert_not_called()

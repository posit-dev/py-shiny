"""Unit tests for the `AppTestValues` Playwright controller (no browser)."""

from __future__ import annotations

from typing import Any, cast

import pytest

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

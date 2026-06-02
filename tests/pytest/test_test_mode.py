"""Tests for Shiny test mode (Phase A)."""

from __future__ import annotations

import pytest

from shiny._utils import is_test_mode


def test_is_test_mode_reads_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("SHINY_TESTMODE", raising=False)
    assert is_test_mode() is False

    monkeypatch.setenv("SHINY_TESTMODE", "1")
    assert is_test_mode() is True

    monkeypatch.setenv("SHINY_TESTMODE", "0")
    assert is_test_mode() is False

    monkeypatch.setenv("SHINY_TESTMODE", "true")
    assert is_test_mode() is False

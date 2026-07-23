"""Tests for env-var injection in the app-launch path."""

from __future__ import annotations

import os
from typing import cast
from unittest import mock

import pytest

from shiny.run import _run


def test_subprocess_env_none_returns_none() -> None:
    assert _run._subprocess_env(None) is None


def test_subprocess_env_merges_with_os_environ(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("EXISTING_VAR", "keep")
    merged = _run._subprocess_env({"SHINY_TESTMODE": "1"})
    assert merged is not None
    assert merged["SHINY_TESTMODE"] == "1"
    assert merged["EXISTING_VAR"] == "keep"  # inherits parent env


def test_run_shiny_app_passes_env_to_popen() -> None:
    captured: dict[str, object] = {}

    class _FakeProc:
        stdout: None = None
        stderr: None = None

        def wait(self) -> int:
            return 0

    def fake_popen(*args: object, **kwargs: object):
        captured.update(kwargs)
        return _FakeProc()

    with mock.patch.object(_run.subprocess, "Popen", fake_popen):
        with mock.patch.object(_run, "ShinyAppProc") as fake_app_proc:
            _run.run_shiny_app(
                "app.py", wait_for_start=False, env={"SHINY_TESTMODE": "1"}
            )

    assert fake_app_proc.called
    assert "env" in captured
    env_arg = captured["env"]
    assert isinstance(env_arg, dict)
    env_dict = cast("dict[str, str]", env_arg)
    assert env_dict["SHINY_TESTMODE"] == "1"
    assert env_dict.get("PATH") == os.environ.get("PATH")  # merged with parent env


def test_create_app_fixture_accepts_env_param() -> None:
    """create_app_fixture exposes an `env` override and returns a fixture."""
    import inspect

    from shiny.pytest import create_app_fixture

    sig = inspect.signature(create_app_fixture)
    assert "env" in sig.parameters

    # Returns a callable (a pytest fixture function) without launching anything.
    fixture = create_app_fixture("app.py")
    assert callable(fixture)

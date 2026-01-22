"""Tests for shiny.bookmark._serializers."""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import cast

import pytest

from shiny.bookmark._serializers import (
    Unserializable,
    can_serialize_input_file,
    is_unserializable,
    serializer_default,
    serializer_file_input,
    serializer_unserializable,
)
from shiny.session import Session


def test_is_unserializable() -> None:
    assert is_unserializable(Unserializable()) is True
    assert is_unserializable("x") is False


def test_serializer_unserializable() -> None:
    value = asyncio.run(serializer_unserializable())
    assert isinstance(value, Unserializable)


def test_serializer_default() -> None:
    assert asyncio.run(serializer_default(1, None)) == 1


def test_serializer_file_input_warns_when_no_state_dir() -> None:
    with pytest.warns(UserWarning):
        result = serializer_file_input(
            [{"datapath": "x", "name": "a", "size": 1, "type": "t"}], None
        )
    assert isinstance(result, Unserializable)


def test_serializer_file_input_type_errors(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="Expected list"):
        serializer_file_input("bad", tmp_path)  # type: ignore[arg-type]

    with pytest.raises(ValueError, match="Expected dict"):
        serializer_file_input(["bad"], tmp_path)  # type: ignore[list-item]

    with pytest.raises(ValueError, match="Missing 'datapath'"):
        serializer_file_input([{"name": "x"}], tmp_path)  # type: ignore[list-item]

    with pytest.raises(TypeError, match="Expected str"):
        serializer_file_input(
            [{"datapath": 1, "name": "x", "size": 1, "type": "t"}], tmp_path
        )


def test_serializer_file_input_copies_file(tmp_path: Path) -> None:
    source = tmp_path / "source.txt"
    source.write_text("data")

    state_dir = tmp_path / "state"
    state_dir.mkdir()

    value = [
        {"datapath": str(source), "name": "source.txt", "size": 4, "type": "text/plain"}
    ]

    result = serializer_file_input(value, state_dir)
    assert isinstance(result, list)
    assert result[0]["datapath"] == "source.txt"
    assert (state_dir / "source.txt").exists()


def test_can_serialize_input_file() -> None:
    class FakeBookmark:
        store = "server"

    class FakeSession:
        bookmark = FakeBookmark()

    assert can_serialize_input_file(cast(Session, FakeSession())) is True

    FakeBookmark.store = "url"
    assert can_serialize_input_file(cast(Session, FakeSession())) is False

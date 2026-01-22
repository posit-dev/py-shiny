"""Tests for shiny.bookmark save/restore helpers."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any, Awaitable

import pytest

from shiny.bookmark._global import (
    as_bookmark_dir_fn,
    get_bookmark_restore_dir_fn,
    get_bookmark_save_dir_fn,
    set_global_restore_dir_fn,
    set_global_save_dir_fn,
)
from shiny.bookmark._restore_state import RestoreContext, RestoreInputSet, RestoreState
from shiny.bookmark._save_state import BookmarkState
from shiny.types import MISSING_TYPE


def test_as_bookmark_dir_fn_wraps_sync() -> None:
    def sync_fn(bookmark_id: str) -> Path:
        return Path(f"/tmp/{bookmark_id}")

    async_fn = as_bookmark_dir_fn(sync_fn)
    assert async_fn is not None
    result = asyncio.run(async_fn("abc"))
    assert result == Path("/tmp/abc")


def test_global_save_restore_dir_fns(monkeypatch: pytest.MonkeyPatch) -> None:
    def save_fn(bookmark_id: str) -> Path:
        return Path(f"/save/{bookmark_id}")

    def restore_fn(bookmark_id: str) -> Path:
        return Path(f"/restore/{bookmark_id}")

    monkeypatch.setattr("shiny.bookmark._global._default_bookmark_save_dir_fn", None)
    monkeypatch.setattr("shiny.bookmark._global._default_bookmark_restore_dir_fn", None)

    set_global_save_dir_fn(save_fn)
    set_global_restore_dir_fn(restore_fn)

    save_dir = get_bookmark_save_dir_fn(MISSING_TYPE())
    restore_dir = get_bookmark_restore_dir_fn(MISSING_TYPE())
    assert save_dir is not None
    assert restore_dir is not None
    assert asyncio.run(save_dir("x")) == Path("/save/x")
    assert asyncio.run(restore_dir("y")) == Path("/restore/y")


def test_restore_state_namespace_scoping(tmp_path: Path) -> None:
    state = RestoreState(
        input={"ns-x": 1, "y": 2},
        values={"ns-z": 3, "q": 4},
        dir=tmp_path,
    )
    scoped = state._state_within_namespace("ns-")
    assert scoped.input == {"x": 1}
    assert scoped.values == {"z": 3}
    assert scoped.dir == tmp_path / "ns-"


def test_restore_input_set_lifecycle() -> None:
    rset = RestoreInputSet({"x": 1, "y": 2})
    assert rset.exists("x")
    assert rset.available("x")
    assert rset.get("x") == 1
    assert rset.is_pending("x")
    rset.flush_pending()
    assert rset.is_used("x")
    assert rset.get("x") is None
    assert rset.get("x", force=True) == 1


def test_restore_context_from_query_string_inputs_values() -> None:
    ctx = asyncio.run(
        RestoreContext.from_query_string("_inputs_&x=1&_values_&y=2", app=FakeApp())
    )
    assert ctx.active is True
    assert ctx.input.get("x", force=True) == 1
    assert ctx.values == {"y": 2}


def test_restore_context_load_state_qs(tmp_path: Path) -> None:
    state_dir = tmp_path / "state"
    state_dir.mkdir()
    (state_dir / "input.json").write_text(json.dumps({"x": 1}))
    (state_dir / "values.json").write_text(json.dumps({"y": 2}))

    async def restore_dir_fn(bookmark_id: str) -> Path:
        assert bookmark_id == "abc"
        return state_dir

    app = FakeApp()
    app._bookmark_restore_dir_fn = restore_dir_fn

    ctx = asyncio.run(RestoreContext.from_query_string("_state_id_=abc", app=app))
    assert ctx.active is True
    assert ctx.dir == state_dir
    assert ctx.input.get("x", force=True) == 1
    assert ctx.values == {"y": 2}


def test_bookmark_state_encode_and_save(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    inputs = FakeInputs({"x": 1})
    state = BookmarkState(inputs, exclude=[], on_save=None)
    state.values["y"] = 2

    monkeypatch.setattr("shiny.bookmark._save_state.private_random_id", lambda **_: "id")

    async def save_dir_fn(bookmark_id: str) -> Path:
        assert bookmark_id == "id"
        return tmp_path

    app = FakeApp()
    app._bookmark_save_dir_fn = save_dir_fn

    query_string = asyncio.run(state._save_state(app=app))
    assert query_string == "_state_id_=id"
    assert (tmp_path / "input.json").exists()
    assert (tmp_path / "values.json").exists()

    encoded = asyncio.run(state._encode_state())
    assert "_inputs_" in encoded
    assert "_values_" in encoded


class FakeApp:
    _bookmark_restore_dir_fn: Any = None
    _bookmark_save_dir_fn: Any = None


class FakeInputs:
    def __init__(self, values: dict[str, Any]):
        self._values = values

    async def _serialize(
        self, *, exclude: list[str], state_dir: Path | None
    ) -> dict[str, Any]:
        return {k: v for k, v in self._values.items() if k not in exclude}

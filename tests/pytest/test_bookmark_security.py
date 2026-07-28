"""Tests for bookmark id validation and restore gating (ab10e069).

Covers the `_state_id_` id allowlist, the rule that a restore only reads from
disk under `bookmark_store="server"`, and the file-input restore source checks.
"""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import cast

import pytest

from shiny import App
from shiny._utils import private_random_id
from shiny.bookmark._bookmark_state import (
    _local_dir,
    _max_bookmark_id_length,
    local_restore_dir,
    shiny_bookmarks_folder_name,
    validate_bookmark_id,
)
from shiny.bookmark._restore_state import RestoreContext
from shiny.input_handler import _restore_file_source


class _FakeApp:
    """Stand-in for ``shiny.App``; ``from_query_string`` reads only these two attrs.

    ``bookmark_store`` is typed ``str`` (not the ``Literal``) so tests can pass an
    unexpected value.
    """

    def __init__(
        self,
        bookmark_store: str = "server",
        restore_dir_fn: object = None,
    ) -> None:
        self.bookmark_store = bookmark_store
        self._bookmark_restore_dir_fn = restore_dir_fn


def _fake_app(bookmark_store: str = "server", restore_dir_fn: object = None) -> App:
    """A ``_FakeApp`` cast to ``App`` so call sites stay typed as ``App``."""
    return cast(App, _FakeApp(bookmark_store, restore_dir_fn))


@pytest.fixture
def app_workdir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Isolated cwd, not treated as a Shiny Server.

    The ``SHINY_PORT`` deletion is load-bearing: it routes ``_load_state_qs`` to
    ``local_restore_dir`` instead of raising ``NotImplementedError``.
    """
    workdir = tmp_path / "app"
    workdir.mkdir()
    monkeypatch.chdir(workdir)
    monkeypatch.delenv("SHINY_PORT", raising=False)
    return workdir


# Values the allowlist rejects because they are not a single safe path segment:
# some would resolve outside the store (via ``..`` or an absolute path), the rest
# contain characters an opaque bookmark token would never contain.
INVALID_IDS = [
    "..",
    "../other",
    "../../etc",
    "../../../../../../etc/other",
    "sub/../../outside",
    "/etc",
    "/tmp/elsewhere",
    "foo/bar",
    "foo\\bar",
    "with\x00nul",
    "",
    ".",
    "id.txt",  # a dot could combine into ".." across segments; disallowed
    "has space",
    "café",  # non-ASCII
    "a\nb",  # newline
    "abc\n",  # trailing newline (rejected by fullmatch, unlike `$`)
]

# IDs a well-behaved client/host could legitimately produce. All are single
# safe path segments (hex tokens, UUIDs with hyphens, underscore-delimited).
VALID_IDS = [
    "0b771f6dcb8c757d",
    "abc123DEF456",
    "550e8400-e29b-41d4-a716-446655440000",
    "my_saved_state_01",
    "A",
]


# ---------------------------------------------------------------------------
# id validation (allowlist)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("invalid_id", INVALID_IDS)
def test_validate_bookmark_id_rejects_invalid_ids(invalid_id: str) -> None:
    with pytest.raises(ValueError):
        validate_bookmark_id(invalid_id)


@pytest.mark.parametrize("invalid_id", INVALID_IDS)
def test_local_dir_rejects_invalid_ids(invalid_id: str) -> None:
    """``_local_dir`` must refuse ids that would resolve outside the ``shiny_bookmarks`` store."""
    with pytest.raises(ValueError):
        _local_dir(invalid_id)


@pytest.mark.parametrize("valid_id", VALID_IDS)
def test_validate_bookmark_id_accepts_valid_ids(valid_id: str) -> None:
    # A no-op (returns None) for valid ids; the assertion is that it does not raise.
    assert validate_bookmark_id(valid_id) is None


def test_validate_bookmark_id_accepts_server_generated_ids() -> None:
    """The opaque tokens that Shiny actually issues must still be accepted."""
    for _ in range(50):
        id = private_random_id(prefix="", bytes=8)
        validate_bookmark_id(id)  # must not raise


def test_validate_bookmark_id_rejects_overlong_id() -> None:
    validate_bookmark_id("a" * _max_bookmark_id_length)  # boundary: allowed
    with pytest.raises(ValueError):
        validate_bookmark_id("a" * (_max_bookmark_id_length + 1))


def test_local_dir_accepts_valid_id_stays_in_store(app_workdir: Path) -> None:
    id = "abc123def456"
    assert _local_dir(id) == app_workdir / shiny_bookmarks_folder_name / id


def test_local_dir_accepts_symlinked_per_id_dir(app_workdir: Path) -> None:
    """A symlinked per-id directory must not be rejected (no `.resolve()`)."""
    store = app_workdir / shiny_bookmarks_folder_name
    store.mkdir()
    outside = app_workdir.parent / "elsewhere" / "abc123"
    outside.mkdir(parents=True)
    (store / "abc123").symlink_to(outside)

    resolved = _local_dir("abc123")
    assert resolved == store / "abc123"
    assert resolved.exists()  # the symlink resolves to a real directory


@pytest.mark.asyncio
async def test_local_restore_dir_rejects_absolute_id(tmp_path: Path) -> None:
    with pytest.raises(ValueError):
        await local_restore_dir(str(tmp_path))


# ---------------------------------------------------------------------------
# end-to-end restore via `_state_id_` (server store)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_restore_context_ignores_absolute_id(app_workdir: Path) -> None:
    """A client-supplied absolute ``_state_id_`` must not read an outside dir."""
    outside = app_workdir.parent / "outside"
    outside.mkdir()
    (outside / "input.json").write_text(json.dumps({"other": "OUTSIDE_VALUE"}))

    ctx = await RestoreContext.from_query_string(
        f"_state_id_={outside}", app=_fake_app("server")
    )

    assert not ctx.active
    assert ctx.input.as_dict().get("other") != "OUTSIDE_VALUE"


@pytest.mark.asyncio
async def test_restore_context_ignores_relative_id(app_workdir: Path) -> None:
    """A relative ``_state_id_`` with ``..`` must not climb out of the store."""
    # The store must exist for the OS to resolve the ".." components.
    (app_workdir / shiny_bookmarks_folder_name).mkdir()

    outside = app_workdir.parent / "outside"
    outside.mkdir()
    (outside / "input.json").write_text(json.dumps({"other": "OUTSIDE_VALUE"}))

    rel = os.path.relpath(outside, app_workdir / shiny_bookmarks_folder_name)
    ctx = await RestoreContext.from_query_string(
        f"_state_id_={rel}", app=_fake_app("server")
    )

    assert not ctx.active
    assert ctx.input.as_dict().get("other") != "OUTSIDE_VALUE"


@pytest.mark.asyncio
async def test_restore_context_still_restores_valid_bookmark(app_workdir: Path) -> None:
    """A legitimate server-generated bookmark id must still restore normally."""
    id = private_random_id(prefix="", bytes=8)
    state_dir = app_workdir / shiny_bookmarks_folder_name / id
    state_dir.mkdir(parents=True)
    (state_dir / "input.json").write_text(json.dumps({"my_input": "hello"}))

    ctx = await RestoreContext.from_query_string(
        f"_state_id_={id}", app=_fake_app("server")
    )

    assert ctx.active
    assert ctx.input.as_dict().get("my_input") == "hello"


@pytest.mark.asyncio
async def test_source_validation_runs_before_custom_restore_dir_fn(
    app_workdir: Path,
) -> None:
    """An invalid ``_state_id_`` is rejected before a custom restore-dir fn runs.

    The built-in ``local_restore_dir`` re-validates, so the source check is only
    observable via a custom (e.g. host-registered) restore-dir function.
    """
    seen: list[str] = []

    async def custom_restore_dir(id: str) -> Path:
        seen.append(id)
        return app_workdir.parent / "outside"

    app = _fake_app("server", restore_dir_fn=custom_restore_dir)
    ctx = await RestoreContext.from_query_string("_state_id_=../../etc", app=app)

    assert not ctx.active
    assert seen == []  # the tainted id never reached the restore-dir function


# ---------------------------------------------------------------------------
# gating on `bookmark_store` (the unauthenticated-reachability half of the fix)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_disabled_store_ignores_state_id(app_workdir: Path) -> None:
    """With bookmarking disabled, a valid on-disk ``_state_id_`` is not restored."""
    id = private_random_id(prefix="", bytes=8)
    state_dir = app_workdir / shiny_bookmarks_folder_name / id
    state_dir.mkdir(parents=True)
    (state_dir / "input.json").write_text(json.dumps({"my_input": "hello"}))

    ctx = await RestoreContext.from_query_string(
        f"_state_id_={id}", app=_fake_app("disable")
    )

    assert not ctx.active
    assert ctx.input.as_dict() == {}


@pytest.mark.asyncio
async def test_disabled_store_ignores_encoded_state(app_workdir: Path) -> None:
    """With bookmarking disabled, URL-encoded state is not restored either."""
    ctx = await RestoreContext.from_query_string(
        "_inputs_&myinput=%22hello%22", app=_fake_app("disable")
    )

    assert not ctx.active
    assert ctx.input.as_dict() == {}


@pytest.mark.asyncio
async def test_url_store_ignores_state_id(app_workdir: Path) -> None:
    """A ``"url"`` app decodes the query string and never reads on-disk state."""
    id = private_random_id(prefix="", bytes=8)
    state_dir = app_workdir / shiny_bookmarks_folder_name / id
    state_dir.mkdir(parents=True)
    (state_dir / "input.json").write_text(json.dumps({"my_input": "hello"}))

    ctx = await RestoreContext.from_query_string(
        f"_state_id_={id}", app=_fake_app("url")
    )

    assert ctx.input.as_dict() == {}  # the on-disk state was not read


@pytest.mark.asyncio
async def test_url_store_restores_encoded_state(app_workdir: Path) -> None:
    """A ``"url"`` app still restores URL-encoded state (no regression)."""
    ctx = await RestoreContext.from_query_string(
        "_inputs_&myinput=%22hello%22", app=_fake_app("url")
    )

    assert ctx.active
    assert ctx.input.as_dict().get("myinput") == "hello"


@pytest.mark.parametrize(
    "store, query_string",
    [
        ("url", ""),
        ("url", "?"),
        ("url", "foo=bar"),
        # Under `"url"`, `_state_id_` is just an unrecognized decode key.
        ("url", "_state_id_=abc123"),
        ("server", ""),
        ("server", "?"),
        ("server", "foo=bar"),
        # `("server", "_state_id_=...")` is deliberately absent: that *is* a
        # request to load on-disk state, so becoming inactive when the directory
        # does not exist is correct. Covered by the restore tests above.
    ],
)
@pytest.mark.asyncio
async def test_restore_context_stays_active_when_bookmarking_enabled(
    store: str, query_string: str, app_workdir: Path
) -> None:
    """Any request must yield an *active* context once bookmarking is enabled.

    ``shinychat``'s ``ui.Chat.enable_bookmarking()`` destroys its own
    message-init effect and renders ``ui.Chat(messages=)`` from an ``on_restore``
    callback, which ``_bookmark.py`` only invokes for an active context. Marking
    any of these inactive stops chat apps rendering their initial messages -- a
    regression that only the chat end-to-end tests catch, so pin it here.
    """
    ctx = await RestoreContext.from_query_string(query_string, app=_fake_app(store))

    assert ctx.active
    # Nothing was actually restored, and no directory was resolved.
    assert ctx.input.as_dict() == {}
    assert ctx.dir is None


@pytest.mark.asyncio
async def test_unexpected_store_value_raises(app_workdir: Path) -> None:
    """An unexpected ``bookmark_store`` value fails loudly via the ``else`` branch."""
    ctx = await RestoreContext.from_query_string(
        "_inputs_&myinput=%22hello%22", app=_fake_app("bogus")
    )

    assert not ctx.active
    assert ctx._init_error_msg is not None


@pytest.mark.asyncio
async def test_failed_restore_logs_warning(
    app_workdir: Path, caplog: pytest.LogCaptureFixture
) -> None:
    """The failure detail is logged for the app author, not sent to the client.

    The client-facing notification is a generic message (see
    ``BookmarkApp._create_effects``); the reason belongs in the server log.
    """
    logger = "shiny.bookmark._restore_state"
    with caplog.at_level(logging.WARNING, logger=logger):
        ctx = await RestoreContext.from_query_string(
            "_state_id_=../../etc", app=_fake_app("server")
        )

    assert not ctx.active
    warnings_logged = [
        r.getMessage()
        for r in caplog.records
        if r.name == logger and r.levelno == logging.WARNING
    ]
    assert len(warnings_logged) == 1
    assert "Could not restore bookmarked state" in warnings_logged[0]
    # The detail the client never sees.
    assert "../../etc" in warnings_logged[0]


@pytest.mark.asyncio
async def test_unparsable_url_parameter_logs_warning(
    app_workdir: Path, caplog: pytest.LogCaptureFixture
) -> None:
    """A malformed encoded value is skipped and logged, without failing the restore.

    The bad value is client-supplied, so it is named but not echoed back.
    """
    logger = "shiny.bookmark._restore_state"
    with caplog.at_level(logging.WARNING, logger=logger):
        ctx = await RestoreContext.from_query_string(
            "_inputs_&good=%22hi%22&bad=notjson", app=_fake_app("url")
        )

    # The valid parameter still restores; only the bad one is dropped.
    assert ctx.active
    assert ctx.input.as_dict() == {"good": "hi"}

    warnings_logged = [
        r.getMessage()
        for r in caplog.records
        if r.name == logger and r.levelno == logging.WARNING
    ]
    assert len(warnings_logged) == 1
    assert '"bad"' in warnings_logged[0]
    assert "inputs" in warnings_logged[0]
    # The client-supplied value itself is not echoed into the log.
    assert "notjson" not in warnings_logged[0]


# ---------------------------------------------------------------------------
# file-input restore: refuse symlinked / non-regular sources
# ---------------------------------------------------------------------------


def test_restore_file_source_accepts_regular_file(tmp_path: Path) -> None:
    (tmp_path / "data.csv").write_text("a,b\n")
    assert _restore_file_source(tmp_path, "data.csv") == tmp_path / "data.csv"


def test_restore_file_source_refuses_symlink(tmp_path: Path) -> None:
    """A symlinked entry must be refused -- `shutil.copy2` would follow it."""
    outside = tmp_path.parent / "outside.txt"
    outside.write_text("SECRET")
    store = tmp_path / "state"
    store.mkdir()
    (store / "data.csv").symlink_to(outside)

    with pytest.raises(ValueError):
        _restore_file_source(store, "data.csv")


def test_restore_file_source_refuses_missing_and_dir(tmp_path: Path) -> None:
    (tmp_path / "subdir").mkdir()
    with pytest.raises(ValueError):
        _restore_file_source(tmp_path, "nope.csv")
    with pytest.raises(ValueError):
        _restore_file_source(tmp_path, "subdir")


def test_restore_file_source_allows_symlinked_store_dir(tmp_path: Path) -> None:
    """A symlinked *store* directory is still fine; only the file must be regular.

    Mirrors `test_local_dir_accepts_symlinked_per_id_dir`: deployments may back
    per-id bookmark directories with symlinked storage.
    """
    real = tmp_path / "real"
    real.mkdir()
    (real / "data.csv").write_text("a,b\n")
    link = tmp_path / "linked"
    link.symlink_to(real)

    assert _restore_file_source(link, "data.csv") == link / "data.csv"

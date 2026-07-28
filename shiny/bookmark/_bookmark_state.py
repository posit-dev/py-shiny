from __future__ import annotations

import os
import re
from pathlib import Path

shiny_bookmarks_folder_name = "shiny_bookmarks"

# Allowlist for the client-supplied `_state_id_`: a single path segment that
# can't express a separator, `..`, or an absolute path. (R uses `[a-zA-Z0-9]`;
# `-`/`_` are allowed here for UUID/token-style ids.) (ab10e069)
_valid_bookmark_id_re = re.compile(r"[A-Za-z0-9_-]+")

# Guards only against an attacker echoing a huge id back through error/log output.
_max_bookmark_id_length = 1024


def validate_bookmark_id(id: str) -> None:
    if len(id) > _max_bookmark_id_length or not _valid_bookmark_id_re.fullmatch(id):
        raise ValueError(f"Invalid bookmark id: {id!r}")


def _local_dir(id: str) -> Path:
    validate_bookmark_id(id)
    # `id` is a single safe path segment, so this join can't escape the store.
    # Not `.resolve()`d: that would follow a symlinked per-id dir out and break
    # stores backed by symlinked/persistent storage. (ab10e069)
    return Path(os.getcwd()) / shiny_bookmarks_folder_name / id


async def local_save_dir(id: str) -> Path:
    state_dir = _local_dir(id)
    state_dir.mkdir(parents=True, exist_ok=True)
    return state_dir


async def local_restore_dir(id: str) -> Path:
    return _local_dir(id)

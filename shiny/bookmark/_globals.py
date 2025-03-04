from __future__ import annotations

from pathlib import Path
from typing import Awaitable, Callable, Literal

from ..types import MISSING, MISSING_TYPE

# TODO: Barret: Q: Can we merge how bookmark dirs are saved / loaded?
BookmarkStateSaveDir = Callable[[str], Awaitable[Path]]
BookmarkStateLoadDir = Callable[[str], Awaitable[Path]]
bookmark_state_save_dir: BookmarkStateSaveDir | MISSING_TYPE = MISSING
bookmark_state_load_dir: BookmarkStateLoadDir | MISSING_TYPE = MISSING

BookmarkStore = Literal["url", "server", "disable"]
bookmark_store: BookmarkStore = "disable"


# def bookmark_store_get() -> BookmarkStore:
#     return bookmark_store


# def bookmark_store_set(value: BookmarkStore) -> None:
#     global bookmark_store
#     bookmark_store = value

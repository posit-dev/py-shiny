from __future__ import annotations

from pathlib import Path
from typing import Awaitable, Callable, Literal

from ..types import MISSING, MISSING_TYPE

# TODO: Barret: Q: Can we merge how bookmark dirs are saved / loaded?... it's the same directory! However, the save will return a possibly new path. Restoring will return an existing path.
BookmarkSaveDir = Callable[[str], Awaitable[Path]]
BookmarkLoadDir = Callable[[str], Awaitable[Path]]

bookmark_save_dir: BookmarkSaveDir | MISSING_TYPE = MISSING
bookmark_load_dir: BookmarkLoadDir | MISSING_TYPE = MISSING

BookmarkStore = Literal["url", "server", "disable"]
# TODO: Barret - Q: Should we have a `enable_bookmarking(store: BookmarkStore)` function?
bookmark_store: BookmarkStore = "disable"


# TODO: Barret; Q: I feel like there could be a `@shiny.globals.on_session_start` decorator that would allow us to set these values.

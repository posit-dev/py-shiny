from __future__ import annotations

from pathlib import Path
from typing import Awaitable, Callable, Literal

from ..types import MISSING, MISSING_TYPE

# TODO: Barret: Q: Can we merge how bookmark dirs are saved / loaded?... it's the same directory! However, the save will return a possibly new path. Restoring will return an existing path.
BookmarkStateSaveDir = Callable[[str], Awaitable[Path]]
BookmarkStateLoadDir = Callable[[str], Awaitable[Path]]
bookmark_state_save_dir: BookmarkStateSaveDir | MISSING_TYPE = MISSING
bookmark_state_load_dir: BookmarkStateLoadDir | MISSING_TYPE = MISSING

BookmarkStore = Literal["url", "server", "disable"]
# TODO: barret - Q: Should we have a `enable_bookmarking(store: BookmarkStore)` function?
bookmark_store: BookmarkStore = "disable"

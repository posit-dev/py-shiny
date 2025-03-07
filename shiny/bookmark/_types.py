from __future__ import annotations

from pathlib import Path
from typing import Awaitable, Callable, Literal

# Q: Can we merge how bookmark dirs are saved / loaded?... it's the same directory! However, the save will return a possibly new path. Restoring will return an existing path.
# A: No. Keep them separate. The save function may need to create a new directory, while the load function will always return an existing directory.
GetBookmarkSaveDir = Callable[[str], Awaitable[Path]]
GetBookmarkRestoreDir = Callable[[str], Awaitable[Path]]


BookmarkStore = Literal["url", "server", "disable"]

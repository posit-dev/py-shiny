from __future__ import annotations

from pathlib import Path
from typing import Awaitable, Callable, Literal, Union

# Q: Can we merge how bookmark dirs are saved / loaded?... it's the same directory! However, the save will return a possibly new path. Restoring will return an existing path.
# A: No. Keep them separate. The save function may need to create a new directory, while the load function will always return an existing directory.

BookmarkDirFn = Union[Callable[[str], Awaitable[Path]], Callable[[str], Path]]
BookmarkDirFnAsync = Callable[[str], Awaitable[Path]]

BookmarkSaveDirFn = BookmarkDirFnAsync
BookmarkRestoreDirFn = BookmarkDirFnAsync


BookmarkStore = Literal["url", "server", "disable"]

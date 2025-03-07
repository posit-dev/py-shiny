from __future__ import annotations

from pathlib import Path
from typing import Awaitable, Callable, Literal, TypeVar

from .._utils import wrap_async
from ..types import MISSING, MISSING_TYPE
from ._types import GetBookmarkRestoreDir, GetBookmarkSaveDir

BookmarkStore = Literal["url", "server", "disable"]


# WARNING! This file contains global state!
# During App initialization, the save_dir and restore_dir functions are conventionally set
# to read-only on the App.

# The set methods below are used to set the save_dir and restore_dir locations for locations like Connect or SSP.
# Ex:
# ```python
# @shiny.bookmark.set_save_dir
# def connect_save_shiny_bookmark(id: str) -> Path:
#     path = Path("connect") / id
#     path.mkdir(parents=True, exist_ok=True)
#     return path
# @shiny.bookmark.set_restore_dir
# def connect_restore_shiny_bookmark(id: str) -> Path:
#     return Path("connect") / id
# ```


_bookmark_save_dir: GetBookmarkSaveDir | MISSING_TYPE = MISSING
_bookmark_restore_dir: GetBookmarkRestoreDir | MISSING_TYPE = MISSING


GetBookmarkDirT = TypeVar(
    "GetBookmarkDirT",
    bound=Callable[[str], Awaitable[Path]] | Callable[[str], Awaitable[Path]],
)


def set_save_dir(fn: GetBookmarkDirT) -> GetBookmarkDirT:
    """TODO: Barret document"""
    global _bookmark_save_dir

    _bookmark_save_dir = wrap_async(fn)
    return fn


def set_restore_dir(fn: GetBookmarkDirT) -> GetBookmarkDirT:
    """TODO: Barret document"""
    global _bookmark_restore_dir

    _bookmark_restore_dir = wrap_async(fn)
    return fn

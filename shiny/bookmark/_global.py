from __future__ import annotations

from typing import overload

from .._utils import wrap_async
from ._types import (
    BookmarkDirFn,
    BookmarkDirFnAsync,
    BookmarkRestoreDirFn,
    BookmarkSaveDirFn,
)

# WARNING! This file contains global state!
# During App initialization, the save_dir and restore_dir functions are conventionally set
# to read-only on the App.


bookmark_save_dir: BookmarkSaveDirFn | None = None
bookmark_restore_dir: BookmarkRestoreDirFn | None = None


@overload
def as_bookmark_dir_fn(fn: BookmarkDirFn) -> BookmarkDirFnAsync:
    pass


@overload
def as_bookmark_dir_fn(fn: None) -> None:
    pass


def as_bookmark_dir_fn(fn: BookmarkDirFn | None) -> BookmarkDirFnAsync | None:
    if fn is None:
        return None
    return wrap_async(fn)


# TODO: Barret - Integrate Set / Restore for Connect. Ex: Connect https://github.com/posit-dev/connect/blob/8de330aec6a61cf21e160b5081d08a1d3d7e8129/R/connect.R#L915


def set_global_save_dir_fn(fn: BookmarkDirFn):
    """TODO: Barret document"""
    global bookmark_save_dir

    bookmark_save_dir = as_bookmark_dir_fn(fn)
    return fn


def set_global_restore_dir_fn(fn: BookmarkDirFn):
    """TODO: Barret document"""
    global bookmark_restore_dir

    bookmark_restore_dir = as_bookmark_dir_fn(fn)
    return fn

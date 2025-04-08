from __future__ import annotations

from typing import overload

from .._utils import wrap_async
from ..types import MISSING_TYPE
from ._types import (
    BookmarkDirFn,
    BookmarkDirFnAsync,
    BookmarkRestoreDirFn,
    BookmarkSaveDirFn,
)

# WARNING! This file contains global default values!


# During App initialization, the save_dir and restore_dir functions are conventionally set
# to read-only on the App.
# If nothing is set on the `app` object, the global default bookmark functions are found and used during every save/restore.
_default_bookmark_save_dir_fn: BookmarkSaveDirFn | None = None
_default_bookmark_restore_dir_fn: BookmarkRestoreDirFn | None = None


def get_bookmark_save_dir_fn(
    save_dir_fn: BookmarkSaveDirFn | None | MISSING_TYPE,
) -> BookmarkSaveDirFn | None:
    if isinstance(save_dir_fn, MISSING_TYPE):
        # Allow for default bookmark function to be utilized after app initialization.
        # Sometimes the app is created before hooks are registered.
        return _default_bookmark_save_dir_fn
    else:
        return save_dir_fn


def get_bookmark_restore_dir_fn(
    restore_dir_fn: BookmarkRestoreDirFn | None | MISSING_TYPE,
) -> BookmarkRestoreDirFn | None:
    if isinstance(restore_dir_fn, MISSING_TYPE):
        # Allow for default bookmark function to be utilized after app initialization.
        # Sometimes the app is created before hooks are registered.
        return _default_bookmark_restore_dir_fn
    else:
        return restore_dir_fn


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


def set_global_save_dir_fn(fn: BookmarkDirFn):
    """
    Set the global bookmark save directory function.

    This function is NOT intended to be used by app authors. Instead, it is a last resort option for hosted invironments to adjust how bookmarks are saved.

    Parameters
    ----------
    fn : BookmarkDirFn
        The function that will be used to determine the directory where bookmarks are saved. This function should create the directory (`pathlib.Path` object) that is returned.

    Examples
    --------
    ```python
    from pathlib import Path
    from shiny.bookmark import set_global_save_dir_fn, set_global_restore_dir_fn

    bookmark_dir = Path(__file__).parent / "bookmarks"

    def save_bookmark_dir(id: str) -> Path:
        save_dir = bookmark_dir / id
        save_dir.mkdir(parents=True, exist_ok=True)
        return save_dir

    def restore_bookmark_dir(id: str) -> Path:
        return bookmark_dir / id

    # Set global defaults for bookmark saving and restoring.
    set_global_restore_dir_fn(restore_bookmark_dir)
    set_global_save_dir_fn(save_bookmark_dir)

    app = App(app_ui, server, bookmark_store="server")
    ```


    See Also
    --------
    * `~shiny.bookmark.set_global_restore_dir_fn` : Set the global bookmark restore directory function
    """
    global _default_bookmark_save_dir_fn

    _default_bookmark_save_dir_fn = as_bookmark_dir_fn(fn)
    return fn


def set_global_restore_dir_fn(fn: BookmarkDirFn):
    """
    Set the global bookmark restore directory function.

    This function is NOT intended to be used by app authors. Instead, it is a last resort option for hosted invironments to adjust how bookmarks are restored.

    Parameters
    ----------
    fn : BookmarkDirFn
        The function that will be used to determine the directory (`pathlib.Path` object) where bookmarks are restored from.

    Examples
    --------
    ```python
    from pathlib import Path
    from shiny.bookmark import set_global_save_dir_fn, set_global_restore_dir_fn

    bookmark_dir = Path(__file__).parent / "bookmarks"

    def save_bookmark_dir(id: str) -> Path:
        save_dir = bookmark_dir / id
        save_dir.mkdir(parents=True, exist_ok=True)
        return save_dir

    def restore_bookmark_dir(id: str) -> Path:
        return bookmark_dir / id

    # Set global defaults for bookmark saving and restoring.
    set_global_restore_dir_fn(restore_bookmark_dir)
    set_global_save_dir_fn(save_bookmark_dir)

    app = App(app_ui, server, bookmark_store="server")
    ```

    See Also
    --------
    * `~shiny.bookmark.set_global_save_dir_fn` : Set the global bookmark save directory function.
    """
    global _default_bookmark_restore_dir_fn

    _default_bookmark_restore_dir_fn = as_bookmark_dir_fn(fn)
    return fn

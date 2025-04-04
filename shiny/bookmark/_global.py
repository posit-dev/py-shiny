from __future__ import annotations

import warnings
from typing import TYPE_CHECKING, overload

from starlette.applications import Starlette
from starlette.routing import BaseRoute, Mount

from .._utils import wrap_async
from ._types import (
    BookmarkDirFn,
    BookmarkDirFnAsync,
    BookmarkRestoreDirFn,
    BookmarkSaveDirFn,
)

if TYPE_CHECKING:
    from .._app import App

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
    global bookmark_save_dir

    bookmark_save_dir = as_bookmark_dir_fn(fn)
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
    global bookmark_restore_dir

    bookmark_restore_dir = as_bookmark_dir_fn(fn)
    return fn


def set_app_bookmark_callbacks(
    app: App | Starlette,
    *,
    get_bookmark_save_dir: BookmarkDirFn,
    get_bookmark_restore_dir: BookmarkDirFn,
) -> None:
    """
    Set the bookmark save and restore callbacks on the app.

    Parameters
    ----------
    app
        The app to set the callbacks on. This can be a `shiny.App` or a
        `starlette.applications.Starlette` app. If a `starlette.applications.Starlette`
        app, the callbacks will be set on all `shiny.App` instances mounted anywhere the
        app (through recursive route inspection).
    get_bookmark_save_dir
        The function to call to retrieve the bookmark save directory. This function should
        create the directory (`pathlib.Path` object) that is returned.
    get_bookmark_restore_dir
        The function to call to retrieve the bookmark restore directory. This function
        should create the directory (`pathlib.Path` object) that is returned.

    Returns
    -------
    None
        This function does not return anything. It modifies the app object in place.
    """

    from .. import App

    bookmark_save_dir_fn = as_bookmark_dir_fn(get_bookmark_save_dir)
    bookmark_restore_dir_fn = as_bookmark_dir_fn(get_bookmark_restore_dir)

    if isinstance(app, App):
        # print("Raw Shiny App: ", app)
        app._bookmark_save_dir_fn = bookmark_save_dir_fn
        app._bookmark_restore_dir_fn = bookmark_restore_dir_fn
    elif isinstance(app, Starlette):

        an_app_found: bool = False

        def inspect_starlette_routes(routes: list[BaseRoute]):
            for route in routes:
                if not isinstance(route, Mount):
                    continue

                if isinstance(route.app, App):
                    nonlocal an_app_found
                    an_app_found = True
                    # print("Shiny App: ", route.path)
                    route.app._bookmark_save_dir_fn = bookmark_save_dir_fn
                    route.app._bookmark_restore_dir_fn = bookmark_restore_dir_fn
                else:
                    # print("Inspecting Mount: ", route.path)
                    inspect_starlette_routes(route.routes)

        # print("Inspecting Starlette App: ", app)
        inspect_starlette_routes(app.router.routes)

        if not an_app_found:
            warnings.warn(
                "No Shiny app found in the Starlette app. Bookmarking will not be set.",
                UserWarning,
                stacklevel=1,
            )
    else:
        warnings.warn(
            "The app is not a Shiny app or a Starlette app. Bookmarking will not be set.",
            UserWarning,
            stacklevel=1,
        )

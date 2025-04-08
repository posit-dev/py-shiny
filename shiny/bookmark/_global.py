from __future__ import annotations

import warnings
from typing import TYPE_CHECKING, overload

from starlette.applications import Starlette
from starlette.routing import BaseRoute, Mount

from .._utils import wrap_async
from ._types import BookmarkDirFn, BookmarkDirFnAsync

if TYPE_CHECKING:
    from .._app import App

# WARNING! This file contains global state!
# During App initialization, the save_dir and restore_dir functions are conventionally set
# to read-only on the App.


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
        app.set_bookmark_save_dir_fn(bookmark_save_dir_fn)
        app.set_bookmark_restore_dir_fn(bookmark_restore_dir_fn)
    elif isinstance(app, Starlette):

        an_app_found: bool = False

        def inspect_starlette_routes(routes: list[BaseRoute]):
            for route in routes:
                if not isinstance(route, Mount):
                    continue

                if isinstance(route.app, App):
                    nonlocal an_app_found
                    an_app_found = True
                    route.app.set_bookmark_save_dir_fn(bookmark_save_dir_fn)
                    route.app.set_bookmark_restore_dir_fn(bookmark_restore_dir_fn)
                else:
                    # Recurse
                    inspect_starlette_routes(route.routes)

        inspect_starlette_routes(app.routes)

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

from __future__ import annotations

from pathlib import Path
from typing import Awaitable, Callable, Literal

# TODO: Barret: Q: Can we merge how bookmark dirs are saved / loaded?... it's the same directory! However, the save will return a possibly new path. Restoring will return an existing path.
# A: No. Keep them separate. The save function may need to create a new directory, while the load function will always return an existing directory.

# TODO: Barret Rename load -> restore. Keep the names consistent!
GetBookmarkSaveDir = Callable[[str], Awaitable[Path]]
GetBookmarkRestoreDir = Callable[[str], Awaitable[Path]]


BookmarkStore = Literal["url", "server", "disable"]


# TODO: Barret; Q: I feel like there could be a `@shiny.globals.on_session_start` decorator that would allow us to set these values.


# @shiny.session.on_session_start
# def _(session): ...


# @shiny.session.on_session_started
# def _(session): ...


# shiny.bookmark.globals.bookmark_save_dir = connect_custom_method
# shiny.bookmark.globals.bookmark_load_dir = connect_custom_method


# shiny.bookmark.set_bookmark_save_dir(connect_custom_method)
# shiny.bookmark.set_bookmark_load_dir(connect_custom_method)

# ------------

# import shiny

# # Garrick like's this one... fix the name!
# @shiny.bookmark.bookmark_save_dir
# def connect_custom_method(id: str) -> Path:
#     return Path("connect") / id


# shiny.run_app("some file")

# Using a decorator


# from shiny.bookmark import _globals as bookmark_globals
# bookmark_globals.bookmark_store = "url"

# bookmark.globals.bookmark_store = "url"

# import shiny

# TODO: Barret - Implement

# # Make placeholders start with underscore
# shiny.bookmark.globals.bookmark_save_dir = connect_save_shiny_bookmark
# shiny.bookmark.globals.bookmark_load_dir = connect_restore_shiny_bookmark

# # Implement this for now
# # Hold off on

# # Global level
# @shiny.bookmark.set_save_dir
# def connect_save_shiny_bookmark(): ...

# Don't implement this
# # App level
# @app.bookmark.set_save_dir
# def save_shiny_bookmark(): ...


# @app.bookmark.set_save_dir
# def save_shiny_bookmark(): ...


# @shiny.bookmark.set_restore_dir
# def connect_save_shiny_bookmark(): ...


# VV Don't use the next line style. It must be in the App() object!
# shiny.bookmark.globals.bookmark_store = "url"

# shiny.run_app("foo")

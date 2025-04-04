from pathlib import Path

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import PlainTextResponse
from starlette.routing import Mount, Route, WebSocketRoute
from starlette.staticfiles import StaticFiles
from starlette.websockets import WebSocket

import shiny
from shiny import App, ui
from shiny.bookmark._global import as_bookmark_dir_fn


def homepage(request: Request):
    return PlainTextResponse("Hello, world!")


def user_me(request: Request):
    username = "John Doe"
    return PlainTextResponse("Hello, %s!" % username)


def user(request: Request):
    username = request.path_params["username"]
    return PlainTextResponse("Hello, %s!" % username)


async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_text("Hello, websocket!")
    await websocket.close()


# shiny app ----
app_shiny = App(ui.page_fluid("hello from shiny!"), None)
sub_app_shiny = App(ui.page_fluid("hello from sub shiny!"), None)
sub_sub_app_shiny = App(ui.page_fluid("hello from sub sub shiny!"), None)


# combine apps ----
sub_sub_app = Starlette(
    routes=[
        Mount("/sub_sub_static", StaticFiles(directory=".")),
        Mount("/sub_sub_shiny", app=sub_sub_app_shiny),
    ]
)
sub_app = Starlette(
    routes=[
        Mount("/sub_sub", app=sub_sub_app),
        Mount("/sub_static", StaticFiles(directory=".")),
        Mount("/sub_shiny", app=sub_app_shiny),
    ]
)
routes = [
    Route("/", homepage),
    Route("/user/me", user_me),
    Route("/user/{username}", user),
    WebSocketRoute("/ws", websocket_endpoint),
    Mount("/static", StaticFiles(directory=".")),
    Mount("/shiny", app=app_shiny),
    Mount("/sub", sub_app),
]

app = Starlette(routes=routes)


def test_shiny_can_set_app_bookmarking_fns():

    app_fns = [
        app_shiny._bookmark_save_dir_fn,
        app_shiny._bookmark_restore_dir_fn,
    ]
    sub_app_fns = [
        sub_app_shiny._bookmark_save_dir_fn,
        sub_app_shiny._bookmark_restore_dir_fn,
    ]
    sub_sub_app_fns = [
        sub_sub_app_shiny._bookmark_save_dir_fn,
        sub_sub_app_shiny._bookmark_restore_dir_fn,
    ]

    assert app_fns == [None, None]
    assert sub_app_fns == [None, None]
    assert sub_sub_app_fns == [None, None]

    def save_dir(id: str) -> Path:
        # This function should really create the directory,
        # but for testing purposes, we just return the path without creating it.
        return Path("save_dir") / id

    def restore_dir(id: str) -> Path:
        return Path("restore_dir") / id

    internally_upgraded_fn_save = as_bookmark_dir_fn(save_dir)
    internally_upgraded_fn_restore = as_bookmark_dir_fn(restore_dir)

    shiny._set_app_bookmark_callbacks(
        app=app,
        get_bookmark_save_dir=internally_upgraded_fn_save,
        get_bookmark_restore_dir=internally_upgraded_fn_restore,
        # # Normally...
        # get_bookmark_save_dir=save_dir,
        # get_bookmark_restore_dir=restore_dir,
        # # ...but we want to test the upgrade to bookmark_dir_fn
        # # and not that the user function is always upgraded to async
    )

    assert app_shiny._bookmark_save_dir_fn == internally_upgraded_fn_save
    assert app_shiny._bookmark_restore_dir_fn == internally_upgraded_fn_restore

    assert sub_app_shiny._bookmark_save_dir_fn == internally_upgraded_fn_save
    assert sub_app_shiny._bookmark_restore_dir_fn == internally_upgraded_fn_restore

    assert sub_sub_app_shiny._bookmark_save_dir_fn == internally_upgraded_fn_save
    assert sub_sub_app_shiny._bookmark_restore_dir_fn == internally_upgraded_fn_restore

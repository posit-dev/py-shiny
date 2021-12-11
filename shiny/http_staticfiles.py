"""
We can't use starlette's StaticFiles when running in wasm mode, because it launches a
thread. Instead, use our own crappy version. Fortunately, this is all we need.

When running in native Python mode, use the starlette StaticFiles impl; it's battle
tested, whereas ours is not. Under wasm, it's OK if ours has bugs, even security holes:
everything is running in the browser sandbox including the filesystem, so there's
nothing we could disclose that an attacker wouldn't already have access to. The same is
not true when running in native Python, we want to be as safe as possible.
"""

import sys

if "pyodide" not in sys.modules:
    # Running in native mode; use starlette StaticFiles

    import starlette.staticfiles

    StaticFiles = starlette.staticfiles.StaticFiles  # type: ignore

else:
    # Running in wasm mode; must use our own simple StaticFiles

    from typing import Optional, Tuple
    from asgiref.typing import (
        ASGIReceiveCallable,
        ASGISendCallable,
        Scope,
    )
    import os
    import os.path
    import pathlib
    import urllib.parse

    from shiny.responses import Error404, FileResponse

    class StaticFiles:
        dir: pathlib.Path
        root_path: str

        def __init__(self, directory: str):
            self.dir = pathlib.Path(os.path.realpath(os.path.normpath(directory)))

        async def __call__(
            self, scope: Scope, receive: ASGIReceiveCallable, send: ASGISendCallable
        ):
            if scope["type"] != "http":
                raise AssertionError("StaticFiles can't handle non-http request")
            path = scope["path"]
            path_segments = path.split("/")
            final_path, trailing_slash = traverse_url_path(self.dir, path_segments)
            if final_path is None:
                return await Error404()(scope, receive, send)

            if not final_path.exists():
                return await Error404()(scope, receive, send)

            # Sanity check that final path is under self.dir, and if not, 404
            if not final_path.is_relative_to(self.dir):
                return await Error404()(scope, receive, send)

            # Serve up the path

            if final_path.is_dir():
                if trailing_slash:
                    # We could serve up index.html or directory listing if we wanted
                    return await Error404()(scope, receive, send)
                else:
                    # We could redirect with an added "/" if we wanted
                    return await Error404()(scope, receive, send)
            else:
                return await FileResponse(final_path)(scope, receive, send)

    def traverse_url_path(
        dir: pathlib.Path[str], path_segments: list[str]
    ) -> Tuple[Optional[pathlib.Path[str]], bool]:
        assert len(path_segments) > 0

        new_dir = dir
        path_segment = urllib.parse.unquote(path_segments.pop(0))
        # Gratuitous whitespace is not allowed
        if path_segment != path_segment.strip():
            return None, False

        # Check for illegal paths
        if "/" in path_segment:
            return None, False
        elif path_segment == ".." or path_segment == ".":
            return None, False

        if path_segment != "":
            new_dir = dir / path_segment

        if len(path_segments) == 0:
            return new_dir, path_segment == ""
        else:
            return traverse_url_path(new_dir, path_segments)

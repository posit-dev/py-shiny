import sys
from typing import Any, Iterable, Optional, Tuple

if sys.version_info >= (3, 8):
    from typing import Protocol
else:
    from typing_extensions import Protocol

if sys.version_info >= (3, 9):
    from collections.abc import MutableMapping
else:
    from typing import MutableMapping


from asgiref.typing import (
    ASGIReceiveCallable,
    ASGISendCallable,
    HTTPResponseBodyEvent,
    HTTPResponseStartEvent,
    Scope,
)
import json
import os
import mimetypes

# Reimplementations of response types in starlette; we need to reimplement them
# ourselves because starlette doesn't work with pyodide/wasm currently


class Response(Protocol):
    async def __call__(
        self, scope: Scope, receive: ASGIReceiveCallable, send: ASGISendCallable
    ) -> None:
        """Handle an HTTP request, ASGI3Application style"""


class BinaryResponse:
    charset: str = "utf-8"
    conetnt: Any
    status_code: int
    headers: Optional[MutableMapping[str, str]]
    media_type: Optional[str] = None

    def __init__(
        self,
        content: Any,
        status_code: int = 200,
        headers: Optional[MutableMapping[str, str]] = None,
        media_type: Optional[str] = None,
    ) -> None:
        self.content = content
        self.status_code = status_code
        self.headers = headers
        if media_type is not None:
            self.media_type = media_type

    async def __call__(
        self, scope: Scope, receive: ASGIReceiveCallable, send: ASGISendCallable
    ) -> None:
        await send(
            HTTPResponseStartEvent(
                type="http.response.start",
                status=self.status_code,
                headers=convert_headers(self.headers, self.media_type),
            )
        )
        await send(
            HTTPResponseBodyEvent(
                type="http.response.body",
                body=self.render(self.content),
                more_body=False,
            )
        )

    def render(self, content: Any) -> bytes:
        if content is None:
            return b""
        if isinstance(content, bytes):
            return content
        return content.encode(self.charset)


class TextResponse(BinaryResponse):
    media_type = "text/plain"


class HTMLResponse(TextResponse):
    media_type = "text/html; charset=utf-8"


class JSONResponse(BinaryResponse):
    media_type = "application/json"

    def render(self, content: Any) -> bytes:
        separators = None  # Make this (",", ":") for compact mode
        json_str = json.dumps(
            self.content, ensure_ascii=False, indent=2, separators=separators
        )
        return json_str.encode("utf-8")


class Error404(TextResponse):
    def __init__(
        self,
        content: str = "Not found",
        headers: Optional[MutableMapping[str, str]] = None,
        media_type: Optional[str] = "text/plain",
    ) -> None:
        super().__init__(content, 404, headers, media_type)


class FileResponse:
    file: os.PathLike[str]
    headers: Optional[MutableMapping[str, str]]
    media_type: str

    def __init__(
        self,
        file: os.PathLike[str],
        headers: Optional[MutableMapping[str, str]] = None,
        media_type: Optional[str] = None,
    ) -> None:
        self.headers = headers
        self.file = file

        if media_type is None:
            media_type, _ = mimetypes.guess_type(file, strict=False)
            if media_type is None:
                media_type = "application/octet-stream"
        self.media_type = media_type

    async def __call__(
        self, scope: Scope, receive: ASGIReceiveCallable, send: ASGISendCallable
    ) -> None:
        await send(
            HTTPResponseStartEvent(
                type="http.response.start",
                status=200,
                headers=convert_headers(self.headers, self.media_type),
            )
        )
        with open(self.file, "rb") as f:
            data = f.read()
            await send(
                HTTPResponseBodyEvent(
                    type="http.response.body", body=data, more_body=False
                )
            )


def convert_headers(
    headers: Optional[MutableMapping[str, str]], media_type: Optional[str] = None
) -> Iterable[Tuple[bytes, bytes]]:
    if headers is None:
        headers = {}

    header_list = [
        (k.encode("latin-1"), v.encode("latin-1")) for k, v in headers.items()
    ]
    if media_type is not None:
        header_list += [
            (
                b"Content-Type",
                media_type.encode("latin-1"),
            )
        ]
    return header_list

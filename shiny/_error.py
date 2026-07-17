from __future__ import annotations

import logging
from typing import cast

import starlette.exceptions as exceptions
import starlette.responses as responses
from starlette.types import ASGIApp, Receive, Scope, Send

logger = logging.getLogger(__name__)


class ErrorMiddleware:
    """Inserts shiny-autoreload.js into the head.

    It's necessary to do it using middleware instead of in a nice htmldependency,
    because we want autoreload to be effective even when displaying an error page.
    """

    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        try:
            return await self.app(scope, receive, send)
        except exceptions.HTTPException as e:
            resp = responses.PlainTextResponse(
                "An error occurred",
                e.status_code,
                headers=cast(
                    "dict[str, str]",
                    e.headers,  # pyright: ignore[reportUnknownMemberType]
                ),
                media_type="text/plain",
            )
            await resp(scope, receive, send)
        except Exception as e:
            logger.exception("Unhandled error: %s", e)
            resp = responses.PlainTextResponse(
                "An internal server error occurred", 500, media_type="text/plain"
            )
            await resp(scope, receive, send)

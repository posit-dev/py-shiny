"""Real recorded reactlogs for viewer tests: run a server in a mock session."""

from __future__ import annotations

import asyncio
import concurrent.futures
import json
from typing import Any, Callable

from shiny import App, Inputs, Outputs, Session, ui
from shiny._connection import MockConnection
from shiny.reactive._reactlog import load_reactlog_json


def record_export(
    server: Callable[[Inputs, Outputs, Session], None],
    steps: list[dict[str, Any]],
    *,
    app_ui: Any = None,
) -> dict[str, Any]:
    app = App(app_ui if app_ui is not None else ui.TagList(), server, reactlog=True)
    try:

        async def run() -> str:
            conn = MockConnection()
            sess = app._create_session(conn)
            conn.cause_receive(
                json.dumps({"method": "init", "data": steps[0] if steps else {}})
            )
            for update in steps[1:]:
                conn.cause_receive(json.dumps({"method": "update", "data": update}))
            conn.cause_disconnect()
            await sess._run()
            return sess.id

        # Own thread: Playwright's sync API may already own this thread's loop.
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
            session_id = pool.submit(asyncio.run, run()).result()
        export = app._reactlog_export(session_id, local=True)
        assert export is not None
        return export
    finally:
        app.reactlog_enabled = False


def record_log(
    server: Callable[[Inputs, Outputs, Session], None],
    steps: list[dict[str, Any]],
    *,
    app_ui: Any = None,
) -> dict[str, Any]:
    return load_reactlog_json(record_export(server, steps, app_ui=app_ui))

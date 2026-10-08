# Session lifecycle in Shiny for Python

## Overview

Every connected browser gets its own `Session` object. It is the natural home
for per-user state and cleanup: resources opened for one user must be released
when *that* user disconnects, not at process exit. Get the session as the
`server` function's third argument, or call
`require_active_session()` anywhere a reactive context is active.

In Core, do NOT store per-user state in a module-level global (it is shared
across every connected session). Express has a per-session `app.py` scope;
see [Express shared objects](express.md#shared-objects-and-startup-cost).
Do NOT rely on `atexit`/module teardown for per-user cleanup; use
`session.on_ended` instead.

```python
from shiny import App, Inputs, Outputs, Session, reactive, render, ui

def server(input: Inputs, output: Outputs, session: Session):
    ...
```

To reach the session from a helper called inside a reactive context, use
`require_active_session(None)` (it raises if no session is active).

## Clean up when a user disconnects: `session.on_ended`

Register a callback that runs after the client disconnects. Use it to close DB
connections, cancel background work, or delete temp files. The callback may be
sync or async; it returns a function that cancels the registration.

```python
def server(input, output, session):
    conn = open_db()

    @session.on_ended
    def _():
        conn.close()          # runs once, when this user's session ends
```

`on_ended` takes a single function; you can also call it directly:
`session.on_ended(conn.close)`.

`on_ended` fires when the whole session disconnects. To tear down just one
module instance's reactive graph (not the entire session), use
`session.destroy(id)` — see `references/modules-core.md`.

Closing a session is not the same as destroying a scope. On close, reactive
values and calcs stay readable at their last value (they are just reclaimed by
garbage collection), so async work that outlives the connection — an
`@reactive.extended_task` that settles after the user refreshes the page, a
stray `asyncio` task — can still touch them without erroring. Effects are
destroyed, so writes after close are inert. An explicit `session.destroy(id)`
on a live session does hard-destroy: reading a value from that scope afterwards
raises `DestroyedReactiveError`.

## Read the incoming request: `http_conn` and `clientdata`

`session.http_conn` is the Starlette
[`HTTPConnection`](https://www.starlette.io/requests/) for the WebSocket
handshake — read headers, cookies, and query params from it. It is a plain
attribute (not reactive), so it is safe to read anywhere in `server`.

```python
def server(input, output, session):
    token = session.http_conn.headers.get("authorization")
    theme = session.http_conn.cookies.get("theme", "light")
```

The browser's live URL is exposed reactively through `session.clientdata`
(read only inside a reactive context):

```python
@render.text
def where():
    cd = session.clientdata
    return f"{cd.url_protocol()}//{cd.url_hostname()}{cd.url_pathname()}{cd.url_search()}"
```

## Serve a per-session URL: `session.dynamic_route`

Register an ad-hoc HTTP endpoint scoped to this session and get back its URL
path. The handler takes a Starlette `Request` and returns a Starlette response.
Useful for serving a session-specific asset or value for another client to
`fetch`.

```python
from starlette.requests import Request
from starlette.responses import JSONResponse

def server(input, output, session):
    async def handler(request: Request) -> JSONResponse:
        return JSONResponse({"n": input.serve()})

    @reactive.effect
    @reactive.event(input.serve)
    def _():
        path = session.dynamic_route("my_handler", handler)   # register, get URL
        ui.insert_ui(ui.tags.script(f"fetch('{path}')..."), selector="body")
```

## Hook the reactive flush: `on_flush` / `on_flushed`

A flush is when Shiny recomputes invalidated reactives and sends the resulting
output updates to the client. `on_flush(fn)` runs *before* that send;
`on_flushed(fn)` runs *after*. Both default to `once=True` (fire on the next
flush only); pass `once=False` to run on every flush.

```python
def server(input, output, session):
    session.on_flushed(lambda: print("client updated"), once=False)
```

## Quick reference

| Need | Use |
|---|---|
| Get the session in `server` | third arg: `def server(input, output, session)` |
| Get the session elsewhere | `require_active_session(None)` |
| Run cleanup on disconnect | `@session.on_ended` |
| Request headers / cookies | `session.http_conn.headers` / `.cookies` |
| Live browser URL (reactive) | `session.clientdata.url_*()` |
| Per-session HTTP endpoint | `path = session.dynamic_route(name, handler)` |
| Run before flush is sent | `session.on_flush(fn, once=False)` |
| Run after flush is sent | `session.on_flushed(fn, once=False)` |
| Close the session | `await session.close()` |

## Common mistakes

- Per-user state in a module-level global -> shared across all sessions; create
  it inside Core `server()` or Express `app.py` so each session gets its own.
  Wrapping a global in `reactive.value` does not make it per-session.
- Cleanup in `atexit`/module teardown -> fires once at shutdown, not per user;
  register it with `session.on_ended`.
- Reading `session.clientdata.url_*()` at module scope or in a plain helper ->
  "no current reactive context" error; read inside a `@render.*`, `calc`, or
  `effect`. `session.http_conn` is not reactive and can be read anywhere.
- `await`ing `session.close()` without `async` -> `close` is a coroutine; call
  it from an async `@reactive.effect`.
- Passing a coroutine function to `on_ended`/`on_flush` -> fine, they accept
  sync *or* async callbacks; just don't call the function yourself.

### Keep user state per session

Create authentication state, preferences, and user-specific database resources
in the session's scope. This Core example gives each user their own value:

```python
from shiny import reactive, render

# Bad: user_state = reactive.value({"logged_in": False}) at module scope.

def server(input, output, session):
    user_state = reactive.value({"logged_in": False})

    @render.text
    def status():
        return f"Logged in: {user_state()['logged_in']}"
```

Global reactive values are valid for intentional shared counters or broadcast
state. Shared `reactive.file_reader()` caches are also appropriate for data
every user may read; see [Reactivity](reactivity.md#timers-and-streaming-invalidate_later-poll-file_reader).
Keep user-specific state out of those caches and server credentials out of
rendered UI.

## Related references

- Module namespaces (`session.make_scope`, `session.destroy(id)`,
  `session.on_destroy`) -> `references/modules-core.md`.
- Sending custom JS messages (`session.send_custom_message`) -> `references/custom-components.md`.
  This reference owns `session.send_input_message` (the low-level primitive behind
  `ui.update_*`; prefer the `ui.update_*` wrappers).
- Saving/restoring session state across reconnects -> `references/bookmarking.md`.

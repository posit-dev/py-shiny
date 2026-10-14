---
title: "Session Messaging"
description: "The server<->browser session protocol and lifecycle: connection setup, the AppSession message loop, file uploads and makeRequest calls, output flushing, busy/progress/recalculating messages, error sanitization, custom/input/dynamic-UI messages, and session teardown. Read before changing shiny/session/_session.py, shiny/_connection.py, or anything that sends messages to the client."
---

# Session Messaging

How a browser tab talks to its `AppSession`. For the class layout (`Session`
ABC, `AppSession`, `SessionProxy`, `Inputs`/`Outputs`) see the "Session
Hierarchy" section of `memory-bank/architecture.md`; this doc covers the wire
protocol and the order things happen in.

The client is R Shiny's `shiny.js`, vendored into `shiny/www/shared/shiny.js`
(see `memory-bank/assets.md`). The server speaks *that* protocol, so message
shapes are fixed by R Shiny. py-shiny's own TypeScript in `js/` (e.g.
`js/data-frame/request.ts`, which wraps `Shiny.shinyapp.makeRequest`) only
*uses* the protocol; it doesn't define it.

## Connection setup

- `shiny/_app.py` `App.init_starlette_app` mounts:
  - `WebSocketRoute("/websocket/")` -> `App._on_connect_cb`
  - `Route("/session/{session_id}/{action}/{subpath:path}")` (GET/POST) ->
    `App._on_session_request_cb` (uploads, downloads, dynamic routes, test snapshots)
- `_on_connect_cb` accepts the socket, wraps it in
  `shiny/_connection.py` `StarletteConnection`, calls `App._create_session`
  (id = `secrets.token_hex(32)`, stored in `App._sessions`), then awaits
  `AppSession._run()` for the life of the socket.
- `Connection` is the transport ABC (`send`/`receive`/`close`/`get_http_conn`).
  `StarletteConnection.send` never raises: on failure it closes with code 1008
  and returns. `receive` turns `WebSocketDisconnect` into `ConnectionClosed`.
  `MockConnection` (used by `tests/pytest/test_shinysession.py`,
  `shiny/testserver/_test_server.py`, etc.) feeds messages via
  `cause_receive()`; `cause_disconnect()` sends `""`, which raises `ConnectionClosed`.
- `AppSession.__init__` reads the `shiny-server-credentials` header (falling back
  to `rstudio-connect-credentials`) for `session.user`/`session.groups`.

## The message loop (`AppSession._run_impl`)

1. Server sends `{"config": {"workerId": "", "sessionId": id, "user": None}}`.
2. Loop: `await self._conn.receive()`, then `json.loads(..., object_hook=_utils.lists_to_tuples)`.
   Bad JSON or a missing `"method"` ends the session (warn/print and `return`).
3. Each message is handled while holding the global `reactive.lock()`, keyed on `method`:

| Client message | Required state | Handling |
|---|---|---|
| `{"method": "init", "data": {...}}` | `Start` | Sets bookmark `RestoreContext` from `.clientdata_url_search`; registers `self._flush` with `reactive._core.on_flushed`; `bookmark._create_effects()`; state -> `Running`; `_manage_inputs(data)`; runs `app.server(input, output, session)` in `session_context` + the `session_start` OTel span; then `reactive_flush()` |
| `{"method": "update", "data": {...}}` | `Running` | `_manage_inputs(data)` |
| `{"method": name, "tag": n, "args": [...]}` | `Running` | `AppSession._dispatch` (see below) |
| anything else | - | `ProtocolError` (the session gets closed) |

4. After every message: `await asyncio.sleep(0)` (lets queued sync sends like
   progress messages drain, issue #1381), then `_request_flush()` and
   `reactive_flush()` inside `session_context(self)`.

`ConnectionState` (`Start`/`Running`/`Closed`) is enforced by `verify_state`; a
wrong-state message raises `ProtocolError`.

### Inputs (`AppSession._manage_inputs`)

- Keys may be `"id:type"`. The `type` part is passed through
  `shiny/input_handler.py` `input_handlers._process_value` (register with
  `input_handlers.add(type)`). More than one `:` raises `ValueError`.
- Every value is set with `Value._set(val, force=True)`: a value the client
  resends (e.g. `{priority: "event"}`) always invalidates dependents, matching
  R's `dedupe=FALSE`.
- Ends with `self.output._manage_hidden()`, which suspends/resumes output
  effects based on `.clientdata_output_<id>_hidden`. An output whose hidden flag
  hasn't been received yet counts as hidden (`AppSession._is_hidden`).

### Request/response calls (`makeRequest` <-> `set_message_handler`)

- JS `Shiny.shinyapp.makeRequest(method, args, ...)` sends `{method, tag, args}`.
- `AppSession._dispatch` looks up `_message_handlers[method]` and runs the
  handler under the `session_context` it was registered from (`_handler_session`)
  and `isolate()`. The reply is `{"response": {"tag": n, "value": ...}}`, or
  `{"response": {"tag": n, "error": msg}}` for an unknown method or an exception.
- `SessionProxy.set_message_handler` namespaces `name` with `self.ns(name)` and
  returns the key. JS must call that namespaced key (see `render.data_frame`).
  Passing `handler=None` removes the handler.

### File uploads

Built-in handlers are registered in `AppSession._init_message_handlers`:

1. `uploadInit(file_infos)` (makeRequest): fills in a missing MIME type and
   creates a `FileUploadManager` operation. It returns
   `{"jobId", "uploadUrl": "session/{id}/upload/{job_id}?w="}`.
2. Browser POSTs each file's bytes to that URL ->
   `AppSession._handle_request_impl` (`action == "upload"`) streams the chunks
   into the operation (one POST per file; `with upload_op` opens the next file).
3. `uploadEnd(job_id, input_id)`: `upload_op.finish()`, sets the input to the
   file-info list, and registers the file serializer and snapshot preprocessor.
- Upload temp dirs are removed by an `on_ended` hook
  (`_register_session_ended_callbacks`).

### HTTP side channel

`_on_session_request_cb` runs `AppSession._handle_request` inside
`session_context(session)`. It increments/decrements the busy count around the
request and handles `upload` (POST), `download` (GET, see
`render.download_button`), `dynamic_route` (GET, from
`session.dynamic_route()`), and `dataobj/shinytest` (test mode only). Unknown
session ids get a 404.

## Server -> client messages

All of them go through `AppSession._send_message` (async, `json.dumps`, logs
`SEND:` when `debug=True`) or `_send_message_sync`. The sync version uses
`_utils.run_coro_hybrid`, which runs the send right away up to its first await
instead of scheduling a task. `SessionProxy` forwards everything to the root;
only `send_input_message` (`ns(id)`), `set_message_handler`, and `dynamic_route`
add a namespace.

| Top-level key | Sent by | When |
|---|---|---|
| `values`, `errors`, `inputMessages` | `AppSession._flush` | Batched, once per reactive flush |
| `recalculating` `{name, status}` | `Outputs.__call__` `output_obs` | Immediately, before (`recalculating`) and after (`recalculated`) each render |
| `progress` `{type: "binding"\|"open"\|"update"\|"close"}` | `_send_progress`; `output_obs.on_invalidate`; `shiny/ui/_progress.py` | Immediately (sync) |
| `busy` `"busy"`/`"idle"` | `_increment_busy_count`/`_decrement_busy_count` | When the count goes 0->1 / 1->0 |
| `custom` `{type: msg}` | `send_custom_message`; bslib toasts/offcanvas/dark mode call `_send_message_sync({"custom": ...})` | Immediately |
| `shiny-insert-ui` / `shiny-remove-ui` | `ui.insert_ui`/`ui.remove_ui` -> `_send_insert_ui`/`_send_remove_ui` | `on_flushed` by default; immediately when `immediate=True` |
| `shiny-insert-tab` / `shiny-remove-tab` / `shiny-change-tab-visibility` | `shiny/ui/_navs_dynamic.py` | Immediately |
| `modal`, `notification` | `shiny/ui/_modal.py`, `shiny/ui/_notification.py` | Immediately |
| `allowReconnect` | `Session.allow_reconnect` | Immediately |
| `response` | `_dispatch` | Reply to a makeRequest |

- `send_input_message(id, msg)` does **not** send right away. It queues into
  `OutBoundMessageQueues.input_messages` and goes out in the next `_flush`
  (the client routes it to the input binding's `receiveMessage`).
- Dynamic UI content comes from `AppSession._process_ui`. It renders the
  `TagList`, registers each `HTMLDependency` with the app
  (`App._register_web_dependency`) so its files get served, and sends
  `{"deps": [...], "html": ...}`.

## The flush cycle

`reactive.flush()` (`ReactiveEnvironment.flush`) runs all pending effects in
priority order, then calls its `on_flushed` callbacks. Each running session
registered `AppSession._flush` there during `init`. `_flush` then:

1. Within `session_context`: `bookmark._restore_context.flush_pending()`, then
   `session.on_flush` callbacks.
2. Sends one `{"values", "inputMessages", "errors"}` message, then
   `OutBoundMessageQueues.reset()` (inside a `finally`, so the queues get cleared
   even if the send fails).
3. `session.on_flushed` callbacks (in a `finally`). Deferred `insert_ui`/`remove_ui` run here.

Output lifecycle (`Outputs.__call__` -> `output_obs`, an `Effect_`):

- On invalidation, the effect sends `progress {type: "binding", id}` and the
  effect's session increments the busy count (`Effect_._create_context`). The
  count is decremented after the effect runs. So `busy` is sent when the first
  effect is invalidated and `idle` once the last pending one has run.
- On run, it sends `recalculating` and calls `renderer.render()`. The result
  goes into `set_value` / `set_error` / `set_silent`, and it finally sends
  `recalculated`.
- `OutBoundMessageQueues` is a dict keyed by output id, so only the last
  value/error per output per flush is sent. `set_value` and `set_error` clear
  each other's entry. The `test_*` fields keep a persistent copy only in
  `SHINY_TESTMODE`.

## Errors

- **Outputs**: `SilentException` (e.g. `req()`) -> `set_silent` (blank output).
  `SilentCancelOutputException` -> keeps the existing output.
  `SilentOperationInProgressException` -> sends a persistent `binding` progress
  message and returns *without* `recalculated`. Any other exception is printed
  to the console and becomes `errors[id] = {"message", "call": None, "type": None}`.
- **Sanitizing**: if `session.app.sanitize_errors` is set (the instance attribute
  defaults to module-level `shiny/_app.py` `SANITIZE_ERRORS`, `False`), messages
  are replaced with `app.sanitize_error_msg` unless the exception is a
  `shiny.types.SafeException`. Both `output_obs` and `_dispatch` apply this.
  Tracebacks never go to the client; in test mode they're kept only in
  `OutBoundMessageQueues.test_tracebacks`.
- **Effects** (`Effect_._run`): `SilentException` is swallowed. `NotifyException`
  shows an error notification and closes the session only if `e.close`. Any
  other exception calls `session._unhandled_error(e)`, which prints and **closes
  the session**.
- **Message loop**: an exception that escapes the loop prints the traceback and
  closes the session.

## Session end and cleanup

- Triggered by `ConnectionClosed` (client left), a loop exception,
  `session.close()`, `_unhandled_error`, or `App.stop()` (closes every session).
- `AppSession._run_session_ended_tasks` (idempotent, guarded by
  `_has_run_session_ended_tasks`) does the following:
  1. Sets the flag first, so `_is_closed()` is already true during teardown.
  2. `on_ended` callbacks.
  3. `destroy()`: root-scope destroy callbacks. Reactive values and calcs stay
     readable on this path.
  4. `App._remove_session` (in a `finally`).
- After that the `ExitStack` in `_run_impl` unregisters `_flush` from the global
  `on_flushed`.
- Module-scope teardown (`SessionProxy.destroy`) also deletes the module's
  namespaced `_message_handlers`, `_dynamic_routes`, and `_downloads` from the root.

## Where to hook in

- New client->server RPC: `session.set_message_handler(name, fn)` plus JS
  `makeRequest`. Don't add a new `method` branch to `_run_impl`.
- New server->client message: prefer `send_custom_message` with a namespaced
  type (`"bslib.*"`, etc.) and a JS `addCustomMessageHandler`. A new top-level
  key only works if vendored `shiny.js` already understands it.
- Updating an input widget: `session.send_input_message` (batched with outputs).
- Work that has to happen around the outbound batch: `session.on_flush` /
  `session.on_flushed`.
- Every new `_send_*` on `Session` needs matching implementations in
  `SessionProxy` and `shiny/express/_stub_session.py` `ExpressStubSession`.

## Pitfalls

- **Ordering between immediate and batched messages.** `recalculating`,
  `progress`, `custom`, modal/notification, and `immediate=True` insert/remove
  go out right away. Values, errors, and input messages wait until the end of
  the flush. A custom message sent from inside a render can reach the browser
  before the output value it relates to. Use `on_flushed` if it has to come after.
- **`on_flush` fires after effects run, not before.** The docstring says
  "before the next reactive flush", but it's called from `_flush`, which runs in
  the reactive environment's `on_flushed` phase. It is "before the outbound
  batch is sent", not "before effects run".
- **Every flush is broadcast to every session.** There is one global
  `ReactiveEnvironment`, and `App._request_flush` is a no-op TODO. Each session's
  `_flush` runs on every flush from any session, and sends a (possibly empty)
  `values` message each time.
- **One global lock.** `reactive.lock()` serializes message handling across all
  sessions. Code that modifies the reactive graph from another task must hold
  it (see `ExtendedTask`).
- **JSON lists arrive as tuples.** `lists_to_tuples` converts nested lists, so
  input values and makeRequest `args` are tuples. Compare with tuples, not lists.
- **Exceptions close the session.** An error in an `Effect`, or anything that
  escapes `_run_impl`, closes the socket. Only output render errors are shown
  in place.
- **`NotifyException` with `sanitize=True`** uses the module constant
  `SANITIZE_ERROR_MSG`, not `app.sanitize_error_msg`.
- **Hidden-by-default outputs.** An output only renders after the client
  reports `.clientdata_output_<id>_hidden = False`. Server-only tests with
  `MockConnection` have to send that input, or pass `suspend_when_hidden=False`.
- **`_send_message_sync` doesn't guarantee completion.** It returns a future;
  large messages or backpressure finish later, and errors end up in the
  ignored future, not raised at the call site.
- **Session id is a bearer token.** `/session/{id}/...` routes trust the id
  alone, so never log it or expose it beyond what the protocol already sends.

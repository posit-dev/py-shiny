---
title: "Session Messaging"
description: "The server<->browser session protocol and lifecycle: connection setup, the AppSession message loop, file uploads and makeRequest calls, per-session cycles and the output flush, busy/progress/recalculating messages, error sanitization, custom/input/dynamic-UI messages, and session teardown. Read before changing shiny/session/_session.py, shiny/_connection.py, or anything that sends messages to the client."
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
3. Each message is handled by `method`. The loop never awaits a round or an
   effect, so a busy session keeps receiving:

| Client message | Required state | Handling |
|---|---|---|
| `{"method": "init", "data": {...}}` | `Start` | Sets bookmark `RestoreContext` from `.clientdata_url_search`; sets `_output_flush_enabled` (the `ExitStack` undoes it and cancels dispatch tasks on exit); state -> `Running`; `_manage_inputs(data)` directly; inside `session_context` + the `session_start` OTel span: `bookmark._create_effects()`, `app.server(input, output, session)`, `_request_output_flush()`, then `await _reactive_environment.start_round()` (starts the first effects without waiting for their async parts) |
| `{"method": "update", "data": {...}}` | `Running` | `run_once_when_idle(partial(_manage_inputs, data))`: applied at the start of the next cycle, never mid-cycle |
| `{"method": name, "tag": n, "args": [...]}` | `Running` | `AppSession._dispatch` in its own task (`_dispatch_tasks`; see below) |
| anything else | - | `ProtocolError` (the session gets closed) |

4. After every message: `_request_output_flush()`, which sends anything queued
   (and runs a queued cycle start action) after the next round, once the
   session is idle.

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
- `AppSession._dispatch` (run as a task, so slow handlers don't block the
  loop, and not awaited by `reactive.flush()`) looks up `_message_handlers[method]` and runs the
  handler under the `session_context` it was registered from (`_handler_session`)
  and `isolate()`. The reply is `{"response": {"tag": n, "value": ...}}`, or
  `{"response": {"tag": n, "error": msg}}` for an unknown method or an exception.
  An exception escaping the task (e.g. the reply can't be sent) closes the
  session (`_on_dispatch_done`).
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
   file-info list **right away** (not via a cycle start action, matching R's
   `@uploadEnd`; a running effect can see it change), and registers the file
   serializer and snapshot preprocessor.
- Upload temp dirs are removed by an `on_ended` hook
  (`_register_session_ended_callbacks`).

### HTTP side channel

`_on_session_request_cb` runs `AppSession._handle_request` inside
`session_context(session)`. Only `download` increments/decrements the busy
count (as in R), and only around the handler call: a streamed body is read
afterwards with the session idle. It handles `upload` (POST), `download` (GET, see
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
| `values`, `errors`, `inputMessages` | `AppSession._send_queued_outputs` | Batched, once per cycle (see below) |
| `recalculating` `{name, status}` | `Outputs.__call__` `output_obs` | Immediately, before (`recalculating`, followed by one `asyncio.sleep(0)`) and after (`recalculated`) each render |
| `progress` `{type: "binding"\|"open"\|"update"\|"close"}` | `_send_progress`; `output_obs.on_invalidate`; `shiny/ui/_progress.py` | Immediately (sync) |
| `busy` `"busy"`/`"idle"` | `_increment_busy_count`/`_decrement_busy_count` | When the per-session count goes 0->1 / 1->0 (a cycle's start/end) |
| `custom` `{type: msg}` | `send_custom_message`; bslib toasts/offcanvas/dark mode call `_send_message_sync({"custom": ...})` | Immediately |
| `shiny-insert-ui` / `shiny-remove-ui` | `ui.insert_ui`/`ui.remove_ui` -> `_send_insert_ui`/`_send_remove_ui` | `on_flushed` by default; immediately when `immediate=True` |
| `shiny-insert-tab` / `shiny-remove-tab` / `shiny-change-tab-visibility` | `shiny/ui/_navs_dynamic.py` | Immediately |
| `modal`, `notification` | `shiny/ui/_modal.py`, `shiny/ui/_notification.py` | Immediately |
| `allowReconnect` | `Session.allow_reconnect` | Immediately |
| `response` | `_dispatch` | Reply to a makeRequest |

- `send_input_message(id, msg)` does **not** send right away. It queues into
  `OutBoundMessageQueues.input_messages` and goes out in the next output flush
  (the client routes it to the input binding's `receiveMessage`).
- Dynamic UI content comes from `AppSession._process_ui`. It renders the
  `TagList`, registers each `HTMLDependency` with the app
  (`App._register_web_dependency`) so its files get served, and sends
  `{"deps": [...], "html": ...}`.

## Cycles and the output flush

Terms (cycle, round, output flush) are defined in the `ReactiveEnvironment`
docstring; the engine side is in
[reactiveInternals.md](reactiveInternals.md#cycles-and-the-busy-count).

- A session's **cycle** is its busy period: `_busy_count` goes 0 -> 1 when one
  of its effects is queued, and back to 0 when the last one finishes (async
  part included). Module effects count on the root session. The cycle also
  bounds the session's `reactive_update` OTel span (see [otel.md](otel.md)).
- `_request_output_flush()` -> `App._request_output_flush(session)` -> after the
  next round, `App._start_output_flushes` calls `session._start_output_flush()`,
  which runs `_run_output_flush` in a task of its own (at most one per session;
  a request during a send sets `_output_flush_again`). A slow socket or slow
  `on_flush` callback delays only its own session. Requests are ignored unless
  `_output_flush_enabled` (from `init` until the loop exits).
- `_output_flush` does, in order:
  1. Returns if `_busy_count > 0`: outputs are held until the cycle ends (the
     idle transition requests another output flush).
  2. If a cycle start action is queued, nothing is queued to send, and no
     cycle just ended: runs `_start_cycle()` and returns.
  3. Within `session_context`: `bookmark._restore_context.flush_pending()`, then
     the `session.on_flush` callbacks. Returns if an async callback let an
     effect start meanwhile.
  4. `_send_queued_outputs()`: if a cycle ended (`_cycle_ended`) or anything is
     queued, copies `values`/`inputMessages`/`errors`, **resets the queues
     before awaiting the send** (a value set during the send stays queued), and
     sends one message. A cycle's message is sent **even when empty**: the
     client uses it to settle outputs still showing progress (e.g. after
     `req(False, cancel_output=True)`).
  5. `session.on_flushed` callbacks (in a `finally`). Deferred
     `insert_ui`/`remove_ui` run here. Anything they queue goes out in one more
     message (`_output_flush_tail`) without rerunning them.
  6. `_start_cycle()`: pops **one** cycle start action (an input update, an
     `invalidate_later` timer, a `session.run_once_when_idle()` fn) and runs it
     synchronously; it marks `_cycle_ended` and requests another output flush,
     so even an action that starts no effect gets its (empty) message.
- Errors in an output flush (an input update, a flush callback, the restore
  context) print a traceback and close the session.
- Registering `on_flush`/`on_flushed` requests an output flush. Anything queued
  from inside an `on_flush` callback goes out in the message being built,
  without another request.

Output lifecycle (`Outputs.__call__` -> `output_obs`, an `Effect_`):

- On invalidation, the effect sends `progress {type: "binding", id}` and the
  effect's session increments the busy count (`Effect_._create_context`). The
  count is decremented after the effect's run ends. So `busy` is sent when the
  first effect of a cycle is queued and `idle` once the last one has finished.
- On run, it sends `recalculating`, then `await asyncio.sleep(0)` so the
  message leaves before a sync renderer blocks the loop (on Windows a write
  queued behind an in-flight one otherwise goes out with the value; #1381,
  #2525). It then calls `renderer.render()` inside
  `session.clientdata._output_name_ctx(output_name)`. The result goes into
  `set_value` / `set_error` / `set_silent`, and it finally sends `recalculated`.
- The current output name is a module-level `ContextVar`
  (`_current_output_name` in `shiny/session/_session.py`), set with a token and
  reset on exit, so concurrent async renders each see their own name in
  `clientdata.output_*()` called with no id.
- `OutBoundMessageQueues` is a dict keyed by output id, so only the last
  value/error per output per message is sent. `set_value` and `set_error` clear
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
  the session**. Errors from an already destroyed effect (e.g. cleanup in a
  cancelled run) are only printed.
- **Message loop**: an exception that escapes the loop prints the traceback and
  closes the session.

## Session end and cleanup

- Triggered by `ConnectionClosed` (client left), a loop exception,
  `session.close()`, `_unhandled_error`, or `App.stop()` (closes every session).
- `AppSession._run_session_ended_tasks` (idempotent, guarded by
  `_has_run_session_ended_tasks`) does the following:
  1. Sets the flag first, so `_is_closed()` is already true during teardown.
  2. `on_ended` callbacks. Effects are destroyed here, which cancels their in-progress runs
     ([reactiveInternals.md](reactiveInternals.md#effect-destroy-and-cancellation)).
     Running `ExtendedTask`s are not cancelled.
  3. `destroy()`: root-scope destroy callbacks. Reactive values and calcs stay
     readable on this path.
  4. In a `finally`: `_end_otel_cycle_span()` and `App._remove_session` (which
     drops the app's output-flush hook after the last session).
- After that the `ExitStack` in `_run_impl` runs `_disable_output_flush` and
  `_cancel_dispatch_tasks`.
- `run_once_when_idle()` after the session ended is dropped; queued actions are
  cleared.
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
- Changing reactive state the way inputs do (between cycles):
  `session.run_once_when_idle(fn)` with a sync `fn`.
- Every new `_send_*` on `Session` needs matching implementations in
  `SessionProxy` and `shiny/express/_stub_session.py` `ExpressStubSession`.

## Pitfalls

- **Ordering between immediate and batched messages.** `recalculating`,
  `progress`, `custom`, modal/notification, and `immediate=True` insert/remove
  go out right away. Values, errors, and input messages wait until the end of
  the cycle. A custom message sent from inside a render can reach the browser
  before the output value it relates to. Use `on_flushed` if it has to come after.
- **`on_flush` / `on_flushed` are per output flush, not per round.** They run
  once the session's cycle has ended (all its effects finished), whether or
  not there are outputs to send. `reactive.on_flushed()` is different: it runs
  after every process-wide round, before effects' async parts finish.
- **Inputs are held while busy.** An `update` message is applied only at the
  start of the next cycle, so a long async effect delays every later input
  change in that session (other sessions are unaffected). Uploads (`uploadEnd`)
  and values set directly with `Value.set()` are not held.
- **Don't drop the empty output message.** Each cycle ends with a `values`
  message even if empty; the client relies on it to clear progress.
- **Sync code still blocks everyone.** Only `await` points let other sessions
  and effects run; `time.sleep()` or a CPU-bound render blocks the whole
  process.
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

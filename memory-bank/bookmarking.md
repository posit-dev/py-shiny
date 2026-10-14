---
title: "Bookmarking"
description: "How bookmarking saves and restores session state: url vs server stores, the save/restore flow, callbacks, restore context, modules, Express, input serializers, and tests. Read before touching shiny/bookmark/, adding an input that should survive a bookmark, or debugging restore."
---

# Bookmarking

Bookmarking snapshots a session's input values (plus author-supplied `values`
and, for server storage, files) and restores them from a URL query string. It is
a port of Shiny for R's bookmarking; R line references in comments are
intentional. User-facing docs live in the bundled skill
`shiny/.agents/skills/shiny-for-python/references/bookmarking.md` — update it
alongside public API changes.

## Files

| File | Contents |
|---|---|
| `shiny/bookmark/_bookmark.py` | `Bookmark` ABC (`session.bookmark`), `BookmarkApp` (root session), `BookmarkProxy` (module sessions), `BookmarkExpressStub` (no-op) |
| `shiny/bookmark/_save_state.py` | `BookmarkState`: `_save_state()` (server, writes JSON to disk) and `_encode_state()` (url query string) |
| `shiny/bookmark/_restore_state.py` | `RestoreContext`, `RestoreInputSet`, `RestoreState`, the `restore_context()` ContextVar manager, `restore_input()` |
| `shiny/bookmark/_bookmark_state.py` | Local `shiny_bookmarks/<id>` dirs and `validate_bookmark_id()` |
| `shiny/bookmark/_global.py` | `set_global_save_dir_fn` / `set_global_restore_dir_fn` (hosting-environment hooks) |
| `shiny/bookmark/_serializers.py` | `Unserializable`, `serializer_unserializable`, `serializer_file_input`, `serializer_default` |
| `shiny/bookmark/_button.py` | `input_bookmark_button`, `BOOKMARK_ID = "._bookmark_"` |
| `shiny/bookmark/_types.py` | `BookmarkStore = Literal["url", "server", "disable"]`, dir-fn types |

`shiny.bookmark` exports the public names; `input_bookmark_button` is also
re-exported from `shiny.ui` and `shiny.express.ui`.

## Enabling and stores

- Core: `App(ui, server, bookmark_store=...)`; Express:
  `shiny.express.app_opts(bookmark_store=...)`. Default `"disable"`.
- `App._init_bookmarking()` raises `TypeError` if the store is not `"disable"`
  and `ui` is not callable — the UI must be re-run per request so input
  functions can read restored values. Express wraps the UI automatically (see
  below).
- `"url"`: `BookmarkState._encode_state()` builds
  `_inputs_&id1=<json>&..._values_&k=<json>`. No `dir`; never touches disk.
- `"server"`: `BookmarkState._save_state()` picks a random id
  (`private_random_id`), gets a dir from the save-dir fn, runs `on_bookmark`
  callbacks, then writes `input.json` (and `values.json` if non-empty). Query
  string is `_state_id_=<id>`.
- Dir fn resolution (`get_bookmark_save_dir_fn` / `get_bookmark_restore_dir_fn`):
  per-app `App.set_bookmark_save_dir_fn()` / `set_bookmark_restore_dir_fn()`
  win; if unset (`MISSING`) the global fns from `_global.py` are used at call
  time; if still `None`, local `./shiny_bookmarks/<id>` (relative to cwd) is
  used, unless `in_shiny_server()` (`SHINY_PORT` set), which raises
  `NotImplementedError`.
- JSON is via `orjson` (`_utils.to_json_str` / `to_json_file`), so saved values
  must be orjson-serializable.

## Save flow

1. Trigger: the default bookmark button (`input[BOOKMARK_ID]`, an effect created
   in `BookmarkApp._create_effects()`), or author code calling
   `await session.bookmark()` (== `do_bookmark()`).
2. `BookmarkApp.get_bookmark_url()` builds a root `BookmarkState` with the
   root `session.input`, `exclude=_get_bookmark_exclude()`, and an `on_save`
   that invokes `on_bookmark` callbacks (inside `isolate()`).
3. Inputs are serialized by `Inputs._serialize()`: skips
   `_is_internal_snapshot_input()` keys (`.clientdata_*`, `._bookmark_` incl.
   namespaced), excluded ids, and inputs raising `SilentException`; applies a
   per-id serializer from `Inputs._serializers` (default identity); drops
   `Unserializable` results.
4. Full URL = clientdata protocol/host/port/pathname + `?` + query string.
5. `do_bookmark()`: if any `on_bookmarked` callback exists, they get the URL
   (typically calling `session.bookmark.update_query_string(url)`); otherwise
   `show_bookmark_url_modal()` is shown. Errors are re-raised as
   `NotifyException`. With store `"disable"` it only warns.

## Restore flow

Restore happens twice per page view, both via
`RestoreContext.from_query_string(query, app=...)`:

- **HTTP UI render** (`App._on_root_request_cb`): with `restore_context(ctx):`
  the UI function runs, so input functions see restored values via the
  ContextVar `_current_restore_context`.
- **WebSocket `init`** (`AppSession` message loop): built from
  `.clientdata_url_search` and stored with `BookmarkApp._set_restore_context()`;
  then `_create_effects()` runs. Server-side code (e.g. `@render.ui`) finds it
  through `get_current_session().bookmark._restore_context`.

`from_query_string` rules:
- `bookmark_store == "disable"` → inactive context.
- `__subapp__=1` → reset/inactive.
- `"server"` + `_state_id_` → `_load_state_qs()` (validates id, loads
  `input.json` / `values.json`, sets `dir`). `_state_id_` is ignored under
  `"url"` on purpose (security).
- Otherwise `_decode_state_qs()`; unparsable JSON params are logged and skipped.
- Any exception → reset + `_init_error_msg`, logged server-side; the client only
  sees a generic "Error restoring bookmarked state." notification.
- **Once enabled, the context is `active` even with an empty query string**
  (shinychat's `enable_bookmarking()` relies on `on_restore` always firing).
  See the comment in `from_query_string` before changing this.

`RestoreInputSet` makes each value one-shot: `get()` marks it pending,
`flush_pending()` marks it used, and used values are no longer returned.
`restore_context()` flushes on exit; `AppSession._flush()` flushes the session's
context each reactive flush. So dynamic UI only restores values if it renders in
the first flush.

## How inputs pick up restored values

`restore_input(resolved_id, default)` returns the restored value if available,
else `default`. It requires a `ResolvedId` (from `resolve_id(id)`) and raises
`TypeError` otherwise. UI functions that call it include text/textarea,
numeric, slider, select/selectize, checkbox/radio/switch, date/date range, dark
mode, code editor, submit textarea, file, navsets (`_navs.py`), accordion,
sidebar, and toolbar. Not restored: `input_password` (never bookmarked),
action/task buttons.

File inputs (`ui.input_file`): the restored value is put into a `data-restore`
attribute; the client sends it back typed `shiny.file`, whose handler in
`shiny/input_handler.py` copies files from the restore dir (via
`_restore_file_source`, which rejects symlinks/escapes) into a per-session temp
dir and re-registers `serializer_file_input`. Only `"server"` supports files;
under `"url"` saving warns and skips, restoring raises.

## Serializers

Register with `session.input.set_serializer(id, fn)`, where
`fn(value, state_dir) -> value | Unserializable` (sync or async;
`state_dir` is `None` for url store). Built-in registrations:

- `shiny.password` input handler → `serializer_unserializable` (never saved).
- `uploadEnd` in `AppSession` and the `shiny.file` handler →
  `serializer_file_input` (copies files into `state_dir`, stores basenames).

Input handlers receive the root `AppSession` and the fully resolved id, so these
land in the root `Inputs._serializers`, which is what `_serialize()` reads.

## Callbacks

| Hook | When | Argument |
|---|---|---|
| `on_bookmark` | Before persisting (after `dir` is set for server) | `BookmarkState`: add to `.values`, write files to `.dir` |
| `on_bookmarked` | After persisting; replaces the default modal | full URL `str` |
| `on_restore` | Effect with `priority=1000000` in the first flush, after the server function | `RestoreState` (`input`, `values`, `dir`) |
| `on_restored` | `session.on_flushed` after the flush is sent | `RestoreState` |

`on_restore`/`on_restored` run only if the context is `active`, inside
`isolate()`; exceptions become a warning plus error notification. All
registrations return a cancel callback.

## Modules and exclusion

- `session.bookmark.exclude` takes unscoped names. `BookmarkProxy` registers an
  `_on_get_exclude` callback on the root that namespaces them; it is removed on
  proxy destroy.
- Every `SessionProxy` (nested included) gets a `BookmarkProxy` registered
  directly on the root `AppSession`'s `BookmarkApp`, with the full namespace.
- Proxy hooks lazily register one forwarding callback on the root.
  `_scoped_on_bookmark` gives module callbacks unprefixed `values` (copied back
  with the namespace) and a `dir` subfolder `root.dir / ns`. Restore callbacks
  get `RestoreState._state_within_namespace(prefix)` with unprefixed
  `input` / `values`.
- `store`, `get_bookmark_url`, `do_bookmark`, `update_query_string` all delegate
  to the root.

## Express mode

- `shiny/express/_run.py` `create_express_app`: if `app_opts(bookmark_store=)` is
  not `"disable"`, the UI becomes `app_ui_wrapper(request)`, which re-runs the
  whole app file under a fresh `ExpressStubSession` per request.
- During UI passes `session.bookmark` is `BookmarkExpressStub` (store
  `"disable"`, all hooks no-ops), so top-level `@session.bookmark.on_*` calls
  are safe; they register for real in the server pass.

## Tests

- Unit: `tests/pytest/test_bookmark_security.py` (id validation, store/id
  gating, active-context invariant, file source checks).
- Playwright: `tests/playwright/shiny/bookmark/` — `callbacks/`, `dir/`
  (per-app and global dir fns), `modal/`, `modules/` (core, express, recursive;
  url and server via `SHINY_BOOKMARK_STORE`), `chat/`. Per-input apps under
  `tests/playwright/ai_generated_apps/bookmark/`.
- Use `utils.bookmark_utils.load_bookmark_url(page)` instead of `page.reload()`:
  Firefox restores form values on reload and masks restore bugs.
- Controller: `InputBookmarkButton` in
  `shiny/playwright/controller/_input_buttons.py` (default id `._bookmark_`).

## Pitfalls

- **New input components** must call `restore_input(resolved_id, default)` on
  their initial value in the UI function, or they bookmark but never restore.
  Add a serializer (or `serializer_unserializable`) if the raw value is not
  JSON-safe or must not be saved, and add an `ai_generated_apps/bookmark/` test.
- `restore_input` returning `None` can mean "restored as None" (accordion uses a
  `MISSING` default to distinguish) — pass a sentinel if `None` is meaningful.
- The `restore_input` docstring says to pass the unresolved id; the code
  requires a `ResolvedId`. Trust the code.
- A static (non-callable) `ui` with bookmarking enabled raises at `App()`
  construction.
- Custom `input_bookmark_button(id=...)` (multiple buttons or inside a module)
  is not wired up: exclude the id and add your own effect calling
  `session.bookmark()`.
- `session.input.set_serializer()` on a module session stores into the proxy's
  own `Inputs._serializers`, which root serialization never reads; register
  serializers on the root session with the resolved id.
- `BookmarkState.exclude` is computed before `on_bookmark` runs; appending to
  `session.bookmark.exclude` inside the callback does not affect that save.
- Module dir mismatch: save uses `root.dir / ns` (e.g. `mod`), but
  `_state_within_namespace` restores from `dir / "mod-"` (prefix with separator).
- `_state_id_` must match `[A-Za-z0-9_-]+` (≤1024 chars); custom dir fns get
  validated ids, but are still responsible for not escaping their store.

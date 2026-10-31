---
title: "App Serving and CLI"
description: "How a Shiny app is served (the App ASGI object, routes, static files, uvicorn, autoreload, proxy URL handling, file uploads) and how the `shiny` CLI works (`run`, `create`, `skills`, etc.). Read before touching shiny/_app.py, shiny/_main/, shiny/_autoreload.py, shiny/_uvicorn.py, or shiny/_hostenv.py."
---

# App Serving and CLI

How an `App` becomes an HTTP/WebSocket server, and the `shiny` command-line
entry points. Session internals and UI rendering live in
`memory-bank/architecture.md`; this doc stops at the session boundary.

## `App` is an ASGI app

`shiny/_app.py` `App.__call__` delegates to a Starlette app built in
`App.init_starlette_app()`. Routes, in match order:

| Route | Handler | Purpose |
|---|---|---|
| `/__shared` (mount, only when autoreload is on) | `StaticFiles(shiny/www/shared)` | serves `shiny-autoreload.js` |
| `/websocket/` | `App._on_connect_cb` | one `AppSession` per connection (`_create_session`, id = `secrets.token_hex(32)`) |
| `GET /` | `App._on_root_request_cb` | renders the page; callable UIs run per request inside `restore_context(...)` for bookmarking |
| `/session/{session_id}/{action}/{subpath:path}` (GET/POST) | `App._on_session_request_cb` | forwards to `AppSession._handle_request` inside `session_context`; unknown session -> JSON 404 |
| `/` (mount) | `App._dependency_handler` (a `starlette.routing.Router`) | HTML deps + `static_assets` |

Session actions (`AppSession._handle_request_impl` in
`shiny/session/_session.py`):

- `upload` (POST) -- streams the body into the current `FileUploadOperation`.
- `download` (GET) -- calls the registered download handler; a `str` result is
  served as a file path via `FileResponse`, otherwise streamed.
- `dynamic_route` (GET) -- handlers registered with `session.dynamic_route(name,
  handler)`, which returns a relative URL with a `nonce` query param.
- `dataobj/shinytest` (GET) -- test snapshot; 404 unless test mode
  (`App(test_mode=)` / `SHINY_TESTMODE`).

Other `App` pieces:

- **Middleware**: `InjectAutoreloadMiddleware` when `autoreload_url()` is set;
  `ErrorMiddleware` under Pyodide (Starlette's default 404 handler ran in a
  threadpool Pyodide can't use).
- **Lifespan**: `App._lifespan` wraps an `AsyncExitStack`; `App.on_shutdown(cb)`
  registers on it. Requires uvicorn `lifespan="on"` (what `run_app` passes).
- `App.run(**kwargs)` just calls `shiny.run_app(self, ...)`.
- `App.call_pyodide()` is the shinylive entry point (converts JS scope/strings
  to ASGI bytes).
- `App.stop()` closes every session.
- `server` may take 1 arg (`Inputs`, wrapped by
  `wrap_server_fn_with_output_session`) or 3; `None` becomes `noop_server_fn`.

## HTML dependencies and `static_assets`

- `App._register_web_dependency` mounts each `HTMLDependency` source dir at
  `/<lib_prefix><name>-<version>` (key from `html_dep_name`), inserting at
  index 0 of `_dependency_handler.routes`. Registration is keyed by
  name+version, app-wide, and never removed. Called from `_render_page` and
  from `AppSession._process_ui` (dynamic UI), so deps first seen at runtime
  are mounted lazily.
- `static_assets=` takes a dir (mounted at `/`) or a `{mount_point: path}`
  mapping (file or dir). Paths **must be absolute** (`ValueError` otherwise).
  Keys are sorted longest-first (`sort_keys_length`) so `/foo` wins over `/`.
  `create_static_asset_route` uses a `Mount` for dirs and a `Route` with a
  guessed MIME type for single files.
- `shiny/http_staticfiles.py` exports `StaticFiles`/`FileResponse`. Native:
  Starlette's, subclassed to fix `text/plain` content types for `.js` on
  Windows (#1601). Pyodide (`"pyodide" in sys.modules`): a minimal
  thread-free reimplementation (no index.html, no directory redirects).

## File uploads

`shiny/_fileupload.py`: each `AppSession` owns a `FileUploadManager` (temp
dir `fileupload-*`, removed via `on_ended(rm_upload_dir)`). Protocol, per the
module comment: `uploadInit` message -> `create_upload_operation` returns a
job id and `session/<id>/upload/<job>?w=` URL -> one POST per file (each
`with upload_op:` opens the next file, named `<n><ext>`) -> `uploadEnd`
message calls `finish()`, which errors if not all files arrived.

## `shiny` CLI (`shiny/_main/`)

Entry point `shiny = "shiny._main:main"` (pyproject `[project.scripts]`);
`python -m shiny` works via `shiny/__main__.py`. `main` is a click group with:

| Command | File | Notes |
|---|---|---|
| `run` | `_run.py` | thin wrapper over `run_app` |
| `create` | `_create.py` | templates (below) |
| `add test` | `_generate_test.py` | AI-generated Playwright test (`--provider anthropic\|openai`) |
| `skills list` / `skills path NAME` | `_skills.py` | lists/locates `shiny/.agents/skills/*/SKILL.md`; install is delegated to `library-skills` |
| `validate` | `_validate.py` | static checks of the entry file and local imports; `--json`, `--strict`, and extra `--validator module:attr` rules |
| `static` | `_static.py` | always exits 1, pointing to `shinylive export` |
| `static-assets remove\|info` | `_static.py` | deprecated shinylive asset cache management |
| `cells-to-app`, `get-shiny-deps` | `_static.py` | Quarto hooks -> `shiny/quarto.py` |

## Static validation

`shiny/_validate.py` implements the public helpers re-exported by
`shiny/validate.py`. `validate_shiny_code()` checks one source string;
`validate_shiny_file()` follows statically named local imports within the entry
file's directory. It reads source without importing it, visits each resolved
file once (including package initializers), and skips paths outside that
directory, installed packages, and unresolved imports. Each file gets a fresh
validator so module IDs and suppression comments do not collide across files.
File diagnostics add an optional `file` key to the usual line/message/code.

Scope rule: only report what a type checker or linter cannot. Syntax errors,
unknown imports, redeclared function names, and attribute/subscript access on
a `reactive.Value` are all pyright/pylance territory and are deliberately not
rules here (a syntax error is still reported, since nothing else can be
checked). Rules must encode Shiny semantics: reactive context, input
read-only-ness, renderer/ID uniqueness, extended-task constraints.

`ShinyCodeValidator` checks IDs, inputs, and decorators. Duplicate input/output
IDs are keyed by `(kind, enclosing Shiny module function, id)`: only
`@module.ui` / `@module.server` functions open a namespace, because those are
the only functions that get one at runtime; ordinary UI helper functions share
the app-level scope, so two helpers that both emit `ui.input_text("x")` warn.
App-level IDs (scope `""`) are also compared across the imported file set in
`validate_shiny_file()`, while module namespaces stay per file. `input`
references respect local shadowing: `input = {...}` in a function or at
module level hides the import, comprehension variables do not (they have
their own scope), and a parameter named `input` is Shiny's only in a server
function (named `server`, `@module.server`, or `(input, output, session)`)
or when annotated `Inputs`; otherwise it is an ordinary local. Only an
argument to `reactive.event(...)` may be an uncalled input. It also checks `@reactive.event`
position, effects that return a value, and Core-mode output/renderer pairing:
`app_outputs` (`ui.output_*` and `ui.download_*` IDs, plus any call with a
string `id=` and a `class_=` containing `-output`, for hand-built
placeholders), `app_renderers`
(`@render.*` IDs, honoring `@output(id=)`), and `app_functions` are collected
outside `@module.*` functions and outside other render functions, merged
across the file set in `validate_shiny_file()`, and compared only when both
sides are non-empty (so a UI or server in an uninspected file is not judged).
Custom renderer decorators are not recognised, so a function carrying any
decorator outside `_NON_RENDERER_DECORATORS` (reactive, module, output, and a
few stdlib ones) counts as a candidate for a placeholder; undecorated helpers
and known reactive decorators do not. IDs are read from the first positional
argument or `id=` via `_literal_id()`, and `input` is matched through
`_is_input_ref()` so import aliases such as `input as inp` are covered.
`run_app(validate=None)` reads `SHINY_VALIDATE`; an explicit bool (or the
`--validate/--no-validate` flag) wins. `shiny/_validate_reactivity.py` tracks
known values, calc functions, extended tasks, and `reactive.Value` parameter
annotations lexically. It reports reads outside a reactive context (module
level, or directly in a function named `server`, decorated `@module.server`,
or taking `(input, output, session)`; `with reactive.isolate():` and lambdas
are exempt, and decorator arguments are checked in the enclosing scope) and
reads inside extended tasks as errors; an effect without `reactive.event`
that reads and sets the same value, a calc that calls `.set()`, same-object
mutation/set, and swallowed task-result exceptions are warnings. `Inputs`
methods that configure rather than read (`set_serializer`,
`set_snapshot_preprocess`) are exempt from the context check. Import aliases
and string annotations are supported. This is a targeted static check, not
type inference across function arguments or a runtime guarantee. Before
adding a rule, sweep `shiny/api-examples`, `examples`, `shiny/templates`, and
`tests/playwright` apps with `validate_shiny_file()` for false positives:
`shiny run` prints findings to stderr, and the Playwright example tests fail
on unexpected stderr.

The CLI, startup `_validate_app_file()`, and public file helper share this path.
Startup reports issues without preventing launch; the CLI exits 1 on errors,
or on warnings with `--strict`. Plugins run per file before local suppression
comments are applied. Tests are in `test_validate*.py` and
`test_main_validate.py` under `tests/pytest/`.

## `shiny run` / `run_app`

`run_app` in `shiny/_main/_run.py` (re-exported as `shiny.run_app`):

1. `port=0` -> `_utils.random_port(host=)`. `dev_mode` (default **True**) sets
   `SHINY_DEV_MODE=1`, which makes `html_dependencies` emit
   `window.__SHINY_DEV_MODE__ = true`.
2. **App resolution** (string `app` only):
   - Strip a trailing `:app` (the CLI default is `app.py:app`).
   - `is_express_app(app, app_dir)` (`shiny/express/_is_express.py`): only for
     `.py` files that exist; a `# shiny_mode: express|core` comment in the
     first 1000 chars wins, else a top-level `import shiny.express` /
     `from shiny.express import ...` / `from shiny import express`.
   - Express: the app string becomes
     `shiny.express.app:<escape_to_var_name(abs_path)>`; the module-level
     `__getattr__` in `shiny/express/app.py` unescapes it and calls
     `wrap_express_app`. Also warns if rsconnect-python < 1.22.0.
   - Core: `resolve_app` -> `module:attr` (attr defaults to `app`). If the
     module looks like a file (`"/"` in it or ends in `.py`), it must exist and
     be a file; its dirname becomes `app_dir`. Windows drive letters are
     special-cased so `C:` isn't parsed as `module:attr`.
3. **Reload**: watches `app_dir` + `--reload-dir`s (+ the shiny package itself
   if `SHINY_PKG_AUTORELOAD` is set), with `RELOAD_INCLUDES_DEFAULT` /
   `RELOAD_EXCLUDES_DEFAULT`. Starts the autoreload server (below).
4. `maybe_setup_rsw_proxying` (Workbench log URL rewriting) and
   `_set_workbench_kwargs` (forces `ws_per_message_deflate=False`), then
   `_run_uvicorn(..., lifespan="on", loop="asyncio")`.

`shiny/_uvicorn.py` `_run_uvicorn` mirrors `uvicorn.run()` but uses
`ShinyServer`, whose `startup()` calls an `on_started` callback once the
socket is up. Reload uses `ChangeReload`; `workers > 1` uses `Multiprocess`
(constructor signature differs across uvicorn versions). Reload/workers
require an import string, not an `App` object. Exits with code 3 on failed
startup.

## Autoreload

`shiny/_autoreload.py`, two halves:

- **Parent** (`start_server`): sets `SHINY_AUTORELOAD_PORT` and a random
  `SHINY_AUTORELOAD_SECRET` in `os.environ` (inherited by uvicorn workers), then
  runs a `websockets` server on a daemon thread on `--autoreload-port`. Paths:
  `/autoreload` (browsers wait for an `"autoreload"` message) and `/notify`
  (worker sends `"reload_end"`, authenticated by the
  `Shiny-Autoreload-Secret` header). Plain HTTP hits are 301-redirected to the
  app URL (for port-sniffing tools such as the VS Code extension in Workbench).
- **Worker**: `reload_end()` is the `on_started` callback; it pings `/notify`,
  and `nudge()` broadcasts the reload. `InjectAutoreloadMiddleware` rewrites
  the `GET /` response (via `ResponseMangler`, which fixes `Content-Length`) to
  add `<script src="__shared/shiny-autoreload.js" data-ws-url=...>` before
  `</head>` -- done as middleware so it also works on error pages.

## Launching the browser

`--launch-browser` without reload: `on_started =
partial(_launchbrowser.launch_browser, host, port)` (`shiny/_launchbrowser.py`,
`webbrowser.open` on the proxied URL). With reload, the long-lived autoreload
server opens it once in `nudge()`, because `on_started` runs in a fresh worker
on every restart and can't remember it already fired.

## Proxy environments (`shiny/_hostenv.py`)

`get_proxy_url(url)` rewrites **loopback** URLs only when `is_workbench()`
(`RS_SERVER_URL` + `RS_SESSION_URL`) or `is_codespaces()`. Workbench shells
out to `/usr/lib/rstudio-server/bin/rserver-url <port>` (cached in
`port_cache`); Codespaces builds `<name>-<port>.<domain>` with https/wss.
Used for the autoreload ws URL, the browser-launch URL, and `ProxyUrlFilter`
(rewrites localhost URLs in uvicorn log lines under Workbench).

## Other entry points

- `shiny/run/` (`run_shiny_app`, `ShinyAppProc`): starts
  `python -m shiny run --port N app_file` in a subprocess, waits for
  `"Uvicorn running on"` on stderr, retries on bind errors (`start_attempts`).
  Under pytest-xdist, `port_search_range()` gives each worker its own port
  block. Used by the Playwright fixtures.
- `shiny/quarto.py`: `convert_code_cells_to_app_py` writes a generated Core
  `app.py` (`App(Path(html_file), server, static_assets=...)`), refusing to
  overwrite files lacking the "generated by Quarto" header and rejecting
  `import *` in server cells; `get_shiny_deps` emits a placeholder dependency
  that Quarto replaces with Shiny's real deps.

## `shiny create` and templates

- Internal templates live in `shiny/templates/{app,package,chat/*,markdown-stream/*}`;
  any dir with a `_template.json` (`id` required; `type`, `title`,
  `description`, `next_steps`, `follow_up` optional) is discovered by
  `find_templates`. `ShinyInternalTemplates` caches each subdir.
- An `app-express.py` next to `app-core.py` enables the Express/Core prompt;
  `copy_template_files` renames the chosen one to `app.py` and refuses to
  overwrite existing files. `type: "package"` templates (JS components) also
  rename the package via `update_component_name_in_template`.
- `--github` accepts `owner/repo[:path][@ref]` or a GitHub URL; it tries
  `refs/heads/`, `refs/tags/`, then a bare commit zip URL. Repos without
  `_template.json` fall back to "the directory is the template".

## Pitfalls

- `is_express_app` requires a `.py` suffix: `shiny run myapp` (no `.py`) on an
  Express file goes down the Core path and fails to find `myapp:app`.
- Directories are not supported as app targets: `resolve_app` exits with "is
  not a file" for any path containing `/` that isn't a file, and a bare
  directory name is imported as a module (only works for a package exporting
  `app`).
- Autoreload is decided at `App` construction time (`init_starlette_app`
  checks `SHINY_AUTORELOAD_PORT`); it only works when the process was started
  by `run_app` with `reload=True`.
- If `--autoreload-port` equals `--port`, reload is silently disabled (with a
  stderr notice), and the non-reload browser-launch path takes over.
- In reload mode `on_started` is pickled into the worker; keep it a
  module-level function or `partial`, not a closure.
- uvloop is deliberately disabled (`loop="asyncio"`, #1373). Don't drop it when
  touching `run_app`.
- Reload excludes get `shiny_bookmarks/*` up to five levels deep, working around
  a uvicorn bug that reloaded on uploaded `*.png` files in bookmark dirs.
- `_run_uvicorn` duplicates `uvicorn.run()` logic; re-check it when bumping
  uvicorn (`Config.load_app` only exists >= 0.47; `Multiprocess(target=)`
  was removed in 0.51, so `on_started` doesn't fire with multiple workers there).
- Dependency mounts are inserted ahead of `static_assets` mounts, so a
  `static_assets` path under `lib/<dep>-<version>/` is shadowed. `GET /` always
  serves the UI, never a static `index.html`.
- The Pyodide `StaticFiles` is intentionally lax on security (browser sandbox);
  never let it run natively.

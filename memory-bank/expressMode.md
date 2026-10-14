---
title: "Express Mode"
description: "Internals of Shiny Express (`shiny/express/`): app detection and loading, the displayhook-based UI capture, `RecallContextManager`, `expressify`, express modules, the session proxies, per-session re-execution, and auto-placed render outputs. Read it before changing anything in `shiny/express/`, adding a `shiny.ui` function, or debugging an Express app that renders the wrong UI."
---

# Express Mode

The high-level Core-vs-Express contrast lives in
`memory-bank/architecture.md` ("Express vs Core Mode"). This doc covers the
machinery.

## Detection and entry point

- `shiny run` (`shiny/_main/_run.py`) calls `is_express_app(app, app_dir)`
  (`shiny/express/_is_express.py`). If it returns true, the app target is rewritten
  to `shiny.express.app:<escaped path>`, using `escape_to_var_name()` from
  `shiny/express/_utils.py`. `shiny/testserver/_test_server.py` uses the same check.
- `is_express_app()` returns true when the file ends in `.py` and either:
  - a magic comment `# shiny_mode: express|core` appears in its first 1000
    characters (`find_magic_comment_mode()`; this always wins), or
  - a **top-level** statement is `import shiny.express`, `from shiny.express import ...`,
    or `from shiny import express`. `DetectShinyExpressVisitor` deliberately does
    not recurse, so an import inside a function or an `if` does not count.
- `shiny/express/app.py` defines a module `__getattr__` that unescapes the name and
  calls `wrap_express_app(Path(name))`.
- `wrap_express_app()` (`_run.py`) registers the file under a synthetic package name
  `shiny_express_app_<n>` in `package_filepath_map` and imports that package.
  `ShinyExpressAppImportFinder` (a `sys.meta_path` finder installed when the module
  is imported) and `ShinyExpressAppLoader` handle the import. The loader sets
  `submodule_search_locations` to the app directory, which is what makes
  `from . import utils` work. Each wrapped app gets its own package name, which
  matters for shinylive, where several apps can run at once.

## Building the App: `create_express_app()`

1. If a `globals.py` sits next to the app, it is imported **once**, under
   `session_context(None)`.
2. The UI phase runs `run_express()` under `session_context(ExpressStubSession())`
   and tagifies the result immediately, so that tagify errors surface here (see
   Pitfalls). A `PageHtmlDocument` returned by `page_opts(html=)` is kept as-is.
3. If `app_opts(bookmark_store=)` is anything other than `"disable"`, the UI becomes a
   `Request -> UI` function that re-runs `run_express()` with a fresh stub session on
   every page load. Bookmark restore needs this (see "App UI types" in
   `architecture.md`).
4. The server is `express_server(input, output, session)`, which just calls
   `run_express(file, package_name)` again and **ignores the returned UI**. That is
   how per-session server logic exists: every top-level statement re-executes in each
   new session, with the real session active.
5. `App(...)` options come from a sibling `www/` directory (mounted at `/`), merged
   with `stub_session.app_opts`, which `express.app_opts()` fills in during the UI
   phase (`_merge_app_opts()`, `_normalize_app_opts()`). In the server phase,
   `app_opts()` is a no-op.

## `run_express()`: executing the file

- The source is parsed with `ast`, then `DisplayFuncsTransformer` is applied, then
  `ast.fix_missing_locations`.
- `sys.displayhook` is swapped for `set_result`, and a fresh top-level
  `RecallContextManager(ui.page_auto)` is created
  (`reset_top_level_recall_context_manager()`, which uses `page_auto_cm()` in
  `ui/_page.py`) and entered. It is stored in a module global, so
  `page_opts()` can reach it.
- Top-level statements run one at a time in a shared namespace (`__name__ == "app"`,
  `__package__` set to the synthetic package, and `input` pre-bound to
  `InputNotImportedShim`):
  - `def` / `async def` nodes are compiled in `"exec"` mode.
  - Every other node is wrapped in `ast.Interactive` and compiled in `"single"`
    mode. This is the REPL trick: CPython then calls `sys.displayhook` on every
    expression statement, including ones nested inside `with` / `for` / `if` blocks
    (but not inside function bodies).
- Exiting the top-level manager calls `page_auto(*children, **page_opts)`. The
  result goes to `set_result`, and `run_express()` returns it.
- If a top-level `app` variable holds a `shiny.App` and there is no magic comment,
  `run_express()` raises: the file looks like both Core and Express.
- An `AttributeError` is re-raised as `RuntimeError`, because uvicorn misreports
  `AttributeError` from an app import (issue #937).

### The displayhook chain

- Every collector wraps its append with `htmltools.wrap_displayhook_handler`:
  - `Tag`, `TagList`, and `Tagifiable` objects pass through unchanged.
  - Objects with `_repr_html_` become `HTML(...)`. A bare `df.head()` line
    therefore renders a table.
  - `None` and `...` are dropped.
  - Anything else, such as a bare string, is appended as-is.
- `DisplayFuncsTransformer` (`expressify_decorator/_node_transformers.py`) inserts
  `_expressify_decorator_function_def` (`_func_displayhook.py`) as the
  **outermost** decorator on each top-level or block-nested `def`. After the other
  decorators have run, it passes the result to `sys.displayhook`, but only if the
  result is tag-like or has `_repr_html_`. Plain functions are not displayed. A
  `@render.*` function is a `Renderer`, which is `Tagifiable`, so it gets displayed.
  This is how outputs get placed.
- `TopLevelTransformer` only descends into `Module`, `With`, `If`, `For`, `While`,
  `Try`, and similar block statements. It never descends into function bodies.

## `RecallContextManager` (`_recall_context.py`)

`with ui.card():` collects its children like this:

- An Express container such as `express.ui.card(...)`
  (`shiny/express/ui/_cm_components.py`) returns
  `RecallContextManager(ui.card, args=..., kwargs=...)` and does not build any UI
  yet.
- `__enter__` saves the current `sys.displayhook` and installs its own.
  Each displayed value is appended to `self.args`, so children become positional
  arguments after any arguments the caller passed.
- `__exit__` restores the previous hook. If no exception was raised, it calls
  `fn(*args, **kwargs)` and sends the result to the parent's displayhook. Nesting
  composes this way, ending at the top-level `page_auto` manager.
- If a child is itself a `RecallContextManager` that was used without `with`
  (for example `ui.card_header("Header")` on its own line), the parent's
  `displayhook` runs `with x: pass`, which calls it with only its explicit arguments
  (covered by `test_recall_context_manager`).
- `RecallContextManager.tagify()` lets a manager be used as a plain value, for
  example passed as an argument. It calls `fn` and tagifies the result, or uses
  `_repr_html_`.
- `wrap_recall_context_manager(fn)` is a generic wrapper that turns a function
  into a manager factory.

`ui.hold()` (`express/ui/_hold.py`) is the opposite: `HoldContextManager` collects
values into a `TagList` instead of displaying them. Use `with ui.hold() as x:` and
later show `x` on its own line.

## `page_auto` / `page_opts`

- `express.ui.page_opts(**)` (`express/ui/_page.py`) only writes into the top-level
  manager's `kwargs`. The page function runs at the end, so the call can appear
  anywhere at top level, and later calls overwrite earlier ones key by key. Outside
  an Express app it raises `RuntimeError`.
- `ui.page_auto()` (`shiny/ui/_page.py`) chooses the page from the **top-level**
  children:
  - Any `NavPanel` or `NavMenu` selects `page_navbar` (one sidebar is allowed).
  - Otherwise, exactly one `Sidebar` selects `page_sidebar`. More than one raises
    `NotImplementedError`.
  - Otherwise `fillable` / `full_width` choose between the fillable, fluid, and
    fixed variants.
  - `page_fn=` overrides all of this. `html=` returns `page_html()` and keeps only
    the children's dependencies; it rejects `page_fn` and other page options.

## `expressify` (`expressify_decorator/_expressify.py`)

- `expressify(fn)` re-reads the function's source from `linecache` (so it works in
  Jupyter cells). It locates the matching `def` with `TargetFunctionTransformer` /
  `ast_matches_func`, matching on `co_name` plus the line number of the `def` or any
  of its decorators.
- `FuncBodyDisplayHookTransformer` then wraps each expression statement in the body
  in a call to `__auto_displayhook_sys__(...)`. That call is `auto_displayhook`,
  which skips `None`; the alias is injected into the new function's globals and into
  `__builtins__`. Inner functions are left alone. `has_docstring=True` stops a leading
  string from being displayed.
- The edited AST is compiled as a whole module, so closures survive, and
  `find_code_for_func` picks out the new code object. A fresh `FunctionType` is
  built with the original closure and defaults.
- Results are memoized in `code_cache`, keyed by `fn.__code__`. The cache is
  disabled under Pyodide.
- Async functions are not supported. A failed lookup raises a `RuntimeError` that
  explains the likely causes.
- `expressify_unwrap_inplace()` mutates `__code__` in place, after unwrapping any
  `__wrapped__` chain. `render.express` (`shiny/render/_express.py`) uses it, then
  runs the function with `sys.displayhook` swapped for a collector and sends the
  collected UI through `session._process_ui`.

## Express modules (`_module.py`)

`@express.module` applies `expressify` to the function. It returns
`wrapper(id, *args, **kwargs)`, which:

1. calls `require_active_session(None).make_scope(id)`,
2. enters `session_context(module_session)`, and
3. calls the function with the module's `input`, `output`, `session`, and any extra
   arguments.

The same call yields namespaced UI in the UI phase, where
`ExpressStubSession.make_scope` returns a `SessionProxy` over the stub, and
namespaced server logic in each real session. There is no separate `.ui` / `.server`
pair as in Core.

## Session, input, and output proxies

- `shiny/express/__init__.py` defines a module-level `__getattr__` for `input`,
  `output`, and `session`. It returns the **current** session's object, or an
  `_ExpressOnlyPlaceholder` (which raises on use) when no session is active.
- Because the file re-runs per session, `from shiny.express import input` re-binds
  the name to that session's `Inputs` on every run. Holding onto `express.input` and
  reading it lazily is the fragile pattern the module comment warns about.
- `ExpressStubSession` (`_stub_session.py`) is a no-op `Session` with empty
  `Inputs`, a real `Outputs`, `BookmarkExpressStub`, and the `app_opts` dict.
  `is_stub_session()` returns true, and `SessionProxy` forwards that check. Code that
  must not act during the UI phase checks it:
  - `Effect_.__init__` in `reactive/_reactives.py` skips registration.
  - `Outputs` refuses to actually render.
  - Download registration in `render/_render.py` is skipped.
  - App code can check it too, for example `api-examples/MarkdownStream/app-express.py`.

## Render functions auto-placing their UI

- `Renderer.__call__` (`render/renderer/_renderer.py`) records `self._session =
  get_current_session()` and auto-registers with `session.output`. In the UI phase
  that session is the stub, so the effect is skipped. In a real session the output
  is live. An explicit `@output` afterwards undoes the auto-registration
  (`_on_register()`).
- When the renderer is displayed, the parent manager later tagifies it.
  `Renderer.tagify()` calls `_render_auto_output_ui()`, which runs
  `auto_output_ui(**self._auto_output_ui_kwargs)` under the captured session, so
  module namespacing applies. If `auto_output_ui()` returns `None`, the renderer
  raises `TypeError`.
- `express.output_args(**kwargs)` (`_output.py`) sets `_auto_output_ui_kwargs`.
  `suspend_display` is a deprecated alias for `ui.hold`.
- To place an output manually, wrap the `def` in `with ui.hold():` and use the
  Core `ui.output_*()` function.

## Keeping `express.ui` in sync with `shiny.ui`

`shiny/express/ui/__init__.py` is maintained **by hand**; nothing generates it.
Items fall into four groups:

- **Re-exported** unchanged from `shiny.ui` or `htmltools`.
- **Container managers**, rewritten in `_cm_components.py` with copied
  signatures and docstrings.
- **Shims** in `_insert.py` (`insert_accordion_panel`, `insert_nav_panel`). They
  take a title plus contents instead of a prebuilt panel, which would otherwise
  need `hold()`.
- **Swapped classes**: `Chat` and `MarkdownStream` come from `shinychat.express`.

Enforcement:

- `tests/pytest/test_express_ui.py::test_express_ui_is_complete` requires every name
  in `shiny.ui.__all__` to be either in `shiny.express.ui.__all__` or listed in
  `_known_missing_express_ui["shiny.ui"]`, and Express-only names to be listed under
  `"shiny.express.ui"`.
- `test_render_output_controls_complete` (same file) and
  `tests/pytest/test_render_auto_output_ui.py` enforce the renderer to
  `ui.output_*` 1:1 pairing and check that `auto_output_ui()` parameters match it.

## Pitfalls

- **Adding a `shiny.ui` function**:
  - Add it to `shiny/express/ui/__init__.py`, both the import and `__all__`.
  - If it takes children, write a `RecallContextManager` wrapper in
    `_cm_components.py` instead.
  - If it is page-level or auto-placed by a renderer, list it in
    `_known_missing_express_ui`.
  - Then add an `express.ui.*` entry to `docs/_quartodoc-express.yml` and an
    `app-express.py` example.
  - `test_express_ui_is_complete` fails if you skip the export, but **nothing
    checks that a container wrapper's signature or docstring matches its Core
    function**. Update both by hand whenever the Core parameters change.
- Any top-level expression whose value is not `None` gets displayed. That includes a
  function call made only for its side effect, or a bare string. Assign it
  (`_ = ...`) to silence it.
- The entire file runs once for the UI and **again for every session**, plus once per
  page load when bookmarking is on. Put expensive setup in `globals.py` or an
  imported module, which run once per process. Don't use module-level mutable state
  as cross-session state.
- Container managers build their UI in `__exit__`. If an exception occurs inside the
  `with` block, nothing is emitted. Calling one without `with` gives an empty
  container.
- `expressify` and `render.express` don't support `async def`. A decorator applied
  *below* `expressify` must return the original function, not a wrapper, or the AST
  lookup fails.
- `_is_express.py` is meant to be copied verbatim into rsconnect-python. Keep
  `is_express_app()` in that file and don't add new imports from `shiny` (it
  currently only imports `.._docstring`).
- A comment in `run_express()` mentions `replace_top_level_recall_context_manager()`,
  but no function by that name exists. Only `reset_` and `get_` exist.
- `express.app_opts()` only takes effect in the UI phase, and `page_opts()` only
  inside a standalone Express app. Both raise under Core or Quarto.

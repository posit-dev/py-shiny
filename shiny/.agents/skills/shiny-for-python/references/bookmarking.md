
# Bookmarking Shiny for Python apps

## Overview

Bookmarking snapshots an app's `input` values (plus optional custom values) and
restores them later from a URL. Use it instead of manually encoding state into
query strings or building a custom persistence layer.

## Store values

`bookmark_store` (on `App(...)` or `app_opts(...)`) accepts three values:

| Value | Where state lives | Trade-offs |
|---|---|---|
| `"url"` | Entirely in the URL query string | Shareable anywhere with zero server setup. Keep the serialized state under ~65k characters; file inputs cannot be serialized. |
| `"server"` | On disk; the URL carries only a state id | Handles large state and file inputs (files are copied into the state directory). URLs only restore on a deployment that still has that directory — the hosting environment must persist it (see "Server-side storage location"). |
| `"disable"` | Nowhere (the default) | Bookmarking is off: `session.bookmark()` warns and does nothing. |

Prefer `"url"` whenever the state fits — it needs no storage management.

## Enable bookmarking

**Express mode** — call `app_opts` at the top of the app file:

```python
from shiny.express import app_opts, session, ui

app_opts(bookmark_store="url")

ui.input_radio_buttons("letter", "Choose a letter", choices=["A", "B", "C"])
ui.input_bookmark_button()


@session.bookmark.on_bookmarked
async def _(url: str):
    await session.bookmark.update_query_string(url)
```

**Core mode** — the UI **must be a function** taking a `starlette.Request`
(a static UI object cannot receive restored values), and `App` needs
`bookmark_store=`:

```python
from starlette.requests import Request
from shiny import App, Inputs, Outputs, Session, ui

def app_ui(request: Request):
    return ui.page_fluid(
        ui.input_radio_buttons("letter", "Choose a letter", choices=["A", "B", "C"]),
        ui.input_bookmark_button(),
    )

def server(input: Inputs, output: Outputs, session: Session):
    @session.bookmark.on_bookmarked
    async def _(url: str):
        await session.bookmark.update_query_string(url)

app = App(app_ui, server, bookmark_store="url")
```

With this in place, all inputs are saved on bookmark and restored on page load
automatically — no per-input code needed.

## Trigger a bookmark

- **UI button:** `ui.input_bookmark_button()` — clicking it calls
  `session.bookmark()` for you.
- **Programmatic** (e.g. bookmark on every change):

```python
@reactive.effect
@reactive.event(input.letter, ignore_init=True)
async def _():
    await session.bookmark()
```

After the state is saved, `on_bookmarked` callbacks receive the bookmark URL.
If none are registered, a modal dialog shows the URL; registering the
`update_query_string(url)` callback (as above) writes it to the browser's
address bar instead.

## Save and restore custom (non-input) values

Reactive values, computed state, etc. go in `state.values` — do NOT create
hidden inputs to smuggle them into the bookmark:

```python
from shiny.bookmark import BookmarkState, RestoreState

@session.bookmark.on_bookmark
def _(state: BookmarkState):
    state.values["page"] = current_page()

@session.bookmark.on_restore
def _(state: RestoreState):
    if "page" in state.values:
        ui.update_radio_buttons("page", selected=state.values["page"])
```

Unlike inputs, `state.values` are never applied to the UI automatically — apply
them yourself in `on_restore` (runs before reactive expressions) or, for slow
late-rendering components, `on_restored` (runs after). `state.input` is also
readable in these callbacks, but input restoration has already happened via the
UI.

## Exclude inputs

```python
session.bookmark.exclude.append("transient_input")
```

Passwords are excluded automatically; file inputs are unserializable under
`"url"` storage. For custom exclusion logic, register a serializer:
`session.input.set_serializer(id, fn)` where `fn` returns a JSON-serializable
value or `shiny.bookmark.Unserializable()`.

## Server-side storage location

For `bookmark_store="server"` in hosted environments, control where state is
written (set these **before** creating the `App`):

```python
from pathlib import Path
from shiny.bookmark import set_global_restore_dir_fn, set_global_save_dir_fn

bookmark_dir = Path(__file__).parent / "bookmarks"

def save_dir(id: str) -> Path:
    d = bookmark_dir / id
    d.mkdir(parents=True, exist_ok=True)
    return d

set_global_save_dir_fn(save_dir)
set_global_restore_dir_fn(lambda id: bookmark_dir / id)
```

## Quick reference

| Need | API |
|---|---|
| Enable (Express / Core) | `app_opts(bookmark_store="url")` / `App(..., bookmark_store="url")` |
| Bookmark now | `await session.bookmark()` |
| Put bookmark URL in address bar | `session.bookmark.update_query_string(url)` inside `on_bookmarked` |
| Get URL without side-band UI | `await session.bookmark.get_bookmark_url()` |
| Lifecycle hooks | `session.bookmark.on_bookmark` / `on_bookmarked` / `on_restore` / `on_restored` |
| Skip an input | `session.bookmark.exclude.append(id)` |
| Custom input component restores itself | `shiny.bookmark.restore_input(resolved_id, default)` when building its HTML |

## Common mistakes

- Core-mode UI defined as a plain object → nothing restores. The UI must be a
  function accepting a `Request`.
- `bookmark_store` left unset (default `"disable"`) → `session.bookmark()`
  warns and does nothing.
- Expecting `state.values` to restore into the UI automatically → they are
  server-only; call `ui.update_*()` in `on_restore`.
- `ui.input_bookmark_button()` inside a module (or two buttons in one app) →
  the default id only auto-bookmarks at the top level. Give each button a
  unique `id=`, exclude that id, and wire your own
  `@reactive.event(input.<id>)` effect that calls `await session.bookmark()`.
- Mutating `state.input` in `on_bookmark` to drop values → ignored on save;
  use `session.bookmark.exclude` instead.
- Module inputs missing from `state.values` checks → names are prefixed with
  the module namespace, like inputs and outputs.

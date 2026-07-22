
# Theming Shiny for Python apps

## Overview

App appearance is controlled by a `ui.Theme` object passed to the `theme=`
argument of a page function. A theme starts from a **preset** (Bootstrap,
`"shiny"`, or a Bootswatch theme) and is customized by chaining `.add_*()`
methods that inject Sass **before** the preset compiles — so you set Bootstrap
Sass variables like `$primary` and get consistent, coherent styling across every
component.

Do NOT hand-edit compiled `bootstrap.min.css`, and do NOT paste large raw CSS
overrides fighting Bootstrap's specificity. Set the Sass variable instead.
Compiling a customized theme requires `libsass` (`pip install "shiny[theme]"`);
the bundled `"bootstrap"` and `"shiny"` presets are pre-compiled and need no
extra install.

## Apply a preset

Pass a `ui.Theme` (or just its preset name via the constructor) to the page's
`theme=`. In Express, use `ui.page_opts(theme=...)` (see `references/express.md`).

```python
from shiny import App, ui

app_ui = ui.page_sidebar(
    ui.sidebar(ui.input_slider("n", "N", 0, 100, 20)),
    ui.h2("Themed app"),
    title="My App",
    theme=ui.Theme("flatly"),   # any Bootswatch preset, "bootstrap", or "shiny"
)

def server(input, output, session):
    pass

app = App(app_ui, server)
```

`ui.Theme.available_presets()` lists all valid preset names.

## Pre-built themes and a runtime picker: shinyswatch

`ui.Theme` already bundles every Bootswatch preset, so a static Bootswatch look
needs no extra package. Reach for the separate **shinyswatch** package
(`pip install shinyswatch`) when you want ready-made theme objects or a
**live theme switcher** the user can operate at runtime:

```python
import shinyswatch
from shiny import App, ui

app_ui = ui.page_sidebar(
    shinyswatch.theme_picker_ui(),          # dropdown to switch themes live
    ui.h2("Themed app"),
    title="My App",
    theme=shinyswatch.theme.slate(),        # a ready-made Bootswatch theme object
)

def server(input, output, session):
    shinyswatch.theme_picker_server()       # wire up the live switcher

app = App(app_ui, server)
```

Omit `theme_picker_ui()`/`theme_picker_server()` if you only want the theme
object. See `shiny/api-examples/theme/` for full examples.

## Customize Sass variables (colors, fonts)

`.add_defaults(...)` sets Bootstrap Sass **variables** (as `!default`, so the
preset can still override structural values). Keyword names use underscores and
convert to kebab-case: `primary_color="#..."` becomes `$primary-color`. The
methods return the theme, so chain them.

```python
from shiny import ui

my_theme = (
    ui.Theme("shiny")
    .add_defaults(
        primary="#00aa88",                          # $primary
        bootstrap_font_size_base="1.1rem",          # $font-size-base
    )
    # .add_mixins(...)  — inject Sass placed after preset mixins
    .add_rules("""
        .card { border-radius: 1rem; }              # literal CSS/Sass rules
        em { color: $warning; }                     # can reference Sass vars
    """)
)

app_ui = ui.page_fluid(ui.h2("Hi"), theme=my_theme)
```

- `.add_defaults(...)` — set/override Sass variables (colors, fonts, spacing).
- `.add_rules(...)` — append custom CSS/Sass rules (may reference `$variables`).
- `.add_mixins(...)` — add/override Sass mixins after the preset's.

To avoid the runtime `libsass` dependency, precompile once with
`my_theme.to_css()` and pass the resulting `.css` file path to `theme=`.

## Dark mode

`ui.input_dark_mode()` adds a light/dark toggle (Bootstrap color modes). Give it
an `id` to read the current mode reactively as `input.<id>()`; drive it from the
server with `ui.update_dark_mode("light"|"dark")`.

```python
from shiny import reactive
from shiny.express import input, render, ui

ui.input_dark_mode(id="mode")          # omit id if you don't need to read it

@render.text
def current():
    return f"Mode: {input.mode()}"     # "light" or "dark"

@reactive.effect
@reactive.event(input.go_dark)
def _():
    ui.update_dark_mode("dark")
```

`mode=` on `input_dark_mode` forces the initial mode; the default follows the
user's system preference.

## brand.yml

`ui.Theme.from_brand()` builds a theme from a `_brand.yml` file (shared brand
colors, fonts, logo). Pass `__file__`, a directory, or the file path:

```python
from shiny.express import ui
ui.page_opts(theme=ui.Theme.from_brand(__file__))
```

For authoring the `_brand.yml` file itself, use the external `shiny:brand-yml`
skill — do not hand-write the spec here.

## Custom CSS / JS assets

For one-off styling outside the theme, include a stylesheet with
`ui.include_css(path)` (or inline `ui.tags.style(...)`), and serve files from a
`www/` directory or via `static_assets` on `App`. Reach for `ui.Theme` first for
anything color/font/Bootstrap-wide; use raw CSS only for genuinely local tweaks.

## Quick reference

| Need | Use |
|---|---|
| Default Shiny look | `ui.Theme("shiny")` (bundled, no libsass) |
| Plain Bootstrap 5 | `ui.Theme("bootstrap")` (bundled) |
| A Bootswatch look | `ui.Theme("flatly")`, `"darkly"`, `"cosmo"`, `"minty"`, ... |
| List all presets | `ui.Theme.available_presets()` |
| Live theme switcher | shinyswatch: `theme_picker_ui()` + `theme_picker_server()` |
| Set a Sass variable | `.add_defaults(primary="#...")` |
| Add custom CSS/Sass rules | `.add_rules("...")` |
| Add/override Sass mixins | `.add_mixins(...)` |
| Theme from brand.yml | `ui.Theme.from_brand(__file__)` |
| Precompile to CSS | `theme.to_css()` -> save, pass file path to `theme=` |
| Dark/light toggle | `ui.input_dark_mode(id="mode")` |
| Set mode from server | `ui.update_dark_mode("dark")` |
| Include a stylesheet | `ui.include_css(path)` |

## Common mistakes

- Editing `bootstrap.min.css` or piling on `!important` CSS -> set the Bootstrap
  Sass variable with `.add_defaults(...)` so the whole app stays consistent.
- `ImportError` about `libsass`/`sass` when using a customized theme ->
  `pip install "shiny[theme]"`; or precompile with `.to_css()` and ship the CSS.
- Passing `ui.Theme(...)` somewhere other than a page's `theme=` (e.g. as a
  child tag) -> it raises; it is only valid as the `theme=` argument.
- Reading `input.mode()` with no `id` on `input_dark_mode` -> add
  `id="mode"` so the current color mode is reported as an input.
- Using kebab-case keyword names like `.add_defaults("primary-color"=...)` ->
  use underscores (`primary_color=`); they convert to `$primary-color` for you.
- Invalid preset name -> `ValueError`; check `ui.Theme.available_presets()`.

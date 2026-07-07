# Component and Renderer Implementation Patterns

Recipes for adding new UI components and output renderers to py-shiny. For
porting a component from R's bslib specifically, use the
`.claude/skills/port-from-bslib/SKILL.md` skill instead — it covers asset
vendoring on top of these steps.

## UI component pattern

When implementing a UI component (see `shiny/ui/_input_slider.py` for a
representative example):

1. Create the file as `shiny/ui/_component_name.py` with an explicit `__all__`
   tuple listing the public names.
2. Resolve the input's ID with `resolve_id(id)` (from `shiny.module`) so the
   component works inside modules.
3. For input components, support bookmarking by passing the initial value
   through `restore_input(resolved_id, value)` (from `shiny.bookmark`).
4. Use `shiny_input_label()` (from `shiny/ui/_utils.py`) to render the label
   consistently with other inputs.
5. Return a `Tag`/`TagList`. If the component depends on bslib assets, include
   `components_dependencies()`; component-specific JS/CSS is attached as
   `HTMLDependency` objects defined in `shiny/ui/_html_deps_*.py`.
6. Export the function:
   - `shiny/ui/__init__.py` (Core API)
   - `shiny/express/ui/__init__.py` (Express API, if applicable — most UI
     functions are re-exported there, sometimes wrapped as a
     `RecallContextManager` for container components)
7. Input components usually need a companion `update_*()` function that sends a
   message via `session.send_input_message(id, ...)`; the TypeScript input
   binding handles it in `receiveMessage()`.
8. Add docs: docstring per `.claude/references/documentation-style.md`, an
   example app in `shiny/api-examples/<name>/` (`app-core.py` +
   `app-express.py`), and entries in `docs/_quartodoc-core.yml` /
   `docs/_quartodoc-express.yml`.
9. For input components, add a Playwright controller class in
   `shiny/playwright/controller/` (see the `_input_*.py` files there) and
   register it in the testing quartodoc YAML.
10. Add unit tests in `tests/pytest/` and an end-to-end test app + test in
    `tests/playwright/shiny/`.
11. Update `CHANGELOG.md`.

## Renderer pattern

Output components and renderers have a **1:1 mapping**: each renderer pairs
with exactly one `ui.output_*()` function (the one returned by its
`auto_output_ui()`), and each output component exists to serve exactly one
renderer. When adding an output component, add its renderer alongside it (and
vice versa) — don't create shared or orphaned output UI functions.

When creating a custom output renderer (base class:
`shiny/render/renderer/_renderer.py`):

1. Inherit from `Renderer[IT]`, where `IT` is the type the app author's value
   function returns.
2. Implement `auto_output_ui(self)` — the UI that Express mode renders
   automatically for this output (Core mode users place the matching
   `ui.output_*()` themselves).
3. Implement **either**:
   - `transform(self, value: IT)` — the simple path. It only receives
     non-`None` values and must return something JSON-serializable; the base
     class handles resolving the value function and early-`None` returns.
   - `render(self)` — full control. Call the app-supplied value function via
     `await self.fn()` (always async-wrapped) and return a JSON-serializable
     result.
4. The renderer auto-registers with the session's `Output` when it receives the
   value function, so app authors don't need `@output`. Use
   `self.output_id` / `self.__name__` for the output's name (module prefix not
   included).
5. Export from `shiny/render/__init__.py` and add docs entries (quartodoc
   YAMLs, example app).

> **Do not use `@output_transformer()`** (`shiny/render/transformer/`) for new
> renderers — it is superseded by the `Renderer` class and slated for removal.

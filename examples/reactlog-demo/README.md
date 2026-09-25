# Northstar reactive planning demo

Upload the contents of `dist/` to a static host such as Netlify. `index.html` is the entry point; keep `recording.webm` beside it. No build command or Python backend is needed to view the exported report. For repository-based deployment, generate the directory locally first and publish `dist`.

The report explores a recorded sales planning session: baseline and campaign modules, discounts, growing demand, shared forecast horizon, overhead, profit targets, and three Matplotlib plots. Click a node to inspect its dependencies. Double-click a module box to collapse or expand it; keyboard users can focus the box and press Enter or Space. Edges crossing a collapsed module remain connected. Plot nodes show the latest recorded image at or before the selected timeline step. The recording tab shows the actual app interaction.

This is a static interactive report of the session. Changing the original app's inputs requires running `app.py` with Shiny. Browser input/output events and plot images are observed; internal reactive execution and dependencies are inferred by static analysis, not runtime profiling.

## Rebuild

From the repository root, with the local Shiny checkout, Matplotlib, and Playwright installed:

```sh
python -m playwright install chromium
python examples/reactlog-demo/build_demo.py
```

The builder copies the app and its module to `dist/app.py` and `dist/scenario.py`, records real interactions, and exports `index.html`, `reactlog.json`, `recording-actions.json`, and `recording.webm`. `dist/` is ignored by Git; this source directory is the reproducible version.

Module analysis follows local Python imports, including aliases and relative package imports, without executing imported code. The App code tab includes a file selector, and node source details point to the original file and line. Call `generate_reactlog(code, source_path="path/to/app.py")` in Python or use `shiny inspect path/to/app.py` from the CLI. Module analysis supports `@module.ui` and `@module.server` definitions called with literal string IDs, including repeated and nested instances, reactive arguments, and a directly returned reactive. Third-party package implementations, star imports, imports inside functions, dynamically generated IDs, and composite module return values are not resolved. Raster plots from `render.plot`/`render.image` are captured as embedded snapshots; interactive HTML widgets can be viewed in the recording but are not replayed as live widgets.

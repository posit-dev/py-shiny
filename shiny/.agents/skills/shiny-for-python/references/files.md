# File uploads and downloads in Shiny for Python

## Overview

Shiny handles the browser plumbing for you. For uploads, `ui.input_file`
receives the file, stores it in a temp file, and hands the server a
`list[FileInfo]` describing each upload. For downloads, `@render.download`
registers a handler that streams bytes to the browser when a paired
`ui.download_button`/`ui.download_link` is clicked.

Do NOT build a raw `<input type="file">`, parse multipart bodies yourself, or
add a custom Starlette route to serve a file — Shiny already exposes both
directions through the components below.

## Upload a file: `ui.input_file`

Add the input to the UI; read it in the server as `list[FileInfo]`. The value
is `None` until the user picks a file, so guard with `req` (see
`references/reactivity.md`) before touching it. Each `FileInfo` is a dict with
`name` (the browser filename), `size`, `type` (MIME), and `datapath` (path to
a temp file holding the data — open this, not `name`).

```python
import pandas as pd
from shiny import App, Inputs, Outputs, Session, reactive, render, req, ui
from shiny.types import FileInfo

app_ui = ui.page_fluid(
    ui.input_file("file1", "Choose CSV file", accept=[".csv"], multiple=False),
    ui.output_data_frame("preview"),
)

def server(input: Inputs, output: Outputs, session: Session):
    @reactive.calc
    def df() -> pd.DataFrame:
        files: list[FileInfo] | None = input.file1()
        req(files)                       # wait until a file is chosen
        return pd.read_csv(files[0]["datapath"])

    @render.data_frame
    def preview():
        return df()

app = App(app_ui, server)
```

Use `multiple=True` to accept several files (iterate the whole list).
`accept=` sets the file input's DOM `accept` attribute — a hint to the browser's
file picker: extensions (`".csv"`), MIME types (`"text/plain"`), or wildcards
(`"image/*"`). It only filters the picker; it is not enforced server-side, so
still validate the uploaded file's type/name yourself.

## Download a generated file: `@render.download`

Pair a handler with a `ui.download_button` (or `ui.download_link`) whose id
matches the function name. The handler either **returns a path** to an existing
file on disk, or **yields** strings/bytes for content generated on the fly.
When yielding, pass `filename=` so the browser knows what to name it.

```python
import io
from datetime import date
import pandas as pd
from shiny import App, Inputs, Outputs, Session, render, ui

app_ui = ui.page_fluid(
    ui.download_button("download_csv", "Download CSV"),
)

def server(input: Inputs, output: Outputs, session: Session):
    @render.download(filename=lambda: f"data-{date.today().isoformat()}.csv")
    def download_csv():
        df = pd.DataFrame({"x": [1, 2, 3], "y": [4, 5, 6]})
        with io.StringIO() as buf:
            df.to_csv(buf, index=False)
            yield buf.getvalue()

app = App(app_ui, server)
```

`filename` accepts a plain string or a no-arg callable for a **dynamic name**
(evaluated per click, so it can read reactive values). Return a path only for a
file that already exists on disk — for temp files you create, `yield` the
bytes instead so Shiny does not leave the temp file behind. The handler may be
sync or async.

In Express mode, `@render.download` renders its own button — pass
`label=` and skip the separate `ui.download_button` (see `references/express.md`).

## Quick reference

| Need | Use |
|---|---|
| Upload control | `ui.input_file("id", "Label", accept=[".csv"], multiple=False)` |
| Read uploaded files | `input.id()` -> `list[FileInfo]` (or `None`) |
| Open uploaded data | `open(fileinfo["datapath"])` / `pd.read_csv(fileinfo["datapath"])` |
| Guard empty upload | `req(input.id())` before reading |
| Download button / link | `ui.download_button("id", "Label")` / `ui.download_link(...)` |
| Download handler | `@render.download(filename=...)` returning a path or yielding bytes/str |
| Dynamic filename | `@render.download(filename=lambda: ...)` |

## Common mistakes

- Reading `input.file1()` without a guard -> `None`/`TypeError` before any
  upload. Call `req(input.file1())` (or check `is None`) first.
- Opening `fileinfo["name"]` -> file-not-found; `name` is the browser's label.
  Open `fileinfo["datapath"]`, the temp file Shiny wrote.
- Assuming the temp file persists -> a later upload may delete it. Read it
  immediately (e.g. inside a `@reactive.calc`).
- `yield`ing content with no `filename=` -> the browser downloads an
  unhelpful default name. Set `filename=` when yielding.
- Returning a path to a temp file you created -> Shiny won't clean it up;
  `yield` the bytes instead.
- Download button never fires -> the function name must match the button id,
  and the button must be registered in the UI.
- Building a raw `<input type="file">` or a custom download route -> use
  `ui.input_file` and `@render.download`; Shiny wires the transport for you.

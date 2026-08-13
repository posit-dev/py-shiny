# Documentation Style Guide

Conventions for writing docstrings and API examples in py-shiny. API docs are
rendered by [quartodoc](https://machow.github.io/quartodoc/) (configured in
`docs/_quartodoc-*.yml`), so docstrings must follow the conventions below to
render correctly.

## Docstring format

Use **NumPy-style (numpydoc) docstrings** with dash-underlined section headers.
(Not Google-style, and not free-form reST — though Sphinx *roles* are used for
cross-references, see below.)

- Brief one-line description first, then optional longer paragraphs.
- Section order: `Parameters`, `Returns`, `Yields`, `Raises`, `Notes`,
  `Examples`, `See Also`.
- Parameter entries are the bare name (no type — types come from annotations)
  followed by an indented description:

  ```
  Parameters
  ----------
  id
      An input id.
  label
      An input label.
  ```

- `Returns` uses a bare `:` placeholder instead of repeating the type:

  ```
  Returns
  -------
  :
      A UI element.
  ```

- `Raises` names the exception class and describes when it is raised.

## Inline markup and cross-references

- Inline code: use double backticks (reST style), e.g. ``` ``True`` ``` ,
  ``` ``None`` ``` , ``` ``"400px"`` ``` . Markdown single backticks also
  render, but match the double-backtick style of surrounding code.
- Cross-reference other API objects with Sphinx roles, using `~` to display
  only the final name segment:
  - Functions: `` :func:`~shiny.ui.update_slider` ``
  - Classes: `` :class:`~shiny.ui.AnimationOptions` ``, `` :class:`~datetime.datetime` ``
  - Also available: `` :meth:` ` ``, `` :attr:` ` ``
- `See Also` is a markdown bullet list of cross-reference roles:

  ```
  See Also
  --------
  * :func:`~shiny.ui.update_slider`
  * :class:`~shiny.ui.AnimationOptions`
  ```

- Quarto markdown (callouts, divs) is allowed in docstrings since docs are
  rendered with Quarto:

  ```
  ::: {.callout-note title="Server value"}
  A number, date, or date-time (depending on the class of value).
  :::
  ```

## Input component conventions

Every `input_*()` function documents its server-side value in a
`Notes` section using the "Server value" callout shown above. This is the
canonical place to describe what `input.<id>()` returns on the server.

## Examples via `@add_example()`

Do **not** write inline `Examples` sections for public API functions. Instead,
attach runnable example apps with the `@add_example()` decorator
(`shiny/_docstring.py`):

- Examples live in `shiny/api-examples/<function_name>/` (or
  `shiny/experimental/api-examples/` for `shiny.experimental`).
- Each example directory contains `app-core.py` (Core syntax) and
  `app-express.py` (Express syntax). A single `app.py` is treated as the Core
  variant. Provide both variants whenever the function exists in both APIs.
- Support files (data, modules, `icons.py`, etc.) may sit alongside the app
  files, but must not be named `app.py` or start with `app-` — those names are
  reserved for example variants.
- `@add_example()` looks up the directory matching the function's `__name__`.
  When the example directory has a different name (e.g. several functions
  share one example), pass `example_name="other_dir"`. Prefer `example_name=`
  over the legacy `ex_dir=` relative-path parameter.
- Use `@no_example()` (optionally `@no_example("express")` /
  `@no_example("core")`) to intentionally skip an example for a function or
  for one mode.
- Examples are only injected when `SHINY_ADD_EXAMPLES=true` (set by
  `make quartodoc`), so missing examples surface as **docs build failures**,
  not import errors. The docs build fails on missing API examples — every new
  public function needs an example directory or an explicit `@no_example()`.

## Registering new API in the docs site

Adding a docstring is not enough to publish it. New public functions/classes
must be listed in the quartodoc config:

- `docs/_quartodoc-core.yml` — Core API reference
- `docs/_quartodoc-express.yml` — Express API reference
- `docs/_quartodoc-testing.yml` — Testing/controller API reference

Add entries in **alphabetical order within their section**. Express variants of
UI functions generally need entries in both the core and express files.

## Verifying docs changes

```bash
make docs           # Build with quartodoc (slow — run at the end; sets SHINY_ADD_EXAMPLES=true)
make docs-preview   # Build and serve locally
```

A successful `make docs` run is the check that examples resolve, cross-reference
roles are valid, and quartodoc YAML entries are correct.

## Full template

````python
from .._docstring import add_example

@add_example()
def input_foo(id: str, label: TagChild, *, width: Optional[str] = None) -> Tag:
    """
    Create a foo input control.

    Longer description if needed. Use ``double backticks`` for inline code and
    :func:`~shiny.ui.update_foo` style roles for cross-references.

    Parameters
    ----------
    id
        An input id.
    label
        An input label.
    width
        The CSS width, e.g. ``"400px"`` or ``"100%"``.

    Returns
    -------
    :
        A UI element.

    Notes
    ------
    ::: {.callout-note title="Server value"}
    A string with the current value of the foo input.
    :::

    See Also
    --------
    * :func:`~shiny.ui.update_foo`
    """
````

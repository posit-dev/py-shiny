from __future__ import annotations

import base64
import html
import re
from importlib.resources import files
from pathlib import Path
from typing import Literal, Optional, TypedDict, Union

import quartodoc.ast as qast
from griffe import dataclasses as dc
from griffe import expressions as exp
from griffe.docstrings import dataclasses as ds
from plum import dispatch
from quartodoc import MdRenderer
from quartodoc.pandoc.blocks import DefinitionList
from quartodoc.renderers.base import convert_rst_link_to_md, sanitize

# from quartodoc.ast import preview

SHINY_PATH = Path(files("shiny").joinpath())


# This is the same as the FileContentJson type in TypeScript.
class FileContentJson(TypedDict):
    name: str
    content: str
    type: Literal["text", "binary"]


class Renderer(MdRenderer):
    style = "shiny"

    @dispatch
    def render(self, el: qast.DocstringSectionSeeAlso):
        # The See Also section in the Shiny docs has bare function references, ones that
        # lack a leading :func: and backticks. This function fixes them. In the future,
        # we can fix the docstrings in Shiny, once we decide on a standard. Then we can
        # remove this function.
        return prefix_bare_functions_with_func(el.value)

    @dispatch
    def render(self, el: Union[dc.Object, dc.Alias]):
        # If `el` is a protocol class that only has a `__call__` method,
        # then we want to display information about the method, not the class.
        if len(el.members) == 1 and "__call__" in el.members.keys():
            return self.render(el.members["__call__"])

        # Not a __call__ Alias, so render as normal.
        rendered = super().render(el)

        converted = convert_rst_link_to_md(rendered)

        check_if_has_auto_example(el, converted)

        return converted

    @dispatch
    def render(self, el: ds.DocstringSectionText):
        # functions like shiny.ui.tags.b have html in their docstrings, so
        # we escape them. Note that we are only escaping text sections, but
        # since these cover the top text of the docstring, it should solve
        # the immediate problem.
        rendered = super().render(el)
        return html_escape_except_backticks(rendered)

    @dispatch
    def render_annotation(self, el: str):
        return sanitize(el)

    # TODO-future; Can be removed once we use quartodoc 0.3.5
    # Related: https://github.com/machow/quartodoc/pull/205
    @dispatch
    def render(self, el: ds.DocstringAttribute):
        row = [
            sanitize(el.name),
            self.render_annotation(el.annotation),
            sanitize(el.description or "", allow_markdown=True),
        ]
        return row

    @dispatch
    def render_annotation(self, el: None):
        return ""

    @dispatch
    def render_annotation(self, el: exp.Expr):
        # an expression is essentially a list[exp.ExprName | str]
        # e.g. Optional[TagList]
        #   -> [Name(source="Optional", ...), "[", Name(...), "]"]

        return "".join(map(self.render_annotation, el))

    @dispatch
    def render_annotation(self, el: exp.ExprName):
        # e.g. Name(source="Optional", full="typing.Optional")
        return f"[{el.name}](`{el.canonical_path}`)"

    @dispatch
    # Overload of `quartodoc.renderers.md_renderer` to fix bug where the descriptions
    # are cut off and never display other places. Fixing by always displaying the
    # documentation.
    def summarize(self, obj: Union[dc.Object, dc.Alias]) -> str:
        # get high-level description
        doc = obj.docstring
        if doc is None:
            docstring_parts = []
        else:
            docstring_parts = doc.parsed

        if len(docstring_parts) and isinstance(
            docstring_parts[0], ds.DocstringSectionText
        ):
            description = docstring_parts[0].value

            # ## Approach: Always return the full description!
            return description

            # ## Alternative: Add ellipsis if the lines are cut off

            # # If the description is more than one line, only show the first line.
            # # Add `...` to indicate the description was truncated
            # parts = description.split("\n")
            # short = parts[0]
            # if len(parts) > 1:
            #     short += "&hellip;"

            # return short

        return ""

    # Consolidate the parameter type info into a single column
    @dispatch
    def render(self, el: ds.DocstringParameter):
        param = f'<span class="parameter-name">{el.name}</span>'
        annotation = self.render_annotation(el.annotation)
        if annotation:
            param = f'{param}<span class="parameter-annotation-sep">:</span> <span class="parameter-annotation">{annotation}</span>'
        if el.default:
            param = f'{param} <span class="parameter-default-sep">=</span> <span class="parameter-default">{el.default}</span>'

        # Wrap everything in a code block to allow for links
        param = "<code>" + param + "</code>"

        return (param, el.description)

    @dispatch
    def render(self, el: ds.DocstringSectionParameters):
        rows = list(map(self.render, el.value))
        # rows is a list of tuples of (<parameter>, <description>)

        return str(DefinitionList(rows))

    @dispatch
    def signature(self, el: dc.Function, source: Optional[dc.Alias] = None):
        if el.name == "__call__":
            # Ex: experimental.ui._card.ImgContainer.__call__(self, *args: Tag) -> Tagifiable
            sig = super().signature(el, source)

            # Remove leading function name (before `__call__`) and `self` parameter
            # Ex: __call__(*args: Tag) -> Tagifiable
            sig = re.sub(r"[^`\s]*__call__\(self, ", "__call__(", sig, count=1)

            return sig

        # Not a __call__ Function, so render as normal.
        return super().signature(el, source)


def html_escape_except_backticks(s: str) -> str:
    """
    HTML-escape a string, except for content inside of backticks.

    Examples
    --------
        s = "This is a <b>test</b> string with `backticks <i>unescaped</i>`."
        print(html_escape_except_backticks(s))
        #> This is a &lt;b&gt;test&lt;/b&gt; string with `backticks <i>unescaped</i>`.
    """
    # Split the string using backticks as delimiters
    parts = re.split(r"(`[^`]*`)", s)

    # Iterate over the parts, escaping the non-backtick parts, and preserving backticks in the backtick parts
    escaped_parts = [
        html.escape(part) if i % 2 == 0 else part for i, part in enumerate(parts)
    ]

    # Join the escaped parts back together
    escaped_string = "".join(escaped_parts)
    return escaped_string


def prefix_bare_functions_with_func(s: str) -> str:
    """
    The See Also section in the Shiny docs has bare function references, ones that lack
    a leading :func: and backticks. This function fixes them.

    If there are bare function references, like "~shiny.ui.panel_sidebar", this will
    prepend with :func: and wrap in backticks.

    For example, if the input is this:
        "~shiny.ui.panel_sidebar  :func:`~shiny.ui.panel_sidebar`"
    This function will return:
        ":func:`~shiny.ui.panel_sidebar`  :func:`~shiny.ui.panel_sidebar`"
    """

    def replacement(match: re.Match[str]) -> str:
        return f":func:`{match.group(0)}`"

    pattern = r"(?<!:`)~\w+(\.\w+)*"
    return re.sub(pattern, replacement, s)


def read_file(file: str | Path, root_dir: str | Path | None = None) -> FileContentJson:
    file = Path(file)
    if root_dir is None:
        root_dir = Path("/")
    root_dir = Path(root_dir)

    type: Literal["text", "binary"] = "text"

    try:
        with open(file, "r") as f:
            file_content = f.read()
            type = "text"
    except UnicodeDecodeError:
        # If text failed, try binary.
        with open(file, "rb") as f:
            file_content_bin = f.read()
            file_content = base64.b64encode(file_content_bin).decode("utf-8")
            type = "binary"

    return {
        "name": str(file.relative_to(root_dir)),
        "content": file_content,
        "type": type,
    }


def check_if_has_auto_example(el, converted):
    if re.search(r"(^|\n)(#{2,6} Examples\n\n|Examples\n------)", converted):
        return

    if "\n.. quartodoc-disable-example-check" in converted:
        # Automatic example detection sometimes has false positives,
        # e.g. `close()` from `Session.close` or `Progress.close`.
        # Add `.. quartodoc-no-examples` to the docstring to disable this check
        return

    if isinstance(el, dc.Alias) and "experimental" in el.target_path:
        p_example_dir = SHINY_PATH / "experimental" / "api-examples" / el.name
        return
    elif isinstance(el, dc.Alias) and "express" in el.target_path:
        p_example_dir = SHINY_PATH / "express" / "api-examples" / el.name
    elif isinstance(el, dc.Alias) and el.target_path.startswith("htmltools"):
        return
    else:
        p_example_dir = SHINY_PATH / "api-examples" / el.name

    if (p_example_dir / "app.py").exists():
        # import pdb

        # pdb.set_trace()
        raise RuntimeError(
            f"An example exists for {p_example_dir} but is not included in the documentation in {el.target_path}. Decorate `{el.name}()` with `@add_example()` to add the example."
        )

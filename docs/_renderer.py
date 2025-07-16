from __future__ import annotations

import base64
import html
import os
import re
from importlib.resources import files
from pathlib import Path
from typing import Literal, Optional, TypedDict, Union

import quartodoc.ast as qast
from griffe import (
    Alias,
    DocstringAttribute,
    DocstringSectionText,
    Expr,
    ExprName,
    Function,
    Object,
)
from plum import dispatch
from quartodoc import MdRenderer
from quartodoc.renderers.base import convert_rst_link_to_md, sanitize
from quartodoc.renderers.md_renderer import ParamRow

# from quartodoc.ast import preview

SHINY_PATH = Path(files("shiny").joinpath())


# This is the same as the FileContentJson type in TypeScript.
class FileContentJson(TypedDict):
    name: str
    content: str
    type: Literal["text", "binary"]


class Renderer(MdRenderer):
    style = "shiny"
    express_api = os.environ.get("SHINY_MODE", "core") == "express"

    @dispatch
    def render(self, el: qast.DocstringSectionSeeAlso):
        # The See Also section in the Shiny docs has bare function references, ones that
        # lack a leading :func: and backticks. This function fixes them. In the future,
        # we can fix the docstrings in Shiny, once we decide on a standard. Then we can
        # remove this function.
        return prefix_bare_functions_with_func(el.value)

    @dispatch
    def render(self, el: Union[Object, Alias]):
        # If `el` is a protocol class that only has a `__call__` method,
        # then we want to display information about the method, not the class.
        if len(el.members) == 1 and "__call__" in el.members.keys():
            return self.render(el.members["__call__"])

        # Not a __call__ Alias, so render as normal.
        rendered = super().render(el)

        converted = convert_rst_link_to_md(rendered)

        # If we're rendering the API reference for Express, try our best to
        # keep you in the Express site. For example, something like shiny.ui.input_text()
        # simply gets re-exported as shiny.express.ui.input_text(), but it's docstrings
        # will link to shiny.ui, not shiny.express.ui. This fixes that.
        if self.express_api:
            converted = converted.replace("shiny.ui.", "shiny.express.ui.")
            # If this el happens to point to itself, it's probably intentionally
            # pointing to Core (i.e., express context managers mention that they
            # wrap Core functions), so don't change that.
            # TODO: we want to be more aggressive about context managers always
            # pointing to the Core docs?
            if f"shiny.express.ui.{el.name}" in converted:
                print(f"Changing Express link to Core for: {el.name}")
                converted = converted.replace(
                    f"shiny.express.ui.{el.name}", f"shiny.ui.{el.name}"
                )
            converted = converted.replace("shiny.render.", "shiny.express.render.")

        check_if_missing_expected_example(el, converted)

        assert_no_sphinx_comments(el, converted)

        return converted

    @dispatch
    def render(self, el: DocstringSectionText):
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
    def render(self, el: DocstringAttribute) -> ParamRow:
        row = ParamRow(
            el.name,
            el.description or "",
            annotation=self.render_annotation(el.annotation),
        )
        return row

    @dispatch
    def render_annotation(self, el: None):
        return ""

    @dispatch
    def render_annotation(self, el: Expr):
        # an expression is essentially a list[ExprName | str]
        # e.g. Optional[TagList]
        #   -> [Name(source="Optional", ...), "[", Name(...), "]"]

        return "".join(map(self.render_annotation, el))

    @dispatch
    def render_annotation(self, el: ExprName):
        # e.g. Name(source="Optional", full="typing.Optional")
        return f"[{el.name}](`{el.canonical_path}`)"

    @dispatch
    # Overload of `quartodoc.renderers.md_renderer` to fix bug where the descriptions
    # are cut off and never display other places. Fixing by always displaying the
    # documentation.
    def summarize(self, obj: Union[Object, Alias]) -> str:
        # get high-level description
        doc = obj.docstring
        if doc is None:
            docstring_parts = []
        else:
            docstring_parts = doc.parsed

        if len(docstring_parts) and isinstance(
            docstring_parts[0], DocstringSectionText
        ):
            description = docstring_parts[0].value

            # # ## Approach: Always return the full description!
            # return description

            parts = description.split("\n")

            # # Alternative: Add ellipsis if the lines are cut off
            # # If the description is more than one line, only show the first line.
            # # Add `...` to indicate the description was truncated
            # short = parts[0]
            # if len(parts) > 1 and parts[1].strip() != "":
            #     short += "&hellip;"

            # Alternative: Add take the first paragraph as the description summary
            short_parts: list[str] = []
            # Capture the first paragraph (lines until first empty line)
            for part in parts:
                if part.strip() == "":
                    break
                short_parts.append(part)

            short = " ".join(short_parts)
            short = convert_rst_link_to_md(short)

            return short

        return ""

    @dispatch
    def signature(self, el: Function, source: Optional[Alias] = None):
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

    If there are bare function references, like "~shiny.ui.sidebar", this will
    prepend with :func: and wrap in backticks.

    For example, if the input is this:
        "~shiny.ui.sidebar  :func:`~shiny.ui.sidebar`"
    This function will return:
        ":func:`~shiny.ui.sidebar`  :func:`~shiny.ui.sidebar`"
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


def check_if_missing_expected_example(el, converted):
    if re.search(r"(^|\n)#{2,6} Examples", converted):
        # Manually added examples are fine
        return

    if not el.canonical_path.startswith("shiny"):
        # Only check Shiny objects for examples
        return

    def is_no_ex_decorator(x):
        # With griffe<0.42.0, it kept parentheses on decorators, but as of 0.42.0, it
        # removes them. At some point in the future we can just use the no-parens case.
        if x == "no_example()" or x == "no_example":
            return True

        no_ex_decorators = [
            f'no_example("{os.environ.get("SHINY_MODE", "core")}")',
            f"no_example('{os.environ.get('SHINY_MODE', 'core')}')",
        ]

        return x in no_ex_decorators

    if hasattr(el, "decorators") and any(
        [is_no_ex_decorator(d.value.canonical_name) for d in el.decorators]
    ):
        # When an example is intentionally omitted, we mark the fn with `@no_example`
        return

    if not el.is_function:
        # Don't throw for things that can't be decorated
        return

    if not el.is_exported:
        # Don't require examples on "implicitly exported" functions
        # In practice, this covers methods of exported classes (class still needs ex)
        return

    no_req_examples = ["shiny.experimental"]
    if any([el.target_path.startswith(mod) for mod in no_req_examples]):
        return

    raise RuntimeError(
        f"{el.name} needs an example, use `@add_example()` or manually add `Examples` section:\n"
        + (f"> file     : {el.filepath}\n" if hasattr(el, "filepath") else "")
        + (f"> target   : {el.target_path}\n" if hasattr(el, "target_path") else "")
        + (f"> canonical: {el.canonical_path}" if hasattr(el, "canonical_path") else "")
    )


def assert_no_sphinx_comments(el, converted: str) -> None:
    """
    Sphinx allows `..`-prefixed comments in docstrings, which are not valid markdown.
    We don't allow Sphinx comments or directives, sorry!
    """
    pattern = r"\n[.]{2} .+(\n|$)"
    if re.search(pattern, converted):
        raise RuntimeError(
            f"{el.name} includes Sphinx-styled comments or directives, please remove.\n"
            + (f"> file     : {el.filepath}\n" if hasattr(el, "filepath") else "")
            + (f"> target   : {el.target_path}\n" if hasattr(el, "target_path") else "")
            + (
                f"> canonical: {el.canonical_path}"
                if hasattr(el, "canonical_path")
                else ""
            )
        )

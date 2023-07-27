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
from quartodoc.renderers.base import convert_rst_link_to_md, sanitize

SHINY_PATH = Path(files("shiny").joinpath())

SHINYLIVE_CODE_TEMPLATE = """
```{{shinylive-python}}
#| standalone: true
#| components: [editor, viewer]
#| layout: vertical
#| viewerHeight: 400{0}
```
"""

DOCSTRING_TEMPLATE = """\
{rendered}

{header} Examples

{examples}
"""


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

        if isinstance(el, dc.Alias) and "experimental" in el.target_path:
            p_example_dir = SHINY_PATH / "experimental" / "api-examples" / el.name
        else:
            p_example_dir = SHINY_PATH / "api-examples" / el.name

        if (p_example_dir / "app.py").exists():
            example = ""

            files = list(p_example_dir.glob("**/*"))

            # Sort, and then move app.py to first position.
            files.sort()
            app_py_idx = files.index(p_example_dir / "app.py")
            files = [files[app_py_idx]] + files[:app_py_idx] + files[app_py_idx + 1 :]

            for f in files:
                if f.is_dir():
                    continue
                file_info = read_file(f, p_example_dir)
                if file_info["type"] == "text":
                    example += f"\n## file: {file_info['name']}\n{file_info['content']}"
                else:
                    example += f"\n## file: {file_info['name']}\n## type: binary\n{file_info['content']}"

            example = SHINYLIVE_CODE_TEMPLATE.format(example)

            return DOCSTRING_TEMPLATE.format(
                rendered=converted,
                examples=example,
                header="#" * (self.crnt_header_level + 1),
            )

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
    def render_annotation(self, el: exp.Expression):
        # an expression is essentially a list[exp.Name | str]
        # e.g. Optional[TagList]
        #   -> [Name(source="Optional", ...), "[", Name(...), "]"]

        return "".join(map(self.render_annotation, el))

    @dispatch
    def render_annotation(self, el: exp.Name):
        # e.g. Name(source="Optional", full="typing.Optional")
        return f"[{el.source}](`{el.full}`)"

    @dispatch
    def summarize(self, el: dc.Object | dc.Alias):
        result = super().summarize(el)
        return html.escape(result)

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

        clean_desc = sanitize(el.description, allow_markdown=True)
        return (param, clean_desc)

    @dispatch
    def render(self, el: ds.DocstringSectionParameters):
        rows = list(map(self.render, el.value))
        header = ["Parameter", "Description"]

        return self._render_table(rows, header)

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

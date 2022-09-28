"""Sphinx extensions for running python code and/or Shiny apps in the browser via WASM
Usage::
    .. shinyapp::
        :width: 100%
        :height: 500px

   .. shinylive-editor::
        :width: 100%
        :height: 500px

    .. cell::
        :width: 100%
        :height: 500px

    .. terminal::
        :width: 100%
        :height: 500px
"""

import os
from os.path import dirname, join, abspath
import shutil

from docutils.nodes import SkipNode, Element
from docutils.parsers.rst import directives
from sphinx.application import Sphinx
from sphinx.util.docutils import SphinxDirective
from htmltools import css

# Local path to the shinylive/ directory (currently provided by rstudio/shinylive)
# This is only needed for the "self-contained" version of the API reference.
# (in other words, you can set this to "" if you already have the shinylive/ directory
# in your repo, just make sure to also point SHINYLIVE_DEST to the right place)
SHINYLIVE_SRC = os.getenv(
    "SHINYLIVE_SRC",
    abspath(join(dirname(__file__), "../../../shinylive/build/shinylive")),
)


class ShinyElement(Element):
    def html(self):
        style = css(height=self["height"], width=self["width"])
        type = self["type"]
        code = self["code"]
        if type == "shinylive-editor":
            # TODO: allow the layout to be specified (right now I don't think we need
            # horizontal layout, but maybe someday we will)
            code = (
                "#| standalone: true\n#| components: [editor, viewer]\n#| layout: vertical\n#| viewerHeight: 400\n"
                + code
            )

        return (
            f'<pre class="shinylive-python" style="{style}"><code>{code}</code></pre>'
        )


def _run(self: SphinxDirective, type: str):
    code = "\n".join(self.content)
    width = self.options.pop("width", "100%")
    height = self.options.pop("height", None)

    return [ShinyElement(type=type, code=code, height=height, width=width)]


class BaseDirective(SphinxDirective):
    has_content = True
    required_arguments = 0
    option_spec = {
        "width": directives.unchanged,
        "height": directives.unchanged,
    }


class ShinyAppDirective(BaseDirective):
    def run(self):
        return _run(self, "shinyapp")


class ShinyliveEditorDirective(BaseDirective):
    def run(self):
        return _run(self, "shinylive-editor")


class CellDirective(BaseDirective):
    def run(self):
        return _run(self, "cell")


class TerminalDirective(BaseDirective):
    def run(self):
        return _run(self, "terminal")


def setup(app: Sphinx):
    # After the build is finished, if necessary, copy over the necessary shinylive
    # static files the usual _static/ directory won't work given the limitations in it's
    # current design
    def after_build(app: Sphinx, error: object):
        if not SHINYLIVE_SRC:
            return
        shinylive = os.path.join(app.outdir, "shinylive")
        if os.path.exists(shinylive):
            shutil.rmtree(shinylive)
        shutil.copytree(SHINYLIVE_SRC, shinylive)
        shutil.copy(
            os.path.join(SHINYLIVE_SRC, "../shinylive-sw.js"),
            os.path.join(app.outdir, "shinylive-sw.js"),
        )

    app.connect(  # pyright: ignore[reportUnknownMemberType]
        "build-finished", after_build
    )

    def append_element_html(self: Sphinx, node: Element):
        # Not sure why type checking doesn't work on this line
        self.body.append(node.html())  # type: ignore
        raise SkipNode

    def skip(self: Sphinx, node: Element):
        raise SkipNode

    app.add_node(  # pyright: ignore[reportUnknownMemberType]
        ShinyElement,
        html=(append_element_html, None),
        latex=(skip, None),
        textinfo=(skip, None),
        text=(skip, None),
        man=(skip, None),
    )
    app.add_directive("shinyapp", ShinyAppDirective)
    app.add_directive("shinylive-editor", ShinyliveEditorDirective)
    app.add_directive("cell", CellDirective)
    app.add_directive("terminal", TerminalDirective)

    return {"version": "0.1"}

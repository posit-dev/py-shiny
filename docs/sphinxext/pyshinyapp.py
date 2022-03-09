"""Sphinx extensions for running python code and/or Shiny apps in the browser via WASM
Usage::
    .. shinyapp::
        :width: 100%
        :height: 500px

   .. shinyeditor::
        :width: 100%
        :height: 500px

    .. cell::
        :width: 100%
        :height: 500px

    .. terminal::
        :width: 100%
        :height: 500px
"""

# N.B. place subclasses of Element in here (not conf.py)...because Sphinx!
# https://github.com/sphinx-doc/sphinx/pull/6754

import os
import shutil

from docutils.nodes import SkipNode, Element
from docutils.parsers.rst import directives
from sphinx.application import Sphinx
from sphinx.util.docutils import SphinxDirective
from htmltools import css

# Current assumption is that rstudio/prism-experiments repo is a sibling of rstudio/prism
SHINYLIVE_DIR = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "../../../prism-experiments/shinylive",
    )
)

if not os.path.exists(SHINYLIVE_DIR):
    raise Exception(
        "Couldn't find the shinylive/ directory (i.e., the static files necessary to render shiny apps client-side)"
    )


class ShinyElement(Element):
    def html(self):
        style = css(height=self["height"], width=self["width"])
        type = self["type"]
        # right now pyshiny gives you the editor, but that'll probably change
        if type == "shinyeditor":
            type = "shiny"
        return (
            f'<pre class="py{type}" style="{style}"><code>{self["code"]}</code></pre>'
        )


def _run(self: SphinxDirective, type: str):
    code = "\n".join(self.content)
    width = self.options.pop("width", "100%")
    height = self.options.pop("height", "500px")

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


class ShinyEditorDirective(BaseDirective):
    def run(self):
        return _run(self, "shinyeditor")


class CellDirective(BaseDirective):
    def run(self):
        return _run(self, "cell")


class TerminalDirective(BaseDirective):
    def run(self):
        return _run(self, "terminal")


def setup(app: Sphinx):
    # After the build is finished, copy over the necessary shinylive static files
    # the usual _static/ directory won't work given the limitations in it's current
    # design
    def after_build(app: Sphinx, error):
        shinylive = os.path.join(app.outdir, "shinylive")
        if os.path.exists(shinylive):
            shutil.rmtree(shinylive)
        shutil.copytree(SHINYLIVE_DIR, shinylive)
        shutil.copy(
            os.path.join(SHINYLIVE_DIR, "../serviceworker.js"),
            os.path.join(app.outdir, "serviceworker.js"),
        )

    app.connect("build-finished", after_build)

    def append_element_html(self, node: Element):
        self.body.append(node.html())
        raise SkipNode

    def skip(self, node: Element):
        raise SkipNode

    app.add_node(
        ShinyElement,
        html=(append_element_html, None),
        latex=(skip, None),
        textinfo=(skip, None),
        text=(skip, None),
        man=(skip, None),
    )
    app.add_directive("shinyapp", ShinyAppDirective)
    app.add_directive("shinyeditor", ShinyEditorDirective)
    app.add_directive("cell", CellDirective)
    app.add_directive("terminal", TerminalDirective)

    return {"version": "0.1"}

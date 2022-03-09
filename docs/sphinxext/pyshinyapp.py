"""Sphinx extension for embedding a purely client-side Shiny app via WASM
Usage::
   .. pyshinyapp::
"""

# N.B. place subclasses of Element in here (not conf.py)...because Sphinx!
# Boy, this was a fun one to track down
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


class PyShinyApp(Element):
    """
    Renders contents of the ``.. pyshinyapp::`` directive according to
    https://rstudio.github.io/prism-experiments/embedded-app.html
    """

    def html(self):
        style = css(height=self["height"], width=self["width"])
        # TODO: Include <script> only once per page
        return (
            """
            <script type="module">
              const serviceWorkerPath = "/serviceworker.js";

              // Start the service worker as soon as possible, to maximize the
              // resources it will be able to cache on the first run.
              if ("serviceWorker" in navigator) {
                navigator.serviceWorker
                  .register(serviceWorkerPath)
                  .then(() => console.log("Service Worker registered"))
                  .catch(() => console.log("Service Worker registration failed"));

                navigator.serviceWorker.ready.then(() => {
                  if (!navigator.serviceWorker.controller) {
                    // For Shift+Reload case; navigator.serviceWorker.controller will
                    // never appear until a regular (not Shift+Reload) page load.
                    window.location.reload();
                  }
                });
              }
            </script>
            <link rel="stylesheet" href="/shinylive/Components/App.css">
            <script src="/shinylive/run-python-blocks.js" type="module"></script>
            """
            f'<pre class="pyshinyapp" style="{style}">{self["code"]}</pre>'
        )


class PyShinyDirective(SphinxDirective):
    """
    The ``.. pyshinyapp::`` directive which places the contents into a code block
    via :class:`PyShinyAppElement`.
    """

    has_content = True
    required_arguments = 0
    option_spec = {
        "width": directives.unchanged,
        "height": directives.unchanged,
    }

    def run(self):
        code = "\n".join(self.content)
        width = self.options.pop("width", "100%")
        height = self.options.pop("height", "500px")

        return [PyShinyApp(code=code, height=height, width=width)]


def skip(self, node: Element):
    raise SkipNode


def append_element_html(self, node: Element):
    self.body.append(node.html())
    raise SkipNode


def after_build(app: Sphinx, error):
    shinylive = os.path.join(app.outdir, "shinylive")
    if os.path.exists(shinylive):
        shutil.rmtree(shinylive)
    shutil.copytree(SHINYLIVE_DIR, shinylive)
    shutil.copy(
        os.path.join(SHINYLIVE_DIR, "../serviceworker.js"),
        os.path.join(app.outdir, "serviceworker.js"),
    )


def setup(app: Sphinx):
    # After the build is finished, copy over the necessary shinylive static files
    # the usual _static/ directory won't work given the limitations in it's current
    # design
    app.connect("build-finished", after_build)

    app.add_node(
        PyShinyApp,
        html=(append_element_html, None),
        latex=(skip, None),
        textinfo=(skip, None),
        text=(skip, None),
        man=(skip, None),
    )
    app.add_directive("pyshinyapp", PyShinyDirective)

    return {"version": "0.1"}

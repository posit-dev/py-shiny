from __future__ import annotations

import os

from htmltools import HTMLDependency

from . import __version__
from .ui._html_deps_py_shiny import busy_indicators_dep


def _page_deps(*, include_css: bool) -> list[HTMLDependency]:
    """
    The complete, ordered set of HTML dependencies that every Shiny page needs.

    This is the one definition of that set: use it wherever a page is assembled, so the
    two forms a page can take -- a tag tree, and a complete HTML document -- cannot
    drift apart.

    Requirejs, jQuery, and Shiny must come before any other dependency (see
    :func:`require_deps` for why requirejs is here at all).

    Parameters
    ----------
    include_css
        Whether to include Shiny's CSS. Pass `False` when the page already has the
        Bootstrap dependency, whose CSS bundles Shiny's.
    """
    return [require_deps(), jquery_deps(), *shiny_deps(include_css=include_css)]


def shiny_deps(include_css: bool = True) -> list[HTMLDependency]:
    """
    Shiny's own client-side dependencies: `shiny.js`, and the busy indicators.

    Also includes a `shiny-devmode` dependency, which sets
    `window.__SHINY_DEV_MODE__`, when the `SHINY_DEV_MODE` environment variable is
    `"1"`.

    Parameters
    ----------
    include_css
        Whether to include Shiny's CSS. Pass `False` when the page already has the
        Bootstrap dependency, whose CSS bundles Shiny's.
    """
    deps = [
        HTMLDependency(
            name="shiny",
            version=__version__,
            source={"package": "shiny", "subdir": "www/shared/"},
            script={"src": "shiny.js"},
            # This CSS is now rendered against default Bootstrap
            stylesheet={"href": "shiny.min.css"} if include_css else None,
        ),
        busy_indicators_dep(),
    ]

    if os.getenv("SHINY_DEV_MODE") == "1":
        deps.append(
            HTMLDependency(
                "shiny-devmode",
                version=__version__,
                head="<script>window.__SHINY_DEV_MODE__ = true;</script>",
            )
        )

    # NOTE: upstream Shiny ships `www/shared/shiny-testmode.js`, a
    # `postMessage` -> `eval` bridge for injecting JS into an app from a parent
    # frame (legacy R `shinytest`). py-shiny does not use or ship it -- test mode
    # is driven via Playwright over the Chrome DevTools Protocol
    # (`page.evaluate`), so the bridge is unnecessary. It is deleted during
    # vendoring (see `scripts/htmlDependencies.R`) and deliberately not registered
    # here. If a non-CDP consumer ever needs it, restore and register it strictly
    # gated behind test mode (e.g. `get_current_session().app._test_mode`).

    return deps


def jquery_deps() -> HTMLDependency:
    """
    jQuery, which `shiny.js` and Bootstrap's JavaScript are both written against.

    Must come before either of them on the page.
    """
    return HTMLDependency(
        name="jquery",
        version="3.6.0",
        source={"package": "shiny", "subdir": "www/shared/jquery/"},
        script={"src": "jquery-3.6.0.min.js"},
    )


def require_deps() -> HTMLDependency:
    """
    Requirejs, which must load before every other script on the page.

    Shiny doesn't (currently) use requirejs directly, but it does include it because a
    custom requirejs setup is needed to get `HTMLDependency()`s (i.e., loading JS via
    `<script>` tags) to be usable. At the moment, we're just setting
    `window.define.amd=false` after loading requirejs so that the typical UMD pattern
    won't result in an anonymous `define()` error. That only works if this loads first.

    * <https://requirejs.org/docs/errors.html#mismatch>
    * <https://github.com/umdjs/umd>

    Someday, we may want the same/similar thing in R, but this is definitely more of an
    immediate issue for Python since many Jupyter extensions use requirejs.
    """
    return HTMLDependency(
        name="requirejs",
        version="2.3.6",
        source={"package": "shiny", "subdir": "www/shared/requirejs/"},
        script={"src": "require.min.js"},
    )

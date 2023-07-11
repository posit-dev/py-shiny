__all__ = ("markdown",)

import importlib
import textwrap
import warnings
from typing import Callable, Literal, Optional

from htmltools import HTML

from .._docstring import add_example


@add_example()
def markdown(
    text: str, *, render_func: Optional[Callable[[str], str]] = None, **kwargs: object
) -> HTML:
    """
    Convert a string of markdown to :func:`ui.HTML`.

    Parameters
    ----------
    text
        A string of text containing markdown.
    render_func
        A function (with at least 1 argument) which accepts a string of markdown and
        returns a string of HTML. By default, a customized instance of the
        :class:`MarkdownIt` class (which supports Github-flavored markdown) from the
        ``markdown-it`` package is used.
    **kwargs
        Additional keyword arguments passed to the ``render_func``.

    Returns
    -------
    :
        An :func:`ui.HTML` string of the rendered markdown.

    Note
    ----
    Use :func:`ui.include_markdown` instead if you want to include local images (or
    other files) in the markdown.

    See Also
    --------
    :func:`ui.include_markdown`
    """

    if render_func is None:
        render_func = default_md_renderer()

    html = render_func(textwrap.dedent(text), **kwargs)

    return HTML(html)


# -----------------------------------------------------------------------------
# TODO: someday it might make sense for the default markdown parser to have support for
# more stuff like syntax highlighting, mathjax, etc., but two things aren't yet entirely
# clear to me:
#   1. Whether it makes more sense to use Quarto or MyST-Parser.
#   2. How to discover and properly include the relevant HTML dependencies
# -----------------------------------------------------------------------------


def default_md_renderer(
    preset: Literal["commonmark", "gfm"] = "gfm"
) -> Callable[[str], str]:
    try:
        from markdown_it.main import MarkdownIt
    except ModuleNotFoundError:
        raise ModuleNotFoundError(
            "The default markdown parser requires the markdown-it-py package"
            " to be installed. Install it with `pip install markdown-it`."
        )

    if preset == "commonmark":
        parser = MarkdownIt("commonmark")
    else:
        try:
            importlib.import_module(name=".", package="linkify_it")
        except ModuleNotFoundError:
            warnings.warn(
                "The 'autolinking' feature of GitHub flavored markdown requires the "
                "linkify-it package. Install it with `pip install linkify-it`.",
                stacklevel=2,
            )
        # Inspired by MyST-Parser's gfm-only option
        # https://github.com/executablebooks/MyST-Parser/blob/ce1245b25/myst_parser/main.py#L257-L269
        parser = MarkdownIt("commonmark", {"linkify": True})
        parser.enable(["table", "linkify", "strikethrough"])

        try:
            from mdit_py_plugins.tasklists import tasklists_plugin

            parser.use(tasklists_plugin)  # type: ignore
        except ModuleNotFoundError:
            warnings.warn(
                "The 'tasklists' feature of GitHub flavored markdown requires the "
                "mdit_py_plugins package. Install it with `pip install mdit_py_plugins`.",
                stacklevel=2,
            )

    def _render(text: str) -> str:
        return parser.render(text)  # type: ignore

    return _render

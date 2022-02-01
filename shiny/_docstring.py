import os
import inspect
from textwrap import dedent, fill
from typing import Callable, Dict, Optional, Any, List, TypeVar
from warnings import warn

ex_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "examples")


FuncType = Callable[..., Any]
F = TypeVar("F", bound=FuncType)


def doc(
    description: str,
    parameters: Optional[Dict[str, str]] = None,
    returns: Optional[str] = None,
    note: Optional[str] = None,
    topics: Optional[Dict[str, str]] = None,
    see_also: Optional[List[str]] = None,
) -> Callable[[F], F]:
    def _(func: F) -> F:
        docstring: str = description

        params = _get_params(func, parameters or {})
        if params:
            docstring += f"\n{_format_params(params)}"

        if returns:
            docstring += f"\n:return: {returns}"

        # Supported in both ReST and numpydoc
        # https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html#directive-note
        # https://numpydoc.readthedocs.io/en/latest/format.html#notes
        if note:
            docstring += f"\n\n.. note::\n\n{indent(note)}"

        # https://docutils.sourceforge.io/docs/ref/rst/directives.html#generic-admonition
        if topics:
            for k, v in topics.items():
                docstring += f"\n\n.. admonition:: {k}\n\n{indent(v)}"

        # The inline form of seealso should work fine so long as we're not
        # looking to include descriptions.
        # https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html#directive-seealso
        if see_also:
            docstring += f"\n\n.. seealso:: {' '.join(see_also)}"

        # https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html#rst-literal-blocks
        fn_name = func.__name__
        example_file = os.path.join(ex_dir, fn_name, "app.py")
        if os.path.exists(example_file):
            with open(example_file) as f:
                example = f.read()
            example = indent(example, 4)
            docstring += f"\n\n.. code-block:: python\n\n{example}"

        if func.__doc__:
            warn("Overwriting existing docstring for " + fn_name)

        func.__doc__ = docstring
        return func

    return _


def _get_params(func: Callable[[], Any], parameters: Dict[str, str]) -> Dict[str, str]:
    param_names = list(inspect.signature(func).parameters.keys())
    param_desc: List[str] = []
    for nm in param_names:
        desc = parameters.get(nm, PARAMS_DICT.get(nm, None))
        if desc:
            param_desc.append(desc)
        elif nm == "self":
            param_desc.append("The object instance")
        else:
            raise ValueError(f"No description for parameter {nm} in {func.__name__}")
    return dict(zip(param_names, param_desc))


# https://pypi.org/project/sphinx-autodoc-typehints/
def _format_params(params: Dict[str, str]) -> str:
    result: str = ""
    for nm, desc in params.items():
        result += f"\n:param {nm}: {_format_desc(desc)}"
    return result


def _format_desc(x: str) -> str:
    return fill(dedent(x), width=80, subsequent_indent=" " * 4)


def indent(text: str, n: int = 4) -> str:
    return "\n".join(" " * n + line for line in text.split("\n"))


PARAMS_DICT: Dict[str, str] = {
    "id": "An input id.",
    "label": "An input label.",
    "icon": "An icon to appear inline with the button/link.",
    "session": """
      The :class:`~shiny.Session` object passed to the server function of a
      :func:`~shiny.App()`.
    """,
    "value": "Initial value.",
    "selected": "The values that should be initially selected, if any.",
    "inline": "If `True`, the result is displayed inline",
    "choices": """
      Either a list of choices or a dictionary mapping choice values to labels. Note
      that if a dictionary is provided, the keys are used as the (input) values so that
      the dictionary values can hold HTML labels. For :func:`~shiny.ui.input_select`/
      :func:`~shiny.ui.input_selectize`, a dictionary of dictionaries are also supported,
      and in that case, the top-level keys are treated as ``<optgroup>`` labels.
    """,
    "placeholder": "The placeholder of the input.",
    "min": "The minimum allowed value.",
    "max": "The maximum allowed value.",
    "start": """
      The initial start date. Either a :func:`~datetime.date()` object, or a string in
      yyyy-mm-dd format. If `None` (the default), will use the current date in the
      client's time zone.
    """,
    "end": """
      The initial end date. Either a :func:`~datetime.date()` object, or a string in
      yyyy-mm-dd format. If `None` (the default), will use the current date in the
      client's time zone.
    """,
    "step": "Interval to use when stepping between min and max.",
    "time_format": """
      Only used if the slider values are :func:`~datetime.date()` or
      :func:`~datetime.datetime()` objects. A time format string, to be passed to the
      Javascript strftime library. See https://github.com/samsonjs/strftime for more
      details. For Dates, the default is "%F" (like "2015-07-01"), and for Datetimes,
      the default is "%F %T" (like "2015-07-01 15:32:10").
    """,
    "timezone": """
      Only used if the values are :func:`~datetime.datetime()` objects. A string
      specifying the time zone offset for the displayed times, in the format "+HHMM" or
      "-HHMM". If `None` (the default), times will be displayed in the browser's time
      zone. The value "+0000" will result in UTC time.
    """,
    "width": "The CSS width, e.g. '400px', or '100%'",
    "height": "The CSS height, e.g. '100%' or '600px'",
    "container": "A Callable that returns the output container.",
}

PARAMS_DICT = {k: dedent(v) for k, v in PARAMS_DICT.items()}

# Needed for types imported only during TYPE_CHECKING with Python 3.7 - 3.9
# See https://www.python.org/dev/peps/pep-0655/#usage-in-python-3-11
from __future__ import annotations

from typing import Literal, overload

from shiny import App, Inputs, Outputs, Session, ui
from shiny.render import TransformerMetadata, ValueFnAsync, output_transformer

#######
# Package authors can create their own renderer methods by leveraging
# `renderer_components` helper method
#
# This example is kept simple for demonstration purposes, but the handler function supplied to
# `renderer_components` can be much more complex (e.g. shiny.render.plotly)
#######


# Create renderer components from the async handler function: `capitalize_components()`
@output_transformer
async def capitalize_components(
    # Contains information about the render call: `name`, `session`, `is_async`
    _meta: TransformerMetadata,
    # An async form of the app-supplied render function
    _fn: ValueFnAsync[str | None],
    *,
    # Extra parameters that app authors can supply (e.g. `render_capitalize(to="upper")`)
    to: Literal["upper", "lower"] = "upper",
) -> str | None:
    # Get the value
    value = await _fn()
    # Quit early if value is `None`
    if value is None:
        return None

    if to == "upper":
        return value.upper()
    if to == "lower":
        return value.lower()
    raise ValueError(f"Invalid value for `to`: {to}")


# First, create an overload where users can supply the extra parameters.
# Example of usage:
# ```
# @output
# @render_capitalize(to="upper")
# def value():
#     return input.caption()
# ```
# Note: Return type is `type_decorator`
@overload
def render_capitalize(
    *,
    to: Literal["upper", "lower"] = "upper",
) -> capitalize_components.OutputRendererDecorator:
    ...


# Second, create an overload where users are not using parenthesis to the method.
# While it doesn't look necessary, it is needed for the type checker.
# Example of usage:
# ```
# @output
# @render_capitalize
# def value():
#     return input.caption()
# ```
# Note: `_fn` type is `type_renderer_fn`
# Note: Return type is `type_renderer`
@overload
def render_capitalize(
    _fn: capitalize_components.ValueFn,
) -> capitalize_components.OutputRenderer:
    ...


# Lastly, implement the renderer.
# Note: `_fn` type is `type_impl_fn`
# Note: Return type is `type_impl`
def render_capitalize(
    _fn: capitalize_components.ValueFnOrNone = None,
    *,
    to: Literal["upper", "lower"] = "upper",
) -> capitalize_components.OutputRendererOrDecorator:
    return capitalize_components.impl(
        _fn,
        capitalize_components.params(to=to),
    )


#######
# End of package author code
#######

app_ui = ui.page_fluid(
    ui.h1("Capitalization renderer"),
    ui.input_text("caption", "Caption:", "Data summary"),
    "No parenthesis:",
    ui.output_text_verbatim("no_parens"),
    "To upper:",
    ui.output_text_verbatim("to_upper"),
    "To lower:",
    ui.output_text_verbatim("to_lower"),
)


def server(input: Inputs, output: Outputs, session: Session):
    @output
    @render_capitalize
    def no_parens():
        return input.caption()

    @output
    @render_capitalize(to="upper")
    def to_upper():
        return input.caption()

    @output
    @render_capitalize(to="lower")
    def to_lower():
        return input.caption()


app = App(app_ui, server)

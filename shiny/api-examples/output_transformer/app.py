from __future__ import annotations

from typing import Literal, overload

from shiny import App, Inputs, Outputs, Session, ui
from shiny.render.transformer import TransformerMetadata, ValueFn, output_transformer
from shiny.render.transformer._transformer import (
    output_transformer_no_params,
    output_transformer_params,
    output_transformer_simple,
)

#######
# Package authors can create their own output transformer methods by leveraging
# `output_transformer` decorator.
#
# The transformer is kept simple for demonstration purposes, but it can be much more
# complex (e.g. shiny.render.plotly)
#######


@output_transformer_simple()
def render_caps_simple(
    value: str,
) -> str:
    """
    Barret - Render Caps docs (simple)
    """
    # return [value.upper(), value.lower()]
    return value.upper()


@output_transformer_simple()
def render_caps_simple2(
    value: str,
) -> str:
    """
    Barret - Render Caps docs (simple2)
    """
    # return [value.upper(), value.lower()]
    return value.upper()


@output_transformer_params()
async def render_caps(
    # Contains information about the render call: `name` and `session`
    _meta: TransformerMetadata,
    # The app-supplied output value function
    _fn: ValueFn[str | None],
) -> str | None:
    """
    Barret - Render Caps docs no params
    """
    # Get the value
    value = await _fn()

    # Render nothing if `value` is `None`
    if value is None:
        return None

    return value.upper()


@output_transformer_params()
async def render_caps_params(
    # Contains information about the render call: `name` and `session`
    _meta: TransformerMetadata,
    # The app-supplied output value function
    _fn: ValueFn[str | None],
    *,
    to: Literal["upper", "lower"] = "upper",
) -> str | None:
    """
    Barret - Render Caps docs params
    """
    # Get the value
    value = await _fn()

    # Render nothing if `value` is `None`
    if value is None:
        return None

    if to == "upper":
        return value.upper()
    if to == "lower":
        return value.lower()
    raise ValueError(f"Invalid value for `to`: {to}")


# Create renderer components from the async handler function: `capitalize_components()`
@output_transformer()
async def CapitalizeTransformer(
    # Contains information about the render call: `name` and `session`
    _meta: TransformerMetadata,
    # The app-supplied output value function
    _fn: ValueFn[str | None],
    *,
    # Extra parameters that app authors can supply to the render decorator
    # (e.g. `@render_capitalize(to="upper")`)
    to: Literal["upper", "lower"] = "upper",
) -> str | None:
    # Get the value
    value = await _fn()

    # Render nothing if `value` is `None`
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
# Note: Return type is `OutputRendererDecorator`
@overload
def render_capitalize(
    *,
    to: Literal["upper", "lower"] = "upper",
) -> CapitalizeTransformer.OutputRendererDecorator:
    ...


# Second, create an overload where users are not using parentheses to the method.
# While it doesn't look necessary, it is needed for the type checker.
# Example of usage:
# ```
# @output
# @render_capitalize
# def value():
#     return input.caption()
# ```
# Note: `_fn` type is the transformer's `ValueFn`
# Note: Return type is the transformer's `OutputRenderer`
@overload
def render_capitalize(
    _fn: CapitalizeTransformer.ValueFn,
) -> CapitalizeTransformer.OutputRenderer:
    ...


# Lastly, implement the renderer.
# Note: `_fn` type is the transformer's `ValueFn` or `None`
# Note: Return type is the transformer's `OutputRenderer` or `OutputRendererDecorator`
def render_capitalize(
    _fn: CapitalizeTransformer.ValueFn | None = None,
    *,
    to: Literal["upper", "lower"] = "upper",
) -> (
    CapitalizeTransformer.OutputRenderer | CapitalizeTransformer.OutputRendererDecorator
):
    """
    OldSchool - CapitalizeTransformer
    """
    return CapitalizeTransformer(
        _fn,
        CapitalizeTransformer.params(to=to),
    )


#######
# End of package author code
#######

app_ui = ui.page_fluid(
    ui.h1("Capitalization renderer"),
    ui.input_text("caption", "Caption:", "Data summary"),
    "Renderer called with out parentheses:",
    ui.output_text_verbatim("no_parens"),
    "To upper:",
    ui.output_text_verbatim("to_upper"),
    "To lower:",
    ui.output_text_verbatim("to_lower"),
    "barret_caps:",
    ui.output_text_verbatim("barret_caps"),
    "barret_caps_simple:",
    ui.output_text_verbatim("barret_caps_simple"),
    "barret_caps_simple2:",
    ui.output_text_verbatim("barret_caps_simple2"),
    "barret_caps_params:",
    ui.output_text_verbatim("barret_caps_params"),
)


def server(input: Inputs, output: Outputs, session: Session):
    @output
    # Called without parentheses
    @render_capitalize
    def no_parens():
        return input.caption()

    @output
    # Called with parentheses. Equivalent to `@render_capitalize()`
    @render_capitalize(to="upper")
    def to_upper():
        return input.caption()

    @output
    @render_capitalize(to="lower")
    # Works with async output value functions
    async def to_lower():
        return input.caption()

    @render_caps()
    def barret_caps():
        return input.caption()

    @render_caps_simple
    def barret_caps_simple():
        return input.caption()

    @render_caps_simple2
    def barret_caps_simple2():
        return input.caption()

    @render_caps_params
    def barret_caps_params():
        return input.caption()

    @render_caps_params(to="upper")
    def barret_caps_params2():
        return input.caption()


app = App(app_ui, server)

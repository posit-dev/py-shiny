# pyright : basic
from __future__ import annotations

from typing import Literal, overload

from shiny import App, Inputs, Outputs, Session, ui
from shiny.render.transformer import (
    TransformerMetadata,
    ValueFn,
    ValueFnApp,
    output_transformer,
)
from shiny.render.transformer._transformer import (
    BarretRenderer,
    BarretSimple,
    JSONifiable,
    output_transformer_json,
    output_transformer_json2,
    output_transformer_no_params,
    output_transformer_params,
    output_transformer_simple,
)

# # # Goals
# # Simple-ish interface for component author
# # Component author only needs to implement one async function
# # For user, support parens and no parens
# # For user, support async and sync usage
# # Support docstrings with pyright for parens and no parens
# # Support docstrings for quartodoc

# # 0. Rename OutputRenderer to `OutputRendererLegacy` (or something)
# # 1. OutputRenderer becomes a protocol
# # PErform a runtime isinstance check on the class
# # Or runtime check for attribute callable field of `_set_metadata()`
# # 2. Don't use `P` within `OutputRenderer` base class. Instead, use `self.FOO` params within the child class / child render method
# # Only use Barret Renderer class and have users overwrite the transform or render method as they see fit.

# class json(BarretSimple[object, jsonifiable]):
#     def __init__(self, _value_fn: Callable[[], object]):
#         super().__init__(_value_fn)

#     async def transform(self, value: object) -> jsonifiable:
#         return json.parse(json.dumps(value))

# class json(BarretRenderer[jsonifiable, str]):
#     default_ui = output_json
#     """
#     Docs! - no params
#     """

#     def __init__(self, _value_fn: Callable[[], jsonifiable], *, indent: int = 0):
#         """
#         Docs! - params
#         """
#         super().__init__(_value_fn)
#         self.indent = indent

#     async def render(self) -> str:
#         value = await self._value_fn()
#         if value is None:
#             return None
#         return await self.transform(value)


# @overload
# def __init__(self, *, a: int = 1) -> None:
#     ...


# @overload
# def __init__(self, _fn: ValueFn[str | None]) -> None:
#     ...
class sub_barret_renderer(BarretRenderer[str | None, JSONifiable]):
    """
    SubBarretSimple - class docs - Render Caps docs
    """

    # a: int
    default_ui = ui.output_text_verbatim
    # default_ui_passthrough_args = None

    def __init__(
        self,
        # Required for no paren usage
        _fn: ValueFnApp[str | None] | None = None,
        *,
        a: int = 1,
        placeholder: bool = True,
    ) -> None:
        """
        SubBarretSimple - init docs - Render Caps docs
        """
        # Do not pass params
        super().__init__(_fn)
        self.widget = None
        self.a: int = a
        # self.default_ui = lambda(id): ui.output_text_verbatim(id, placeholder=placeholder)
        self.default_ui = ui.output_text_verbatim

    async def render(self) -> str | None:
        value = await self._value_fn()
        values = [value, value, value]
        [x for x in values if isinstance(x, Sidebar)]
        if value is None:
            return None
        self.widget = value
        # self.a
        return f"{value.upper()}; a={self.a}"


from typing import Any, Awaitable, Callable, Generic

from shiny.render.transformer._transformer import IT, OT

# class BarretWrap(BarretSimple[IT, OT]):
#     """
#     BarretWrap - Render Caps docs
#     """

#     a: int

#     # @overload
#     # def __init__(self, *, a: int = 1) -> None:
#     #     ...

#     # @overload
#     # def __init__(self, _fn: ValueFn[str | None]) -> None:
#     #     ...

#     # Add default_ui?
#     def __init__(self, transform_fn: Callable[[IT], Awaitable[OT]]) -> None:
#         super().__init__()
#         self._transform_fn = transform_fn

#     async def render(self) -> OT | None:
#         """
#         BarretWrap - render docs here
#         """
#         print("BarretSimple - render")
#         value = await self._value_fn()
#         if value is None:
#             return None

#         rendered = await self.transform(value)
#         return rendered

# from typing import Sequence
# def length(value: Sequence[IT]) -> int:
#     return len(value)


# def simple_fn(
#     transform_fn: Callable[[IT], Awaitable[OT]],
#     # *,
#     # ignore: IT | None = None,
#     # ignore2: OT | None = None,
# ):
#     bs = BarretSimple[IT, OT]()

#     async def transform_(value: IT) -> OT:
#         return await transform_fn(value)

#     bs.transform = transform_
#     # bs is set up

#     @overload
#     def _(_fn: None = None) -> Callable[[ValueFnApp[IT]], BarretSimple[IT, OT]]:
#         ...

#     @overload
#     def _(_fn: ValueFnApp[IT]) -> BarretSimple[IT, OT]:
#         ...

#     def _(
#         _fn: ValueFnApp[IT] | None = None,
#     ) -> BarretSimple[IT, OT] | Callable[[ValueFnApp[IT]], BarretSimple[IT, OT]]:
#         if callable(_fn):
#             bs(_fn)
#         return bs

#     return _


# return ret


# @simple_fn
# async def barret_simple_fn(value: str) -> str:
#     """
#     Barret - Simple function docs
#     """
#     return value.upper()


class sub_barret_simple(BarretRenderer[str, str]):
    """
    SubBarretSimple - class - Render Caps docs
    """

    default_ui = ui.output_text_verbatim

    def __init__(
        self,
        _value_fn: ValueFnApp[str] | None = None,
    ):
        """
        SubBarretSimple - init - docs here
        """
        super().__init__()  # TODO-barret; pass through _value_fn

    async def transform(self, value: str) -> str:
        return str(value).upper()

    # async def render(self) -> str:
    #     # OPen graphics
    #     value = await self._value_fn()
    #     # close graphics
    #     # self.a
    #     return (
    #         f"{value.upper()}, {self._params.args}, {self._params.kwargs}; a={self.a}"
    #     )


#######
# Package authors can create their own output transformer methods by leveraging
# `output_transformer` decorator.
#
# The transformer is kept simple for demonstration purposes, but it can be much more
# complex (e.g. shiny.render.plotly)
#######


# @output_transformer_json2()
# def render_caps_simple(
#     value: str,
# ) -> str:
#     """
#     Barret - Render Caps docs (simple)
#     """
#     # return [value.upper(), value.lower()]
#     return value.upper()


@output_transformer_params(default_ui=ui.output_text_verbatim)
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

    # _meta.self.widget = value  # pyright: ignore

    # Render nothing if `value` is `None`
    if value is None:
        return None

    if to == "upper":
        return value.upper()
    if to == "lower":
        return value.lower()
    raise ValueError(f"Invalid value for `to`: {to}")


# @output_transformer_params()
# async def render_caps_no_params(
#     # Contains information about the render call: `name` and `session`
#     _meta: TransformerMetadata,
#     # The app-supplied output value function
#     _fn: ValueFn[str | None],
# ) -> str | None:
#     """
#     Barret - Render Caps docs no parameters
#     """
#     # Get the value
#     value = await _fn()

#     # Render nothing if `value` is `None`
#     if value is None:
#         return None

#     return value.upper()


# # Create renderer components from the async handler function: `capitalize_components()`
# @output_transformer()
# async def CapitalizeTransformer(
#     # Contains information about the render call: `name` and `session`
#     _meta: TransformerMetadata,
#     # The app-supplied output value function
#     _fn: ValueFn[str | None],
#     *,
#     # Extra parameters that app authors can supply to the render decorator
#     # (e.g. `@render_capitalize(to="upper")`)
#     to: Literal["upper", "lower"] = "upper",
# ) -> str | None:
#     # Get the value
#     value = await _fn()

#     # Render nothing if `value` is `None`
#     if value is None:
#         return None

#     if to == "upper":
#         return value.upper()
#     if to == "lower":
#         return value.lower()
#     raise ValueError(f"Invalid value for `to`: {to}")


# # First, create an overload where users can supply the extra parameters.
# # Example of usage:
# # ```
# # @output
# # @render_capitalize(to="upper")
# # def value():
# #     return input.caption()
# # ```
# # Note: Return type is `OutputRendererDecorator`
# @overload
# def render_capitalize(
#     *,
#     to: Literal["upper", "lower"] = "upper",
# ) -> CapitalizeTransformer.OutputRendererDecorator:
#     ...


# # Second, create an overload where users are not using parentheses to the method.
# # While it doesn't look necessary, it is needed for the type checker.
# # Example of usage:
# # ```
# # @output
# # @render_capitalize
# # def value():
# #     return input.caption()
# # ```
# # Note: `_fn` type is the transformer's `ValueFn`
# # Note: Return type is the transformer's `OutputRenderer`
# @overload
# def render_capitalize(
#     _fn: CapitalizeTransformer.ValueFn,
# ) -> CapitalizeTransformer.OutputRenderer:
#     ...


# # Lastly, implement the renderer.
# # Note: `_fn` type is the transformer's `ValueFn` or `None`
# # Note: Return type is the transformer's `OutputRenderer` or `OutputRendererDecorator`
# def render_capitalize(
#     _fn: CapitalizeTransformer.ValueFn | None = None,
#     *,
#     to: Literal["upper", "lower"] = "upper",
# ) -> (
#     CapitalizeTransformer.OutputRenderer | CapitalizeTransformer.OutputRendererDecorator
# ):
#     """
#     OldSchool - CapitalizeTransformer
#     """
#     return CapitalizeTransformer(
#         _fn,
#         CapitalizeTransformer.params(to=to),
#     )


#######
# End of package author code
#######


def text_row(id: str):
    return ui.tags.tr(
        ui.tags.td(f"{id}:"),
        ui.tags.td(ui.output_text_verbatim(id, placeholder=True)),
    )
    return ui.row(
        ui.column(6, f"{id}:"),
        ui.column(6, ui.output_text_verbatim(id, placeholder=True)),
    )


app_ui = ui.page_fluid(
    ui.h1("Capitalization renderer"),
    ui.input_text("caption", "Caption:", "Data summary"),
    #
    ui.tags.table(
        text_row("old_no_paren"),
        text_row("old_paren"),
        #
        text_row("barret_caps_simple_no_paren"),
        text_row("barret_caps_simple_paren"),
        #
        text_row("barret_caps_params_no_paren"),
        text_row("barret_caps_params_paren"),
        #
        text_row("barret_caps_no_params_no_paren"),
        text_row("barret_caps_no_params_paren"),
        #
        text_row("barret_sub_simple_no_paren"),
        text_row("barret_sub_simple_paren"),
        #
        text_row("barret_sub_renderer_no_paren"),
        text_row("barret_sub_renderer_paren"),
    ),
)

# import dominate.tags as dom_tags

# dom_tags.h1("content")


# @dom_tags.h1
# def _():
#     return "content"


def server(input: Inputs, output: Outputs, session: Session):
    # @output
    # # Called without parentheses
    # @render_capitalize
    # def old_no_paren():
    #     return input.caption()

    # @output
    # # Called with parentheses. Equivalent to `@render_capitalize()`
    # # legacy - Barret - Too much boilerplate
    # @render_capitalize(to="lower")
    # def old_paren():
    #     return input.caption()

    # # No docstring due to overload
    # @render_caps_simple
    # def barret_caps_simple_no_paren():
    #     return input.caption()

    # # No docstring due to overload
    # @render_caps_simple()
    # def barret_caps_simple_paren():
    #     return input.caption()

    # TODO-barret; Double check this one!!!!
    # Barret - Only downside is bad function name in pylance window. Could be pylance bug?
    @render_caps_params
    def barret_caps_params_no_paren():
        return input.caption()

    # Barret - Correct function name
    @render_caps_params(to="lower")
    def barret_caps_params_paren():
        return input.caption()

    # @render_caps_no_params
    # # TODO-barret; Double check this one!!!!
    # # Barret - Only downside is bad function name in pylance window. Could be pylance bug?
    # def barret_caps_no_params_no_paren():
    #     return input.caption()

    # # Barret - Correct function name!
    # @render_caps_no_params()
    # def barret_caps_no_params_paren():
    #     return input.caption()

    # print("\nsub_barret_simple")

    # new (<function server.<locals>.barret_sub at 0x104bd56c0>,) {}
    # creating decorator!
    @sub_barret_simple
    def barret_sub_simple_no_paren():
        return input.caption()

    print("\nbarret_sub_simple_paren")

    # new () {}
    # init () {}
    # call (<function server.<locals>.barret_sub2 at 0x106146520>,) {}
    @sub_barret_simple()
    def barret_sub_simple_paren() -> str:
        return input.caption()

    print("\nbarret_sub_renderer_no_paren")

    # @barret_simple_fn
    # def barret_simple_fn_no_paren():
    #     return input.caption()

    print("\nbarret_sub_simple_paren")

    # # new () {}
    # # init () {}
    # # call (<function server.<locals>.barret_sub2 at 0x106146520>,) {}
    # @barret_simple_fn()
    # def barret_simple_fn_paren() -> str:
    #     return input.caption()

    print("\nbarret_sub_renderer_no_paren")

    # new () {'a': 1}
    # init () {'a': 1}
    # call (<function server.<locals>.barret_sub2 at 0x106146520>,) {}
    @sub_barret_renderer
    def barret_sub_renderer_no_paren():
        return input.caption()

    print("\nbarret_sub_renderer_paren")

    # new () {'a': 1}
    # init () {'a': 1}
    # call (<function server.<locals>.barret_sub2 at 0x106146520>,) {}
    @sub_barret_renderer(a=2)
    def barret_sub_renderer_paren():
        return input.caption()

    print("\n")


app = App(app_ui, server)

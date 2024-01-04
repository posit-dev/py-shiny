# pyright : basic
from __future__ import annotations

from shiny import App, Inputs, Outputs, Session, ui
from shiny.render.renderer import Renderer, ValueFn

# TODO-barret Update app with docs below


class sub_barret_renderer(Renderer[str]):
    """
    SubBarretSimple - class docs - Render Caps docs
    """

    def default_ui(self, id: str):
        return ui.output_text_verbatim(id, placeholder=self.placeholder)

    def __init__(
        self,
        # Required for no paren usage
        _fn: ValueFn[str | None] | None = None,
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
        self.default_ui = ui.output_text_verbatim

    async def render(self) -> str | None:
        value = await self._value_fn()
        if value is None:
            return None
        self.widget = value
        return f"{value.upper()}; a={self.a}"


class sub_barret_simple(Renderer[str]):
    """
    SubBarretSimple - class - Render Caps docs
    """

    def default_ui(self, id: str):
        return ui.output_text_verbatim(id, placeholder=True)

    def __init__(
        self,
        _value_fn: ValueFn[str] | None = None,
    ):
        """
        SubBarretSimple - init - docs here
        """
        super().__init__(_value_fn)

    async def transform(self, value: str) -> str:
        return str(value).upper()


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
    ui.tags.table(
        text_row("barret_sub_simple_no_paren"),
        text_row("barret_sub_simple_paren"),
        #
        text_row("barret_sub_renderer_no_paren"),
        text_row("barret_sub_renderer_paren"),
    ),
)


def server(input: Inputs, output: Outputs, session: Session):
    @sub_barret_simple
    def barret_sub_simple_no_paren():
        return input.caption()

    @sub_barret_simple()
    def barret_sub_simple_paren() -> str:
        return input.caption()

    @sub_barret_renderer
    def barret_sub_renderer_no_paren():
        return input.caption()

    @sub_barret_renderer(a=2)
    def barret_sub_renderer_paren():
        return input.caption()


app = App(app_ui, server)

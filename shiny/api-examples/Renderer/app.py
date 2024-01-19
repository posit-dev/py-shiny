from __future__ import annotations

from typing import Literal, Optional

from shiny import App, Inputs, Outputs, Session, ui
from shiny.render.renderer import Renderer, ValueFn

#######
# Start of package author code
#######


class render_capitalize(Renderer[str]):
    # The documentation for the class will be displayed when the user hovers over the
    # decorator when **no** parenthesis are used. Ex: `@render_capitalize`
    # If no documentation is supplied to the `__init__()` method, then this
    # documentation will be displayed when parenthesis are used on the decorator.
    """
    Render capitalize class documentation goes here.
    """

    to_case: Literal["upper", "lower", "ignore"]
    """
    The case to render the value in.
    """
    placeholder: bool
    """
    Whether to render a placeholder value. (Defaults to `True`)
    """

    def auto_output_ui(self):
        """
        Express UI for the renderer
        """
        return ui.output_text_verbatim(self.output_name, placeholder=self.placeholder)

    def __init__(
        self,
        _fn: Optional[ValueFn[str]] = None,
        *,
        to_case: Literal["upper", "lower", "ignore"] = "upper",
        placeholder: bool = True,
    ) -> None:
        # If a different set of documentation is supplied to the `__init__` method,
        # then this documentation will be displayed when parenthesis are used on the decorator.
        # Ex: `@render_capitalize()`
        """
        Render capitalize documentation goes here.

        It is a good idea to talk about parameters here!

        Parameters
        ----------
        to_case
            The case to render the value. (`"upper"`)

            Options:
            - `"upper"`: Render the value in upper case.
            - `"lower"`: Render the value in lower case.
            - `"ignore"`: Do not alter the case of the value.

        placeholder
            Whether to render a placeholder value. (`True`)
        """
        # Do not pass params
        super().__init__(_fn)
        self.to_case = to_case

    async def render(self) -> str | None:
        value = await self.fn()
        if value is None:
            # If `None` is returned, then do not render anything.
            return None

        ret = str(value)
        if self.to_case == "upper":
            return ret.upper()
        if self.to_case == "lower":
            return ret.lower()
        if self.to_case == "ignore":
            return ret
        raise ValueError(f"Invalid value for `to_case`: {self.to_case}")


class render_upper(Renderer[str]):
    """
    Minimal capitalize string transformation renderer.

    No parameters are supplied to this renderer. This allows us to skip the `__init__()`
    method and `__init__()` documentation. If you hover over this decorator with and
    without parenthesis, you will see this documentation in both situations.

    Note: This renderer is equivalent to `render_capitalize(to="upper")`.
    """

    def auto_output_ui(self):
        """
        Express UI for the renderer
        """
        return ui.output_text_verbatim(self.output_name, placeholder=True)

    async def transform(self, value: str) -> str:
        """
        Transform the value to upper case.

        This method is shorthand for the default `render()` method. It is useful to
        transform non-`None` values. (Any `None` value returned by the app author will
        be forwarded to the browser.)

        Parameters
        ----------
        value
            The a non-`None` value to transform.

        Returns
        -------
        str
            The transformed value. (Must be a subset of `Jsonifiable`.)
        """

        return str(value).upper()


#######
# End of package author code
#######


#######
# Start of app author code
#######


def text_row(id: str, label: str):
    return ui.tags.tr(
        ui.tags.td(f"{label}:"),
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
        text_row("upper", "@render_upper"),
        text_row("upper_with_paren", "@render_upper()"),
        #
        text_row("cap_upper", "@render_capitalize"),
        text_row("cap_lower", "@render_capitalize(to='lower')"),
    ),
)


def server(input: Inputs, output: Outputs, session: Session):
    # Hovering over `@render_upper` will display the class documentation
    @render_upper
    def upper():
        return input.caption()

    # Hovering over `@render_upper` will display the class documentation as there is no
    # `__init__()` documentation
    @render_upper()
    def upper_with_paren():
        return input.caption()

    # Hovering over `@render_capitalize` will display the class documentation
    @render_capitalize
    def cap_upper():
        return input.caption()

    # Hovering over `@render_capitalize` will display the `__init__()` documentation
    @render_capitalize(to_case="lower")
    def cap_lower():
        return input.caption()


app = App(app_ui, server)

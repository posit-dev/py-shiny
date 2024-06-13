# pyright: reportUnusedFunction=false

import typing

from shiny import App, Inputs, Outputs, Session, reactive, render, ui

app_ui = ui.page_fluid(
    ui.input_numeric("n", "N", 20),
    ui.input_numeric("n2", "N2", 50),
    ui.input_checkbox("checkbox", "Checkbox", True),
    ui.output_code("txt", placeholder=True),
    ui.output_code("txt2", placeholder=True),
    ui.output_code("txt3", placeholder=True),
)


# By default the type of any input value, like input.n(), is Any, so no type checking
# will be used.
#
# But it is possible to specify the type of the input value, by creating a subclass of
# Inputs. We'll do that for input.n2() and input.checkbox():
class ShinyInputs(Inputs):
    n2: reactive.value[int]
    check: reactive.value[bool]


def server(input: Inputs, output: Outputs, session: Session):
    # Cast `input` to our ShinyInputs class. This just tells the static type checker
    # that we want it treated as a ShinyInputs object for type checking; it has no
    # run-time effect.
    input = typing.cast(ShinyInputs, input)

    # The type checker knows that r() returns an int, which you can see if you hover
    # over it.
    @reactive.calc
    def r():
        if input.n() is None:
            return 0
        return input.n() * 2

    # Because we did NOT add a type for input.n (we did input.n2), the type checker
    # thinks the return type of input.n() is Any, so we don't get type checking here.
    # The function is returning the wrong value here: it returns an int instead of a
    # string, but this error is not flagged.
    @render.code
    async def txt():
        return input.n() * 2

    # In contrast, input.n2() is declared to return an int, so the type check does flag
    # this error -- the `render.code()` is underlined in red.
    @render.code
    async def txt2():
        return input.n2() * 2

    # This is a corrected version of the function above. It returns a string, and is not
    # marked in red.
    @render.code
    async def txt3():
        return str(input.n2() * 2)


app = App(app_ui, server)

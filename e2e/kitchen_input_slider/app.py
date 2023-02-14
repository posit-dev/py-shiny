from e2e.playground import typing
from shiny import *

slider_nums: typing.List[int] = []


def slider_row(
    num: int,
    label: str,
    *,
    min: float = 0,
    max: float = 100,
    value: float = 20,
    step: float = 1,
    animate: bool = False,
    time_format: typing.Optional[str] = None,
):
    slider_nums.append(num)
    return ui.row(
        ui.column(
            6,
            ui.input_slider(
                f"s{num}",
                label,
                min=min,
                max=max,
                value=value,
                step=step,
                animate=animate,
                time_format=time_format,
            ),
        ),
        ui.column(
            6,
            ui.output_text_verbatim(f"txt{num}", placeholder=True),
        ),
    )


app_ui = ui.page_fluid(
    ui.h2("Sliders!"),
    slider_row(1, "regular"),
)


def server(input: Inputs, output: Outputs, session: Session):
    def make_output(num: int):
        name = f"txt{num}"

        @output(id=name)
        @render.text
        def _():
            return input[f"s{num}"]()

    for num in slider_nums:
        make_output(num)
    # TODO-future; Display any type of supported slider, slider range, etc.


app = App(app_ui, server)

import pathlib

import pandas as pd

from shiny import App, Inputs, Outputs, Session, render, ui

dir = pathlib.Path(__file__).parent
mtcars = pd.read_csv(dir / "mtcars.csv")


app_ui = ui.page_fluid(
    ui.input_checkbox("highlight", "Highlight min/max values"),
    ui.output_table("result"),
    # Legend
    ui.panel_conditional(
        "input.highlight",
        ui.panel_absolute(
            "Yellow is maximum, grey is minimum",
            bottom="6px",
            right="6px",
            class_="p-1 bg-light border",
        ),
    ),
    class_="p-3",
)


def server(input: Inputs, output: Outputs, session: Session):
    @output
    @render.table
    def result():
        if not input.highlight():
            # If we're not highlighting values, we can simply
            # return the pandas data frame as-is; @render.table
            # will call .to_html() on it.
            return mtcars
        else:
            # We need to use the pandas Styler API. The default
            # formatting options for Styler are not the same as
            # DataFrame.to_html(), so we set a few options to
            # make them match.
            return (
                mtcars.style.set_table_attributes(
                    'class="dataframe shiny-table table w-auto"'
                )
                .hide(axis="index")
                .format(
                    {
                        "mpg": "{0:0.1f}",
                        "disp": "{0:0.1f}",
                        "drat": "{0:0.2f}",
                        "wt": "{0:0.3f}",
                        "qsec": "{0:0.2f}",
                    }
                )
                .set_table_styles(
                    [dict(selector="th", props=[("text-align", "right")])]
                )
                .highlight_min(color="silver")
                .highlight_max(color="yellow")
            )


app = App(app_ui, server)

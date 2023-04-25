from pathlib import Path

import matplotlib.pyplot as plt

# import shinyswatch
import pandas as pd
import seaborn as sns
from _colors import bg_palette, palette

from shiny import App, Inputs, Outputs, Session, reactive, render, req, ui
from shiny.experimental.ui_x import (
    layout_column_wrap_x,
    layout_sidebar_x,
    page_fillable_x,
    sidebar_x,
    value_box_x,
)

sns.set_theme()

df = pd.read_csv(Path(__file__).parent / "penguins.csv", na_values="NA")
numeric_cols: list[str] = df.select_dtypes(include=["float64"]).columns.tolist()
species: list[str] = df["Species"].unique().tolist()
species.sort()

value_box_height = "100px"

app_ui = page_fillable_x(
    # shinyswatch.theme.minty(),
    layout_sidebar_x(
        sidebar_x(
            ui.input_selectize(
                "xvar",
                "X variable",
                numeric_cols,
                selected="Bill Length (mm)",
            ),
            ui.input_selectize(
                "yvar",
                "Y variable",
                numeric_cols,
                selected="Bill Depth (mm)",
            ),
            ui.input_checkbox_group(
                "species", "Filter by species", species, selected=species
            ),
            ui.hr(),
            ui.input_switch("by_species", "Show species", value=True),
            ui.input_switch("show_margins", "Show marginal plots", value=True),
            # Artwork by @allison_horst
            ui.tags.img(src="penguins.png", width="100%"),
        ),
        ui.output_ui("value_boxes"),
        ui.output_plot("scatter", height=f"calc(100% - {value_box_height})"),
        fill=True,
    ),
)


def server(input: Inputs, output: Outputs, session: Session):
    @reactive.Calc
    def filtered_df() -> pd.DataFrame:
        """Returns a Polars data frame that includes only the desired rows"""

        # This calculation "req"uires that at least one species is selected
        req(len(input.species()) > 0)
        # Filter the rows so we only include the desired species
        return df[df["Species"].isin(input.species())]

    @output
    @render.plot
    def scatter():
        """Generates a plot for Shiny to display to the user"""

        # The plotting function to use depends on whether margins are desired
        plotfunc = sns.jointplot if input.show_margins() else sns.scatterplot

        plotfunc(
            data=filtered_df(),
            x=input.xvar(),
            y=input.yvar(),
            palette=palette,
            hue="Species" if input.by_species() else None,
            hue_order=species,
        )
        if input.by_species():
            plt.legend(loc="lower right")

    @output
    @render.ui
    def value_boxes():
        df = filtered_df()

        def penguin_value_box(title: str, count: int, bgcol: str, showcase=None):
            return value_box_x(
                f"{title}",
                count,
                # ui.h1(HTML("$1 <i>Billion</i> Dollars")),
                # ui.span(
                #     # bsicons::bs_icon("arrow-up"),
                #     # "X",
                #     " 30% VS PREVIOUS 30 DAYS",
                # ),
                # showcase = bsicons::bs_icon("piggy-bank"),
                # showcase=f"{name}!",
                # class_="bg-success",
                showcase=showcase,
                theme_color=None,
                style=f"background-color: {bgcol};",
                height=value_box_height,
                # full_screen=True,
            )

        if not input.by_species():
            return penguin_value_box("Penguins", len(df.index), bg_palette["default"])

        value_boxes = [
            penguin_value_box(
                name,
                len(df[df["Species"] == name]),
                bg_palette[name],
                # Artwork by @allison_horst
                showcase=ui.tags.img(src=f"{name}.png", height="100%"),
            )
            for name in species
        ]

        return layout_column_wrap_x(1 / 3, *value_boxes)


app = App(
    app_ui,
    server,
    static_assets=str(Path(__file__).parent.resolve() / "www"),
)

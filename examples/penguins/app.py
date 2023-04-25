# TODO-future: Add filter of X varaible to reduce the data? (Here we would show "Gentoo" has count 0, rather than remove if no data exists)
# TODO-future: Add brushing to zoom into the plot. The counts should represent the data in the zoomed area. (Single click would zoom out)

from pathlib import Path

# import shinyswatch
import pandas as pd
import seaborn as sns
from _colors import bg_palette, palette

import shiny.experimental as x
from shiny import App, Inputs, Outputs, Session, reactive, render, req, ui

sns.set_theme()

www_dir = Path(__file__).parent.resolve() / "www"

df = pd.read_csv(Path(__file__).parent / "penguins.csv", na_values="NA")
numeric_cols: list[str] = df.select_dtypes(include=["float64"]).columns.tolist()
species: list[str] = df["Species"].unique().tolist()
species.sort()

app_ui = x.ui.page_fillable(
    # shinyswatch.theme.minty(),
    x.ui.layout_sidebar(
        x.ui.sidebar(
            # Artwork by @allison_horst
            ui.tags.img(
                src="palmerpenguins.png", width="80%", class_="mt-0 mb-2 mx-auto"
            ),
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
        ),
        x.ui.card(
            x.ui.card_header("My Title"),
            x.ui.card_image(
                file=str(www_dir / "penguins.png"),
                href="https://github.com/rstudio/shiny",
            ),
            x.ui.card_body(
                "🎶 It's my [body] and I'll [type what] I want to!",
                class_="p-0",
            ),
            x.ui.card_footer(
                "Copyright 2023 Posit, PBC",
                class_="fs-6",
            ),
            height=135,
            fill=False,
            full_screen=True,
        )
        if False
        else None,
        ui.output_ui("value_boxes"),
        # ui.output_text_verbatim("brush"),
        x.ui.output_plot("scatter", fill=True, brush=ui.brush_opts()),
        fill=True,
        fillable=True,
    ),
)


def server(input: Inputs, output: Outputs, session: Session):
    @reactive.Calc
    def filtered_df() -> pd.DataFrame:
        """Returns a Polars data frame that includes only the desired rows"""

        # This calculation "req"uires that at least one species is selected
        req(len(input.species()) > 0)

        if False:
            if "scatter_brush" in input:
                info = input.scatter_brush()
                print(str(info))
            else:
                print("No brush!")

        # Filter the rows so we only include the desired species
        return df[df["Species"].isin(input.species())]

    @output
    @render.text
    def brush():
        return str(input.scatter_brush())

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
            legend=False,
        )

    @output
    @render.ui
    def value_boxes():
        df = filtered_df()

        def penguin_value_box(title: str, count: int, bgcol: str, showcase=None):
            return x.ui.value_box(
                f"{title}",
                count,
                {"class_": "pt-1 pb-0"},
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
                height="90px",
                full_screen=True,
            )

        if not input.by_species():
            return penguin_value_box(
                "Penguins",
                len(df.index),
                bg_palette["default"],
                # Artwork by @allison_horst
                showcase=ui.tags.img(src="penguins.png", width="100%"),
            )

        value_boxes = [
            penguin_value_box(
                name,
                len(df[df["Species"] == name]),
                bg_palette[name],
                # Artwork by @allison_horst
                showcase=ui.tags.img(src=f"{name}.png", height="100%"),
            )
            for name in species
            # Only include boxes for _selected_ species
            if name in input.species()
        ]

        return x.ui.layout_column_wrap(1 / len(value_boxes), *value_boxes)


app = App(
    app_ui,
    server,
    static_assets=str(www_dir),
)

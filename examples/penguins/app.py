# TODO-future: Add filter of X varaible to reduce the data? (Here we would show "Gentoo" has count 0, rather than remove if no data exists)
# TODO-future: Add brushing to zoom into the plot. The counts should represent the data in the zoomed area. (Single click would zoom out)

from pathlib import Path

# import shinyswatch
import pandas as pd
import seaborn as sns
from _colors import bg_palette, palette

from shiny import App, Inputs, Outputs, Session, reactive, render, req, ui
from shiny.experimental.ui_x import (
    card_body_x,
    card_footer_x,
    card_header_x,
    card_image_x,
    card_x,
    layout_column_wrap_x,
    layout_sidebar_x,
    output_plot_x,
    page_fillable_x,
    sidebar_x,
    value_box_x,
)

sns.set_theme()

www_dir = Path(__file__).parent.resolve() / "www"

df = pd.read_csv(Path(__file__).parent / "penguins.csv", na_values="NA")
numeric_cols: list[str] = df.select_dtypes(include=["float64"]).columns.tolist()
species: list[str] = df["Species"].unique().tolist()
species.sort()

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
        card_x(
            card_header_x("My Title"),
            card_image_x(
                file=str(www_dir / "penguins.png"),
                href="https://github.com/rstudio/shiny",
            ),
            card_body_x(
                "🎶 It's my [body] and I'll [type what] I want to!",
                class_="p-0",
            ),
            card_footer_x(
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
        output_plot_x("scatter", fill=True, brush=ui.brush_opts()),
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
                height="100px",
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

        return layout_column_wrap_x(1 / len(value_boxes), *value_boxes)


app = App(
    app_ui,
    server,
    static_assets=str(www_dir),
)

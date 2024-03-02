from pathlib import Path

import pandas as pd
import seaborn as sns

from shiny import reactive
from shiny.express import input, render, ui

sns.set_theme(style="white")
df = pd.read_csv(Path(__file__).parent / "penguins.csv", na_values="NA")
species = ["Adelie", "Gentoo", "Chinstrap"]

ui.page_opts(fillable=True)


def count_species(df, species):
    return df[df["Species"] == species].shape[0]


with ui.sidebar():
    ui.input_slider("mass", "Mass", 2000, 6000, 3400)
    ui.input_checkbox_group("species", "Filter by species", species, selected=species)


@reactive.calc
def filtered_df() -> pd.DataFrame:
    filt_df = df[df["Species"].isin(input.species())]
    filt_df = filt_df.loc[filt_df["Body Mass (g)"] > input.mass()]
    return filt_df


with ui.layout_columns():
    with ui.value_box(theme="primary"):
        "Adelie"

        @render.text
        def adelie_count():
            return count_species(filtered_df(), "Adelie")

    with ui.value_box(theme="primary"):
        "Gentoo"

        @render.text
        def gentoo_count():
            return count_species(filtered_df(), "Gentoo")

    with ui.value_box(theme="primary"):
        "Chinstrap"

        @render.text
        def chinstrap_count():
            return count_species(filtered_df(), "Chinstrap")


with ui.layout_columns():
    with ui.card():
        ui.card_header("Summary statistics")

        @render.data_frame
        def summary_statistics():
            display_df = filtered_df()[
                [
                    "Species",
                    "Island",
                    "Bill Length (mm)",
                    "Bill Depth (mm)",
                    "Body Mass (g)",
                ]
            ]
            return render.DataGrid(display_df, filters=True)

    with ui.card():
        ui.card_header("Penguin bills")

        @render.plot
        def length_depth():
            return sns.scatterplot(
                data=filtered_df(),
                x="Bill Length (mm)",
                y="Bill Depth (mm)",
                hue="Species",
            )

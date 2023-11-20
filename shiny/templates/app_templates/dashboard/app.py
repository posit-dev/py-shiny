from pathlib import Path

import pandas as pd
import seaborn as sns

from shiny import App, Inputs, Outputs, Session, reactive, render, ui

sns.set_theme(style="white")
df = pd.read_csv(Path(__file__).parent / "penguins.csv", na_values="NA")
species = ["Adelie", "Gentoo", "Chinstrap"]


def make_value_box(penguin):
    return ui.value_box(
        title=penguin, value=ui.output_text(f"{penguin}_count".lower()), theme="primary"
    )


app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.input_slider(
            "mass",
            "Mass",
            2000,
            8000,
            3400,
        ),
        ui.input_checkbox_group(
            "species", "Filter by species", species, selected=species
        ),
    ),
    ui.row(
        ui.layout_column_wrap(
            *[make_value_box(penguin) for penguin in species],
            width=1 / 3,
        )
    ),
    ui.row(
        ui.layout_column_wrap(
            ui.card(
                ui.card_header("Body mass distribution"),
                ui.output_plot("mass_distribution"),
            ),
            ui.card(
                ui.card_header("Penguin bills"),
                ui.output_plot("length_depth"),
            ),
            width=1 / 2,
        ),
    ),
)


def server(input: Inputs, output: Outputs, session: Session):
    @reactive.Calc
    def filtered_df() -> pd.DataFrame:
        filt_df = df[df["Species"].isin(input.species())]
        filt_df = filt_df.loc[filt_df["Body Mass (g)"] > input.mass()]
        return filt_df

    @render.text
    def adelie_count():
        return count_species(filtered_df(), "Adelie")

    @render.text
    def chinstrap_count():
        return count_species(filtered_df(), "Chinstrap")

    @render.text
    def gentoo_count():
        return count_species(filtered_df(), "Gentoo")

    @render.plot
    def length_depth():
        return sns.scatterplot(
            data=filtered_df(),
            x="Bill Length (mm)",
            y="Bill Depth (mm)",
            hue="Species",
        )

    @render.plot
    def mass_distribution():
        return sns.histplot(
            data=filtered_df(),
            x="Body Mass (g)",
            hue="Species",
        )


def count_species(df, species):
    return df[df["Species"] == species].shape[0]


app = App(app_ui, server)

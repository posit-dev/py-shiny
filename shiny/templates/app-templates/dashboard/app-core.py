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
            6000,
            3400,
        ),
        ui.input_checkbox_group(
            "species", "Filter by species", species, selected=species
        ),
    ),
    ui.row(
        ui.layout_columns(
            *[make_value_box(penguin) for penguin in species],
        )
    ),
    ui.row(
        ui.layout_columns(
            ui.card(
                ui.card_header("Summary statistics"),
                ui.output_data_frame("summary_statistics"),
            ),
            ui.card(
                ui.card_header("Penguin bills"),
                ui.output_plot("length_depth"),
            ),
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


def count_species(df, species):
    return df[df["Species"] == species].shape[0]


app = App(app_ui, server)

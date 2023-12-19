from pathlib import Path

import pandas as pd
import seaborn as sns

from shiny import App, Inputs, Outputs, Session, reactive, render, ui

species = ["Adelie", "Gentoo", "Chinstrap"]

species_images = {
    "Adelie": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e3/Hope_Bay-2016-Trinity_Peninsula%E2%80%93Ad%C3%A9lie_penguin_%28Pygoscelis_adeliae%29_04.jpg/1280px-Hope_Bay-2016-Trinity_Peninsula%E2%80%93Ad%C3%A9lie_penguin_%28Pygoscelis_adeliae%29_04.jpg",
    "Gentoo": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/00/Brown_Bluff-2016-Tabarin_Peninsula%E2%80%93Gentoo_penguin_%28Pygoscelis_papua%29_03.jpg/1202px-Brown_Bluff-2016-Tabarin_Peninsula%E2%80%93Gentoo_penguin_%28Pygoscelis_papua%29_03.jpg",
    "Chinstrap": "https://upload.wikimedia.org/wikipedia/commons/0/08/South_Shetland-2016-Deception_Island%E2%80%93Chinstrap_penguin_%28Pygoscelis_antarctica%29_04.jpg",
}


def penguin_box(x):
    return ui.value_box(
        title=x,
        value=ui.output_text(f"{x}_count".lower()),
        showcase=ui.img(
            src=species_images[x],
            max_width="100%",
            height="100%",
        ),
        full_screen=True,
    )


app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.input_slider(
            "mass",
            "Body Mass",
            min=2000,
            max=6000,
            value=3400,
        ),
        ui.input_checkbox_group("species", "Species", species, selected=species),
        title="Filter controls",
    ),
    ui.layout_column_wrap(*[penguin_box(penguin) for penguin in species], fill=False),
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
    title="Palmer Penguins Dashboard",
)


def server(input: Inputs, output: Outputs, session: Session):
    df = pd.read_csv(Path(__file__).parent / "penguins.csv", na_values="NA")
    sns.set_theme(style="white")

    @reactive.Calc
    def filtered_df() -> pd.DataFrame:
        filt_df = df[df["species"].isin(input.species())]
        return filt_df.loc[filt_df["body_mass_g"] > input.mass()]

    @reactive.Calc
    def aggregate_df() -> pd.DataFrame:
        return filtered_df().groupby("species").size()

    @render.text
    def adelie_count():
        return aggregate_df()[["Adelie"]][0]

    @render.text
    def chinstrap_count():
        return aggregate_df()[["Chinstrap"]][0]

    @render.text
    def gentoo_count():
        return aggregate_df()[["Gentoo"]][0]

    @render.plot
    def length_depth():
        return sns.scatterplot(
            data=filtered_df(),
            x="bill_length_mm",
            y="bill_depth_mm",
            hue="species",
        )

    @render.data_frame
    def summary_statistics():
        display_df = filtered_df()[
            [
                "species",
                "island",
                "bill_length_mm",
                "bill_depth_mm",
                "body_mass_g",
            ]
        ]
        return render.DataGrid(display_df, filters=True)


app = App(app_ui, server)

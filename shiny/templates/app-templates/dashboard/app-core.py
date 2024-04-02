import seaborn as sns
from faicons import icon_svg

# Import data from shared.py
from shared import app_dir, df

from shiny import App, reactive, render, ui

app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.input_slider("mass", "Mass", 2000, 6000, 6000),
        ui.input_checkbox_group(
            "species",
            "Species",
            ["Adelie", "Gentoo", "Chinstrap"],
            selected=["Adelie", "Gentoo", "Chinstrap"],
        ),
        title="Filter controls",
    ),
    ui.layout_column_wrap(
        ui.value_box(
            "Number of penguins",
            ui.output_text("count"),
            showcase=icon_svg("earlybirds"),
        ),
        ui.value_box(
            "Average bill length",
            ui.output_text("bill_length"),
            showcase=icon_svg("ruler-horizontal"),
        ),
        ui.value_box(
            "Average bill depth",
            ui.output_text("bill_depth"),
            showcase=icon_svg("ruler-vertical"),
        ),
        fill=False,
    ),
    ui.layout_columns(
        ui.card(
            ui.card_header("Bill length and depth"),
            ui.output_plot("length_depth"),
            full_screen=True,
        ),
        ui.card(
            ui.card_header("Penguin data"),
            ui.output_data_frame("summary_statistics"),
            full_screen=True,
        ),
    ),
    ui.include_css(app_dir / "styles.css"),
    title="Penguins dashboard",
    fillable=True,
)


def server(input, output, session):
    @reactive.calc
    def filtered_df():
        filt_df = df[df["species"].isin(input.species())]
        filt_df = filt_df.loc[filt_df["body_mass_g"] < input.mass()]
        return filt_df

    @render.text
    def count():
        return filtered_df().shape[0]

    @render.text
    def bill_length():
        return f"{filtered_df()['bill_length_mm'].mean():.1f} mm"

    @render.text
    def bill_depth():
        return f"{filtered_df()['bill_depth_mm'].mean():.1f} mm"

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
        cols = [
            "species",
            "island",
            "bill_length_mm",
            "bill_depth_mm",
            "body_mass_g",
        ]
        return render.DataGrid(filtered_df()[cols], filters=True)


app = App(app_ui, server)

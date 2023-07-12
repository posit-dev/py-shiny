from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from shiny import App, Inputs, Outputs, Session, reactive, render, ui
from shiny.plotutils import brushed_points

path = Path(__file__).parent / "boulder_temp.csv"
weather_df = pd.read_csv(path)
weather_df["date"] = pd.to_datetime(weather_df["date"])
weather_df["annotation"] = ""

app_ui = ui.page_fluid(
    ui.panel_title("Plot annotation example"),
    ui.p(
        """
        Select points to annotate,
        the plot is drawn with seaborn and all interaction is handled by Shiny.
        """,
        {"style": "font-size: larger"},
    ),
    ui.row(
        ui.column(
            6,
            ui.output_plot("time_series", brush=ui.brush_opts(direction="x")),
            ui.output_ui("annotator"),
        ),
        ui.column(
            4,
            ui.h3("Annotated points"),
            ui.output_data_frame("annotations"),
        ),
        ui.column(2, ui.download_button("download", "Download CSV")),
    ),
)


def server(input: Inputs, output: Outputs, session: Session):
    annotation_values = reactive.Value(None)

    @reactive.Calc
    def ts_data():
        annotated = annotation_values.get()
        if annotated is None:
            return weather_df
        else:
            return annotated

    @reactive.Calc
    def selected_data():
        out = brushed_points(ts_data(), input.time_series_brush(), xvar="date")
        return out

    @reactive.Effect
    @reactive.event(input.annotate_button)
    def _():
        selected = selected_data()
        selected["annotation_new"] = input.annotation()
        selected = selected.loc[:, ["date", "annotation_new"]]

        df = ts_data()

        df = df.merge(selected, on="date", how="left")
        df["annotation_new"] = df["annotation_new"].fillna("")
        updated_rows = df["annotation_new"] != ""
        df.loc[updated_rows, "annotation"] = df.loc[updated_rows, "annotation_new"]
        df = df.loc[:, ["date", "temp_c", "annotation"]]
        annotation_values.set(df)

    @output
    @render.plot
    def time_series():
        fig, ax = plt.subplots()
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
        ax.set_title("Temperature readings, Boulder Colorado")
        out = sns.scatterplot(
            data=ts_data(), x="date", y="temp_c", hue="annotation", ax=ax
        )

        out.tick_params(axis="x", rotation=30)
        return out.get_figure()

    @output
    @render.ui
    def annotator():
        if input.time_series_brush() is not None:
            selected = selected_data()

            min = str(selected["date"].min())
            max = str(selected["date"].max())

            min = min.replace(" 00:00:00+00:00", "")
            max = max.replace(" 00:00:00+00:00", "")

            out = ui.TagList(
                ui.row(
                    {"style": "padding-top: 20px;"},
                    ui.column(
                        4,
                        ui.p(f"{min} to {max}"),
                    ),
                    ui.column(
                        4,
                        ui.input_text("annotation", "", placeholder="Enter Annotation"),
                    ),
                    ui.column(4, ui.input_action_button("annotate_button", "Submit")),
                )
            )
            return out

    @output
    @render.data_frame
    def annotations():
        df = ts_data().copy()
        df["date"] = df["date"].dt.strftime("%Y-%m-%d")
        df = df.loc[df["annotation"] != ""]
        return df

    @session.download(filename="data.csv")
    def download():
        yield ts_data().to_csv()


app = App(app_ui, server)

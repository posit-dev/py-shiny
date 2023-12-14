from typing import Callable

import pandas as pd
from plots import plot_auc_curve, plot_precision_recall_curve, plot_score_distribution

from shiny import Inputs, Outputs, Session, module, render, ui


@module.ui
def training_ui():
    return ui.nav_panel(
        "Training Dashboard",
        ui.layout_columns(
            ui.card(
                ui.card_header("Model Metrics"),
                ui.output_plot("metric"),
                ui.input_select(
                    "metric",
                    "Metric",
                    choices=["ROC Curve", "Precision-Recall"],
                ),
            ),
            ui.card(
                ui.card_header("Training Scores"),
                ui.output_plot("score_dist"),
            ),
        ),
    )


@module.server
def training_server(
    input: Inputs,
    output: Outputs,
    session: Session,
    df: Callable[[], pd.DataFrame],
):
    @render.plot
    def score_dist():
        return plot_score_distribution(df())

    @render.plot
    def metric():
        if input.metric() == "ROC Curve":
            return plot_auc_curve(df(), "is_electronics", "training_score")
        else:
            return plot_precision_recall_curve(df(), "is_electronics", "training_score")


@module.ui
def data_view_ui():
    return ui.nav_panel(
        "View Data",
        ui.layout_columns(
            ui.value_box(
                title="Row count",
                value=ui.output_text("row_count"),
                theme="primary",
            ),
            ui.value_box(
                title="Mean score",
                value=ui.output_text("mean_score"),
                theme="bg-green",
            ),
            gap="20px",
        ),
        ui.layout_columns(
            ui.card(ui.output_data_frame("data")),
            style="margin-top: 20px;",
        ),
    )


@module.server
def data_view_server(
    input: Inputs, output: Outputs, session: Session, df: Callable[[], pd.DataFrame]
):
    @render.text
    def row_count():
        return df().shape[0]

    @render.text
    def mean_score():
        return round(df()["training_score"].mean(), 2)

    @render.data_frame
    def data():
        return df()

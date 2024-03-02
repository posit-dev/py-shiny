from model_plots import (
    plot_accuracy_over_time,
    plot_feature_importance,
    plot_loss_over_time,
)

from shiny.express import render, ui

ui.page_opts(title="Model Dashboard")

ui.markdown("Using `ui.layout_columns()` for the layout.")


with ui.layout_columns(
    col_widths={"sm": (5, 7, 12)},
    # row_heights=(2, 3),
    # height="700px",
):
    with ui.card(full_screen=True):
        ui.card_header("Loss Over Time")

        @render.plot
        def loss_over_time():
            return plot_loss_over_time()

    with ui.card(full_screen=True):
        ui.card_header("Accuracy Over Time")

        @render.plot
        def accuracy_over_time():
            return plot_accuracy_over_time()

    with ui.card(full_screen=True):
        ui.card_header("Feature Importance")

        @render.plot
        def feature_importance():
            return plot_feature_importance()

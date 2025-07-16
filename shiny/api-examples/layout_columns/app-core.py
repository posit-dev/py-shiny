from model_plots import *  # model plots and cards

from shiny import App, Inputs, Outputs, Session, render, ui

app_ui = ui.page_fluid(
    ui.panel_title(ui.h2("Model Dashboard")),
    ui.markdown("Using `ui.layout_columns()` for the layout."),
    ui.layout_columns(
        card_loss,
        card_acc,
        card_feat,
        col_widths={"sm": (5, 7, 12)},
        # row_heights=(2, 3),
        # height="700px",
    ),
)


def server(input: Inputs, output: Outputs, session: Session):
    @render.plot
    def loss_over_time():
        return plot_loss_over_time()

    @render.plot
    def accuracy_over_time():
        return plot_accuracy_over_time()

    @render.plot
    def feature_importance():
        return plot_feature_importance()


app = App(app_ui, server)

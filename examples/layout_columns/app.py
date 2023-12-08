from kids_say import random_cards

from shiny import App, Inputs, Outputs, Session, reactive, render, ui

app_ui = ui.page_fluid(
    ui.panel_title(ui.h2("Layout Columns")),
    ui.input_slider("n_cards", label="Number of Cards", min=1, max=24, value=12),
    ui.input_action_button("new_cards", "New Cards"),
    ui.output_ui("layout_columns_example").add_class("mt-3"),
)


def server(input: Inputs, output: Outputs, session: Session):
    @reactive.calc
    @reactive.event(input.new_cards, ignore_none=False)
    def cards():
        return random_cards(24)

    @render.ui
    def layout_columns_example():
        return ui.layout_columns(
            *cards()[: input.n_cards()],
            # col_widths=[4, 2, 3, 3],
            # col_widths={"sm": 3},
            # col_widths=(8, 4),
            row_heights=(2, 3, 4),
            # row_heights="500px",
            col_widths={
                "sm": 3,
                "md": (4, 2, 3, 3),
                "lg": [3, 4, 2, 3],
                "xl": (3, 3, 4, 2),
                "xxl": (2, 3, 3, -1, 3),
            },
        )


app = App(app_ui, server)

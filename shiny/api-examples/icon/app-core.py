from shiny import App, ui

app_ui = ui.page_fluid(
    ui.h2("Icon Examples"),
    ui.layout_columns(
        ui.card(
            ui.card_header("FontAwesome Icons"),
            ui.p("Default library — solid style:"),
            ui.icon("star"),
            ui.icon("gear"),
            ui.icon("user"),
            ui.br(),
            ui.p("Brand icons (variant='brands'):"),
            ui.icon("github", variant="brands"),
            ui.icon("python", variant="brands"),
            ui.icon("twitter", variant="brands"),
            ui.br(),
            ui.p("Custom fill color:"),
            ui.icon("star", fill="gold"),
            ui.icon("heart", fill="crimson"),
            ui.icon("circle-check", fill="green"),
        ),
        ui.card(
            ui.card_header("Bootstrap Icons"),
            ui.p("Basic icons (lib='bs'):"),
            ui.icon("star", lib="bs"),
            ui.icon("gear", lib="bs"),
            ui.icon("person", lib="bs"),
            ui.br(),
            ui.p("Custom fill color:"),
            ui.icon("star-fill", lib="bs", fill="gold"),
            ui.icon("heart-fill", lib="bs", fill="crimson"),
            ui.br(),
            ui.p("Styled with CSS classes:"),
            ui.icon("exclamation-triangle-fill", lib="bs", size="1.25em", class_="text-warning"),
            ui.icon("check-circle-fill", lib="bs", size="1.25em", class_="text-success"),
            ui.icon("x-circle-fill", lib="bs", size="1.25em", class_="text-danger"),
        ),
    ),
    ui.layout_columns(
        ui.card(
            ui.card_header("Sizes"),
            ui.p("Semantic sizes (same scale for both libs):"),
            *[ui.icon("circle", lib="bs", size=sz) for sz in ("xs", "sm", "md", "lg", "xl", "2xl")],
            ui.br(),
            ui.p("CSS units:"),
            ui.icon("gear", size="1em"),
            ui.icon("gear", size="2em"),
            ui.icon("gear", size="3em"),
            ui.br(),
            ui.p("Numeric (px):"),
            ui.icon("gear", lib="bs", size=16),
            ui.icon("gear", lib="bs", size=32),
            ui.icon("gear", lib="bs", size=48),
        ),
        ui.card(
            ui.card_header("Accessibility"),
            ui.p(
                "Decorative (default) — hidden from screen readers. "
                "Label the surrounding element instead:"
            ),
            ui.input_action_button(
                "btn_delete",
                ui.icon("trash"),
                aria_label="Delete item",
            ),
            ui.br(),
            ui.br(),
            ui.p("Semantic — icon conveys meaning directly:"),
            ui.icon(
                "circle-exclamation",
                size="2em",
                title="Warning",
                a11y="semantic",
            ),
            ui.icon(
                "exclamation-triangle",
                lib="bs",
                size="2em",
                title="Warning",
                a11y="semantic",
            ),
            ui.br(),
            ui.p("Semantic without title — label derived from icon name:"),
            ui.icon("heart-fill", lib="bs", a11y="semantic"),
        ),
    ),
    ui.layout_columns(
        ui.card(
            ui.card_header("Icons in Buttons"),
            ui.p("FontAwesome:"),
            ui.input_action_button("btn_fa", "Save", icon=ui.icon("floppy-disk")),
            ui.input_action_button(
                "btn_fa2", "Delete", icon=ui.icon("trash", fill="crimson")
            ),
            ui.br(),
            ui.br(),
            ui.p("Bootstrap Icons:"),
            ui.input_action_button(
                "btn_bs", "Save", icon=ui.icon("floppy", lib="bs")
            ),
            ui.input_action_button(
                "btn_bs2", "Delete", icon=ui.icon("trash", lib="bs")
            ),
        ),
    ),
)


def server(input, output, session):
    pass


app = App(app_ui, server)

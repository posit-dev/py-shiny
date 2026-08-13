from shiny import App, ui

theme = ui.Theme.from_brand(__file__)

app_ui = ui.page_fluid(
    ui.h2("Brand color modes", id="heading"),
    ui.tags.a("Brand link", id="link", href="#"),
    ui.tags.button("Primary", id="primary", class_="btn btn-primary"),
    ui.tags.div("Primary background", id="primary-bg", class_="bg-primary"),
    ui.tags.div("Scalar success", id="success-bg", class_="bg-success"),
    ui.tags.div("Partial warning", id="warning-bg", class_="bg-warning"),
    ui.tags.code("Inline code", id="inline-code"),
    ui.tags.pre("Block code", id="block-code"),
    theme=theme,
)

app = App(app_ui, None)

import faicons as fa

from shiny import App, ui

app_ui = ui.page_fluid(
    ui.value_box(
        ui.span("Red Color theme w/ Fullscreen"),
        ui.h1("Showcase top right"),
        ui.span("Inside the fullscreen"),
        showcase=fa.icon_svg("faucet-drip"),
        showcase_layout=ui.showcase_top_right(),
        theme="red",
        full_screen=True,
        id="valuebox1",
    ),
    ui.value_box(
        "Primary theme w/o Fullscreen",
        ui.h5(ui.HTML("Showcase left center")),
        showcase=fa.icon_svg("faucet-drip"),
        showcase_layout=ui.showcase_left_center(),
        theme="primary",
        full_screen=False,
        id="valuebox2",
    ),
    ui.value_box(
        ui.span("No theme w/ Fullscreen"),
        ui.h3("Showcase bottom"),
        showcase=fa.icon_svg("faucet-drip"),
        showcase_layout=ui.showcase_bottom(),
        full_screen=True,
        id="valuebox3",
    ),
    ui.value_box(
        "No showcase - w/o Fullscreen (default)",
        "No theme - only defaults",
        id="valuebox4",
    ),
    ui.value_box(
        "No showcase w/ showcase layout",
        "Red text - fill is False",
        max_height="500px",
        showcase_layout=ui.showcase_left_center(),
        fill=False,
        theme="text-red",
        id="valuebox5",
    ),
)


app = App(app_ui, server=None)

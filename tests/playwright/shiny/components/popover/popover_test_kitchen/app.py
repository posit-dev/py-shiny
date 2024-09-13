from shiny.express import ui

ui.page_opts(title="Popover Kitchen sink", id="page_navbar")

ui.br()
ui.br()

with ui.popover(id="btn_popover_title", title="Popover title"):
    ui.input_action_button("btn", "A button")
    "Placement should be auto along with a title"

ui.br()
ui.br()
ui.br()
ui.br()

with ui.popover(id="btn_popover_top", placement="top"):
    ui.input_action_button("btn2", "A button")
    "Popover placement should be on the top"

ui.br()
ui.br()
ui.br()
ui.br()


with ui.layout_columns(col_widths=[4, 4]):

    with ui.popover(id="btn_popover_right", placement="right"):
        ui.input_action_button("btn3", "A button")
        "Popover placement should be on the right"

    with ui.popover(id="btn_popover_left", placement="left"):
        ui.input_action_button("btn4", "A button")
        "Popover placement should be on the left"

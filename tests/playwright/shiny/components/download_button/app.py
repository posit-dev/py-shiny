from __future__ import annotations

import faicons

from shiny import App, Inputs, Outputs, Session, reactive, render, ui

app_ui = ui.page_fluid(
    ui.h2("Download button kitchen sink"),
    ui.layout_columns(
        ui.card(
            ui.h6("Click the button below to increment the counter"),
            ui.input_action_button("increment", "Add to counter", class_="mb-2"),
        ),
        ui.card(
            ui.h4("Buttons"),
            ui.download_button(
                "plain_csv",
                "Plain CSV",
            ),
            ui.download_button(
                "styled_csv",
                "Styled CSV",
                icon=faicons.icon_svg("file-csv"),
                width="560px",
            ),
        ),
    ),
)


def server(input: Inputs, output: Outputs, session: Session) -> None:
    inventory_total = 0
    plain_total = 0
    styled_total = 0

    @reactive.effect
    @reactive.event(input.increment)
    def _() -> None:
        nonlocal inventory_total
        inventory_total += 1

    @render.download(filename=lambda: f"plain-{plain_total + 1}.csv")
    async def plain_csv():
        nonlocal plain_total
        plain_total += 1
        current_plain = plain_total
        current_inventory = inventory_total
        yield "kind,inventory,count\n"
        yield f"plain,{current_inventory},{current_plain}\n"

    @render.download(
        filename=lambda: f"styled-{inventory_total}-{styled_total + 1}.csv"
    )
    async def styled_csv():
        nonlocal styled_total
        styled_total += 1
        current_styled = styled_total
        current_inventory = inventory_total
        yield "metric,value\n"
        yield f"inventory,{current_inventory}\n"
        yield f"download_number,{current_styled}\n"


app = App(app_ui, server)

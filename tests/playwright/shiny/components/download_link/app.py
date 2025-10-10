from __future__ import annotations

import faicons

from shiny import App, Inputs, Outputs, Session, reactive, render, ui


def _title(text: str) -> ui.Tag:
    return ui.tags.h4(text, class_="mb-3")


def _action_label(text: str) -> ui.Tag:
    return ui.tags.span(text, class_="action-label")


def _action_icon(text: str) -> ui.Tag:
    return ui.tags.span(text, class_="action-icon")


app_ui = ui.page_fluid(
    ui.h2("Download link kitchen sink"),
    ui.layout_columns(
        ui.card(
            _title("Controls"),
            ui.input_text("prefix", "Filename prefix", value="report"),
            ui.input_checkbox("include_summary", "Include summary footer", value=True),
        ),
        ui.card(
            _title("Links"),
            ui.download_link(
                "plain_link",
                _action_label("Plain report"),
            ),
            ui.download_link(
                "styled_link",
                "Styled report",
                icon=faicons.icon_svg("file-arrow-down"),
                width="560px",
            ),
        ),
    ),
)


def server(input: Inputs, output: Outputs, session: Session) -> None:
    plain_total = 0
    styled_total = 0
    current_prefix = "report"
    summary_enabled = True

    @reactive.calc
    def prefix_value() -> str:
        value = input.prefix()
        return value.strip() or "report"

    @reactive.calc
    def include_summary() -> bool:
        return bool(input.include_summary())

    def sync_controls() -> None:
        nonlocal current_prefix, summary_enabled
        with reactive.isolate():
            current_prefix = prefix_value()
            summary_enabled = include_summary()

    sync_controls()

    @reactive.effect
    def _() -> None:
        prefix_value()
        include_summary()
        sync_controls()

    @render.download(filename=lambda: f"{current_prefix}-plain.txt")
    async def plain_link():
        nonlocal plain_total
        plain_total += 1
        current_count = plain_total
        prefix = current_prefix
        include_footer = summary_enabled
        yield f"{prefix} plain download #{current_count}\n"
        if include_footer:
            yield "Summary: plain link\n"

    @render.download(filename=lambda: f"{current_prefix}-styled.csv")
    async def styled_link():
        nonlocal styled_total
        styled_total += 1
        current_count = styled_total
        prefix = current_prefix
        include_footer = summary_enabled
        yield "metric,value\n"
        yield f"prefix,{prefix}\n"
        yield f"download_count,{current_count}\n"
        if include_footer:
            yield "footer,enabled\n"


app = App(app_ui, server)

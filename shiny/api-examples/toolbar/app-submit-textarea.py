from faicons import icon_svg

from shiny import App, reactive, render, ui

app_ui = ui.page_fluid(
    ui.h2("Toolbar in Submit Text Area"),
    ui.p(
        "This example shows how to use the toolbar parameter in input_submit_textarea to add controls."
    ),
    ui.card(
        ui.card_header("Message Composer"),
        ui.card_body(
            ui.input_submit_textarea(
                "message",
                label="Message",
                placeholder="Compose your message...",
                rows=8,
                toolbar=ui.toolbar(
                    ui.toolbar_input_select(
                        "priority",
                        label="Priority",
                        choices={
                            "low": "Low",
                            "medium": "Medium",
                            "high": "High",
                            "urgent": "Urgent",
                        },
                        selected="medium",
                        icon=icon_svg("flag"),
                    ),
                    ui.toolbar_divider(),
                    ui.toolbar_input_button(
                        "btn_attach",
                        label="Attach",
                        icon=icon_svg("paperclip"),
                        tooltip="Attach file",
                    ),
                    ui.toolbar_input_button(
                        "btn_emoji",
                        label="Emoji",
                        icon=icon_svg("face-smile"),
                        tooltip="Insert emoji",
                    ),
                    ui.toolbar_input_button(
                        "btn_copy_draft",
                        label="Copy",
                        icon=icon_svg("copy"),
                        tooltip="Copy to clipboard",
                    ),
                    align="right",
                ),
            ),
            ui.output_text("message_status"),
        ),
    ),
)


def server(input, output, session):
    submit_count = reactive.value(0)

    @reactive.effect
    @reactive.event(input.message)
    def _():
        # Increment submit count when message is submitted
        submit_count.set(submit_count.get() + 1)

    @output
    @render.text
    def message_status():
        priority = input.priority()
        clicks_attach = input.btn_attach()
        clicks_emoji = input.btn_emoji()
        clicks_copy = input.btn_copy_draft()
        return f"Priority: {priority} | Attach: {clicks_attach}, Emoji: {clicks_emoji}, Copy: {clicks_copy} | Submits: {submit_count.get()}"


app = App(app_ui, server)

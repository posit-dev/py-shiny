from faicons import icon_svg

from shiny import App, reactive, render, ui

app_ui = ui.page_fluid(
    ui.h2("Toolbar Special Cases Test App"),
    ui.p(
        "Special toolbar use cases: toolbars in input labels for numeric inputs, text areas, and submit text areas."
    ),
    # Test 1: Toolbar in numeric input label
    ui.card(
        ui.card_header("Test 1: Toolbar in Numeric Input Label"),
        ui.card_body(
            ui.input_numeric(
                "quantity",
                label=ui.toolbar(
                    ui.toolbar_spacer(),
                    ui.toolbar_input_button(
                        "btn_preset_10",
                        label="10",
                        tooltip="Set to 10",
                    ),
                    ui.toolbar_input_button(
                        "btn_preset_50",
                        label="50",
                        tooltip="Set to 50",
                    ),
                    ui.toolbar_input_button(
                        "btn_preset_100",
                        label="100",
                        tooltip="Set to 100",
                    ),
                    ui.toolbar_divider(),
                    ui.toolbar_input_button(
                        "btn_reset",
                        label="Reset",
                        icon=icon_svg("rotate-left"),
                        tooltip="Reset to 1",
                    ),
                    align="right",
                ),
                value=1,
                min=1,
                max=1000,
            ),
            ui.output_text("quantity_status"),
        ),
    ),
    # Test 2: Toolbar in text_area input label
    ui.card(
        ui.card_header("Test 2: Toolbar in Text Area Label"),
        ui.card_body(
            ui.input_text_area(
                "notes",
                label=ui.toolbar(
                    ui.toolbar_input_button(
                        "btn_bold",
                        label="Bold",
                        icon=icon_svg("bold"),
                        tooltip="Make text bold",
                    ),
                    ui.toolbar_input_button(
                        "btn_italic",
                        label="Italic",
                        icon=icon_svg("italic"),
                        tooltip="Make text italic",
                    ),
                    ui.toolbar_input_button(
                        "btn_link",
                        label="Link",
                        icon=icon_svg("link"),
                        tooltip="Insert link",
                    ),
                    ui.toolbar_divider(),
                    ui.toolbar_input_select(
                        "text_size",
                        label="Text Size",
                        choices={
                            "small": "Small",
                            "normal": "Normal",
                            "large": "Large",
                        },
                        selected="normal",
                        show_label=False,
                    ),
                    ui.toolbar_spacer(),
                    ui.toolbar_input_button(
                        "btn_clear",
                        label="Clear",
                        icon=icon_svg("eraser"),
                        tooltip="Clear all text",
                        border=True,
                    ),
                    align="right",
                ),
                placeholder="Type your notes here...",
                rows=6,
            ),
            ui.output_text("notes_status"),
        ),
    ),
    # Test 3: Toolbar in input_submit_textarea with submit functionality
    ui.card(
        ui.card_header("Test 3: Submit Text Area with Toolbar Parameter"),
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
    # Test 1: Numeric input with presets
    @output
    @render.text
    def quantity_status():
        quantity = input.quantity()
        clicks_10 = input.btn_preset_10()
        clicks_50 = input.btn_preset_50()
        clicks_100 = input.btn_preset_100()
        clicks_reset = input.btn_reset()
        return f"Quantity: {quantity} | Preset clicks - 10: {clicks_10}, 50: {clicks_50}, 100: {clicks_100}, Reset: {clicks_reset}"

    @reactive.effect
    @reactive.event(input.btn_preset_10)
    def _():
        ui.update_numeric("quantity", value=10)

    @reactive.effect
    @reactive.event(input.btn_preset_50)
    def _():
        ui.update_numeric("quantity", value=50)

    @reactive.effect
    @reactive.event(input.btn_preset_100)
    def _():
        ui.update_numeric("quantity", value=100)

    @reactive.effect
    @reactive.event(input.btn_reset)
    def _():
        ui.update_numeric("quantity", value=1)

    # Test 2: Text area with formatting
    @output
    @render.text
    def notes_status():
        text_size = input.text_size()
        clicks_bold = input.btn_bold()
        clicks_italic = input.btn_italic()
        clicks_link = input.btn_link()
        clicks_clear = input.btn_clear()
        return f"Text Size: {text_size} | Bold: {clicks_bold}, Italic: {clicks_italic}, Link: {clicks_link}, Clear: {clicks_clear}"

    @reactive.effect
    @reactive.event(input.btn_clear)
    def _():
        ui.update_text_area("notes", value="")

    # Test 3: Message with submit (input_submit_text_area)
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

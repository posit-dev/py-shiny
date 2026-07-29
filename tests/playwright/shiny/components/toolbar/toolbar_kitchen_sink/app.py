from faicons import icon_svg

from shiny import App, Inputs, Outputs, Session, reactive, render, ui

app_ui = ui.page_fluid(
    ui.h2("Toolbar Kitchen Sink Example"),
    ui.p("Comprehensive examples of toolbar usage patterns"),
    # Card 1: Toolbar in header with icon button, select, divider
    # Body has input with toolbar in label
    ui.card(
        ui.card_header(
            "Document Editor",
            ui.toolbar(
                ui.toolbar_input_button(
                    "btn_save",
                    label="Save",
                    icon=icon_svg("floppy-disk"),
                    tooltip="Save Document",
                ),
                ui.toolbar_divider(),
                ui.toolbar_input_select(
                    "format",
                    label="Format",
                    choices={"md": "Markdown", "txt": "Plain Text", "html": "HTML"},
                    selected="md",
                    icon=icon_svg("file-code"),
                ),
                align="right",
            ),
        ),
        ui.card_body(
            ui.input_text_area(
                "content",
                label=ui.toolbar(
                    ui.toolbar_input_button(
                        "btn_bold",
                        label="Bold",
                        icon=icon_svg("bold"),
                    ),
                    ui.toolbar_input_button(
                        "btn_italic",
                        label="Italic",
                        icon=icon_svg("italic"),
                    ),
                    ui.toolbar_input_button(
                        "btn_code",
                        label="Code",
                        icon=icon_svg("code"),
                    ),
                    align="right",
                ),
                placeholder="Type your content here...",
                rows=8,
            ),
            ui.output_text("output_card1"),
        ),
    ),
    # Card 2: Toolbar in header with label button, select with label, spacer
    # Body has submit textarea with toolbar
    ui.card(
        ui.card_header(
            "Message Composer",
            ui.toolbar(
                ui.toolbar_input_button(
                    "btn_new",
                    label="New Message",
                    icon=icon_svg("plus"),
                    show_label=True,
                ),
                ui.toolbar_spacer(),
                ui.toolbar_input_select(
                    "recipient",
                    label="To",
                    choices={
                        "team": "Team",
                        "manager": "Manager",
                        "support": "Support",
                    },
                    selected="team",
                    show_label=True,
                ),
                align="right",
            ),
        ),
        ui.card_body(
            ui.input_submit_textarea(
                "message",
                label="Message",
                placeholder="Compose your message...",
                rows=6,
                toolbar=ui.toolbar(
                    ui.toolbar_input_select(
                        "priority",
                        label="Priority",
                        choices={"low": "Low", "medium": "Medium", "high": "High"},
                        selected="medium",
                        icon=icon_svg("flag"),
                    ),
                    ui.toolbar_divider(),
                    ui.toolbar_input_button(
                        "btn_attach",
                        label="Attach",
                        icon=icon_svg("paperclip"),
                    ),
                    ui.toolbar_input_button(
                        "btn_emoji",
                        label="Emoji",
                        icon=icon_svg("face-smile"),
                    ),
                    align="right",
                ),
            ),
            ui.output_text("output_card2"),
        ),
    ),
)


def server(input: Inputs, output: Outputs, session: Session) -> None:
    # Card 1 outputs
    @output
    @render.text
    def output_card1():
        save_clicks = input.btn_save()
        format_val = input.format()
        bold_clicks = input.btn_bold()
        italic_clicks = input.btn_italic()
        code_clicks = input.btn_code()
        return f"Save: {save_clicks} | Format: {format_val} | Bold: {bold_clicks}, Italic: {italic_clicks}, Code: {code_clicks}"

    # Update save button icon and tooltip after click
    @reactive.effect
    @reactive.event(input.btn_save)
    def _():
        # After click, change to check icon and update tooltip
        ui.update_toolbar_input_button(
            "btn_save",
            icon=icon_svg("circle-check"),
        )
        ui.update_tooltip("btn_save_tooltip", "Saved successfully!")

    # Card 2 outputs
    submit_count = reactive.value(0)

    @reactive.effect
    @reactive.event(input.message)
    def _():
        submit_count.set(submit_count.get() + 1)

    @output
    @render.text
    def output_card2():
        new_clicks = input.btn_new()
        recipient_val = input.recipient()
        priority_val = input.priority()
        attach_clicks = input.btn_attach()
        emoji_clicks = input.btn_emoji()
        return f"New: {new_clicks} | To: {recipient_val} | Priority: {priority_val} | Attach: {attach_clicks}, Emoji: {emoji_clicks} | Submits: {submit_count.get()}"


app = App(app_ui, server)

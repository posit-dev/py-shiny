from faicons import icon_svg

from shiny import App, Inputs, Outputs, Session, reactive, render, ui

app_ui = ui.page_fluid(
    ui.h2("Toolbar Kitchen Sink Example"),
    ui.p("Comprehensive examples of toolbar usage patterns"),
    # Row 1: Two cards side by side
    ui.layout_columns(
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
        # Card 3: Image gallery with toolbar controls
        ui.card(
            ui.card_header(
                "Image Gallery",
                ui.toolbar(
                    ui.toolbar_input_select(
                        "view_mode",
                        label="View",
                        choices={
                            "grid": "Grid",
                            "list": "List",
                            "slideshow": "Slideshow",
                        },
                        selected="grid",
                        icon=icon_svg("images"),
                    ),
                    ui.toolbar_divider(),
                    ui.toolbar_input_button(
                        "btn_filter",
                        label="Filter",
                        icon=icon_svg("filter"),
                    ),
                    ui.toolbar_input_button(
                        "btn_sort",
                        label="Sort",
                        icon=icon_svg("arrow-down-a-z"),
                    ),
                    align="right",
                ),
            ),
            ui.card_body(
                ui.input_slider(
                    "zoom",
                    label=ui.toolbar(
                        ui.toolbar_input_button(
                            "btn_zoom_out",
                            label="Zoom Out",
                            icon=icon_svg("magnifying-glass-minus"),
                        ),
                        ui.toolbar_input_button(
                            "btn_zoom_in",
                            label="Zoom In",
                            icon=icon_svg("magnifying-glass-plus"),
                        ),
                        align="right",
                    ),
                    min=50,
                    max=200,
                    value=100,
                    post="%",
                ),
                ui.output_text("output_card3"),
            ),
        ),
        col_widths=[6, 6],
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
            ui.layout_columns(
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
                ui.div(
                    ui.h5("Sent Messages"),
                    ui.output_ui("output_card2"),
                ),
                col_widths=[6, 6],
            ),
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

    # Card 3 outputs (Image Gallery)
    @output
    @render.text
    def output_card3():
        view_mode = input.view_mode()
        filter_clicks = input.btn_filter()
        sort_clicks = input.btn_sort()
        zoom_val = input.zoom()
        zoom_in_clicks = input.btn_zoom_in()
        zoom_out_clicks = input.btn_zoom_out()
        return f"View: {view_mode} | Zoom: {zoom_val}% | Filter: {filter_clicks}, Sort: {sort_clicks} | Zoom In: {zoom_in_clicks}, Zoom Out: {zoom_out_clicks}"

    # Card 2 outputs
    messages = reactive.value([])

    @reactive.effect
    @reactive.event(input.message)
    def _():
        message_text = input.message()
        recipient = input.recipient()
        priority = input.priority()
        if message_text and message_text.strip():
            current_messages = list(messages.get())  # Create a new list
            current_messages.append(
                {"text": message_text, "to": recipient, "priority": priority}
            )
            messages.set(current_messages)

    @reactive.effect
    @reactive.event(input.btn_new)
    def _():
        # Clear messages when New Message is clicked
        messages.set([])

    @output
    @render.ui
    def output_card2():
        msg_list = messages.get()
        if not msg_list:
            return ui.p("No messages sent yet.", style="color: #888;")

        items = []
        for i, msg in enumerate(reversed(msg_list), 1):
            items.append(
                ui.div(
                    ui.strong(f"To: {msg['to']} ({msg['priority']} priority)"),
                    ui.br(),
                    ui.span(msg["text"]),
                    style="padding: 8px; margin-bottom: 8px; border: 1px solid #ddd; border-radius: 4px; display: block;",
                )
            )
        return ui.div(*items)


app = App(app_ui, server)

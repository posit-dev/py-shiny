from __future__ import annotations

import datetime
import os
import pathlib
import sys
import typing
from typing import Any, Callable

import matplotlib.pyplot as plt

# =============================================================================
# Data
# =============================================================================
import pandas as pd
from htmltools import TagList

from shiny import App, Inputs, Outputs, Session, module, reactive, render, ui
from shiny.session import session_context
from shiny.types import ImgData

pandas_df = pd.DataFrame(
    {
        "name": ["Mazda RX4", "Mazda RX4 Wag", "Datsun 710", "Hornet 4 Drive"],
        "mpg": [21.0, 21.0, 22.8, 21.4],
        "cyl": [6, 6, 4, 6],
    }
)

# To add more options, add more images to the `imgs` folder!!
img_path = pathlib.Path(__file__).parent / "imgs"
penguin_imgs = [str(img_path / img) for img in os.listdir(img_path)]
assert len(penguin_imgs) > 0
letters = [letter for letter in "abcdefghijklmnopqrstuvwxyz"][: len(penguin_imgs)]

input_keys = (
    "input_action_button",
    "input_action_link",
    "download_button",
    "download_link",
    "accordion",
    "input_file",
    "input_checkbox",
    "input_checkbox_group",
    "input_date",
    "input_date_range",
    "input_numeric",
    "input_password",
    "input_radio_buttons",
    "input_select",
    "input_selectize",
    "input_slider",
    "input_switch",
    "input_text",
    "input_text_area",
    "navset_bar",
    "navset_card_pill",
    "navset_card_tab",
    "navset_hidden",
    "navset_pill",
    "navset_tab",
    "sidebar",
    "popover",
    "tooltip",
)
x_input_keys = ()


session_dict: dict[str, Session] = {}


# ============================================================
# Counter module
# ============================================================
@module.ui
def mod_x_ui(label: str) -> ui.TagChild:
    def ui_navs(label: str) -> list[ui._navs.NavPanel]:
        return [
            ui.nav_panel(
                letter.capitalize(),
                f"{label} - {letter.capitalize()} content",
                value=letter,
            )
            for letter in letters
        ]

    return ui.layout_sidebar(
        ui.sidebar("Sidebar content", id="sidebar", width="100px"),
        ui.h2(label),
        ui.tags.label("Output status:"),
        ui.tags.style(
            """
            pre[id*="status_"] {
                padding: 0;
                font-size: xx-small;
                text-wrap: balance;
            }
            """
        ),
        ui.layout_column_wrap(
            *[
                ui.output_text_verbatim(f"status_x_{x_input_key}", placeholder=True)
                for x_input_key in x_input_keys
            ],
            *[
                ui.output_text_verbatim(f"status_{input_key}", placeholder=True)
                for input_key in input_keys
            ],
            width=1 / 2,
            gap="2px",
            heights_equal="row",
        ),
        ui.tags.label("Inputs that need to be visible when updated:"),
        ui.card(
            ui.popover(
                ui.input_action_button("popover_btn", "Popover btn"),
                "Popover content",
                id="popover",
            ),
            ui.tooltip(
                ui.input_action_button("tooltip_btn", "Tooltip btn"),
                "Tooltip content",
                id="tooltip",
            ),
        ),
        ui.tags.label("Manual inputs / outputs:"),
        ui.card(
            ui.input_action_button("input_action_button", "input_button"),
            ui.input_action_link("input_action_link", "Link"),
            ui.download_button("download_button", "Download"),
            ui.download_link("download_link", "Download Link"),
            ui.input_file("input_file", "File"),
            # Plot
            ui.tags.label(ui.markdown("Plot (Changes w/ `input.radio_buttons()`)")),
            ui.output_plot("out_plot"),
        ),
        ui.accordion(
            *[
                ui.accordion_panel(
                    ui.markdown(f"Panel for `{letter}`"),
                    ui.markdown(f"Content for `{letter}`"),
                    value=letter,
                )
                for letter in letters
            ],
            id="accordion",
        ),
        ui.input_checkbox("input_checkbox", "Checkbox"),
        ui.input_checkbox_group(
            "input_checkbox_group", "Checkbox group", choices=letters
        ),
        ui.input_date("input_date", "Date", value="2023-08-24"),
        ui.input_date_range(
            "input_date_range", "Date range", start="2023-08-24", end="2023-08-25"
        ),
        ui.input_numeric(
            "input_numeric", "Numeric", 1, min=0, max=len(letters), step=1
        ),
        ui.input_password("input_password", "Password"),
        ui.input_radio_buttons("input_radio_buttons", "Radio buttons", choices=letters),
        ui.input_select("input_select", "Select", choices=letters),
        ui.input_selectize("input_selectize", "Selectize", choices=letters),
        ui.input_slider(
            "input_slider", "Slider", min=0, max=len(letters), step=1, value=1
        ),
        ui.input_switch("input_switch", "Switch"),
        ui.input_text("input_text", "Text"),
        ui.input_text_area("input_text_area", "Text area"),
        ui.p("(Navbars are in Cards to give some sort of bounding box.)"),
        *[
            ui.card(y)
            for y in (
                ui.navset_bar(
                    *ui_navs("Navset Bar"), title="Navset Bar", id="navset_bar"
                ),
                ui.navset_card_pill(
                    *ui_navs("Navset Card Pill"), id="navset_card_pill"
                ),
                ui.navset_card_tab(*ui_navs("Navset Card Tab"), id="navset_card_tab"),
                TagList(
                    ui.tags.label("(Navset hidden)"),
                    ui.navset_hidden(*ui_navs("Navset Hidden"), id="navset_hidden"),
                ),
                ui.navset_pill(*ui_navs("Navset Pill"), id="navset_pill"),
                ui.navset_tab(*ui_navs("Navset Tab"), id="navset_tab"),
            )
        ],
        *[
            ui.card(ui.tags.label(ui.markdown(f"{label}:")), y)
            for label, y in (
                (
                    "Data Frame (Grows w/ `input.radio_buttons()`)",
                    ui.output_data_frame("out_data_frame"),
                ),
                (
                    "Table (Grows w/ `input.radio_buttons()`)",
                    ui.output_table("out_table"),
                ),
                (
                    "Image (Changes w/ `input.radio_buttons()`)",
                    ui.output_image("out_image", height="180px"),
                ),
                ("Text Verbatim", ui.output_text_verbatim("out_text_verbatim")),
                ("Text", ui.output_text("out_text")),
                ("UI", ui.output_ui("out_ui")),
            )
        ],
        # ui.page_navbar(), # Should not be tested in a module as it is a top level element
    )


@module.server
def mod_x_server(
    input: Inputs,
    output: Outputs,
    session: Session,
):
    session_dict[session.ns] = session

    @reactive.calc
    def n():
        return int(letters.index(input.input_radio_buttons()))

    @render.image
    def out_image() -> ImgData:
        return {"src": penguin_imgs[n()]}

    @render.plot
    def out_plot():
        dt = [1, 2, 3, 4, 5]
        plt.bar(  # pyright: ignore[reportUnknownVariableType, reportUnknownMemberType]
            dt[: ((n() + 1) % len(dt))], dt[: ((n() + 1) % len(dt))]  # pyright: ignore
        )

    @render.table
    def out_table():
        return pandas_df.head(n() + 1)

    @render.data_frame
    def out_data_frame():
        return pandas_df.head(n() + 1)

    @render.text
    def out_text():
        return f"Output text content. `input.radio_buttons()`: `{input.input_radio_buttons()}`"

    @render.text
    def out_text_verbatim():
        return f"Output text verbatim content. `input.radio_buttons()`: `{input.input_radio_buttons()}`"

    @render.ui
    def out_ui():
        return ui.p(
            ui.markdown(
                f"Output UI content. `input.radio_buttons()`: `{input.input_radio_buttons()}`"
            )
        )

    download_button_count = 0

    @render.download(filename=lambda: f"download_button-{session.ns}.csv")
    async def download_button():
        nonlocal download_button_count
        download_button_count += 1
        yield "session,type,count\n"
        yield f"{session.ns},button,{download_button_count}\n"

    download_link_count = 0

    @render.download(filename=lambda: f"download_link-{session.ns}.csv")
    async def download_link():
        nonlocal download_link_count
        download_link_count += 1
        yield "session,type,count\n"
        yield f"{session.ns},link,{download_link_count}\n"

    def render_input_txt(
        input_key: str,
        prefix_txt: str = "",
        prefix_id: str = "",
        preprocess: Callable[[object], str] | None = None,
    ) -> None:
        @output(id=f"status_{prefix_id}{input_key}")
        @render.text
        def _():
            value = getattr(input, input_key)()
            if preprocess is not None:
                value = preprocess(value)
            return f"{prefix_txt}ui.{input_key}: `{value}`"

    for x_input_key in x_input_keys:
        render_input_txt(
            x_input_key,
            prefix_txt="x.",
            prefix_id="x_",
        )

    for input_key in input_keys:
        # Manually handle `input_file`
        if input_key == "input_file":
            continue
        render_input_txt(input_key)

    def preprocess_file(x: Any) -> str:
        if isinstance(x, list):
            # Extract the name to avoid the temp folder path in output
            return typing.cast(
                str,
                x[0].get("name"),  # pyright: ignore[reportUnknownMemberType]
            )
        else:
            return str(x)

    render_input_txt("input_file", preprocess=preprocess_file)


# =============================================================================
# App that uses module
# =============================================================================
app_ui = ui.page_fluid(
    ui.input_action_button("reset", "Reset"),
    ui.input_action_button("update_global", "Update Global"),
    ui.input_action_button("update_mod1", "Update Module 1"),
    ui.input_action_button("update_mod2", "Update Module 2"),
    ui.tags.head(
        ui.tags.style(
            """
        .popover.popover {
            --bs-popover-max-width: 500px;
        }
        """
        )
    ),
    ui.popover(
        ui.input_action_button("ignore", "Explanation of test"),
        ui.markdown(
            """
            E2E test app added has a main session and two module sessions that have inputs and outputs. It makes sure that one module does not update the other module or the main session.

            If a component does not use `resolve_id()`, the global session will be updated and the module will be unchanged.

            ### Approach
            * Reset all sessions
            * Verify all sessions have been reset
            * Update the second module x3 times
            * Verify that main session and first module have not updated
            * Verify the second module has been updated

            ### Future addtions
            * What qualifies:
                * If the input/output/update method uses `resolve_id()` or `id` (outside of `session.send_custom_input(id=)`)
                * It can be placed into a module. (e.g. not `ui.page_navbar()`)
            * Inputs
                * Add the input into the `input_keys` (or `x_input_keys`) tuple
                * Add the input into the module ui definition
                * The input `id=` should be the same as the function name. Ex: `ui.input_action_button("input_action_button", "Title")`
                * Update `expect_mod_state()` to support the new input
                * Update `expect_default_mod_state()` to reflect the reset state of the new input
            * Outputs
                * Add the output into the module ui definition
                * If it needs to be on the screen to be updated (rare), add it near the top of the definition
                * Update `expect_outputs()` to support the new output
            """
        ),
        id="explanation",
    ),
    ui.layout_column_wrap(
        mod_x_ui("", "Global"),  # "" == Root
        mod_x_ui("mod1", "Module 1"),
        mod_x_ui("mod2", "Module 2"),
        width=1 / 3,
    ),
    # ui.h3("Inputs that are not in a module:"),
    # ui.output_text_verbatim("not_modules", placeholder=True),
)


def server(input: Inputs, output: Outputs, session: Session):
    mod_x_server(session.ns)  # Root
    mod_x_server("mod1")
    mod_x_server("mod2")

    # Check if in interactive mode
    # https://stackoverflow.com/a/64523765/591574
    if hasattr(sys, "ps1"):
        # Open the explanation popover
        ui.update_popover("explanation", show=True)

        # On button clicks, hide the explanation popover
        @reactive.effect(suspended=True)
        def _():
            input.reset()
            input.update_global()
            input.update_mod1()
            input.update_mod2()
            ui.update_popover("explanation", show=False)

    # Master function to update a module's features
    def update_session(
        session: Session,
        *,
        count: int = 1,
    ):
        letter = letters[count % len(letters)]
        on_off = count % 2 == 1
        with session_context(session):
            ui.update_accordion("accordion", show=letter)

            ui.update_checkbox("input_checkbox", value=on_off)
            checkbox_group_letters = letters.copy()
            checkbox_group_letters.remove(letter)
            ui.update_checkbox_group(
                "input_checkbox_group", selected=checkbox_group_letters
            )
            date_start = datetime.date(2023, 8, 24) + datetime.timedelta(days=count)
            ui.update_date("input_date", value=date_start)
            ui.update_date_range(
                "input_date_range",
                start=date_start + datetime.timedelta(days=1),
                end=date_start + datetime.timedelta(days=3),
            )
            ui.update_numeric("input_numeric", value=count)
            ui.update_text("input_password", value=f"password{count}")
            ui.update_radio_buttons("input_radio_buttons", selected=letter)
            ui.update_select("input_select", selected=letter)
            ui.update_selectize("input_selectize", selected=letter)
            ui.update_slider("input_slider", value=count)
            ui.update_text("input_text", value=f"text{count}")
            ui.update_text_area("input_text_area", value=f"text_area{count}")

            # Toggle elements
            if count == 0:
                # Open sidebar
                # https://github.com/posit-dev/py-shiny/issues/716
                # ui.update_sidebar("sidebar", value=True)
                if session.input.sidebar() is False:
                    ui.update_sidebar("sidebar", show=True)

                # Turn off switch
                ui.update_switch("input_switch", value=False)

                # Hide popover
                # https://github.com/posit-dev/py-shiny/issues/717
                # ui.update_popover("popover", show=False)
                if session.input.popover() is True:
                    ui.update_popover("popover", show=False)
                # Hide tooltip
                # https://github.com/posit-dev/py-shiny/issues/717
                if session.input.tooltip() is True:
                    ui.update_tooltip("tooltip", show=False)
            else:
                if session.input.sidebar() == on_off:
                    ui.update_sidebar("sidebar", show=not on_off)
                if session.input.input_switch() != on_off:
                    ui.update_switch("input_switch", value=on_off)
                if session.input.popover() != on_off:
                    ui.update_popover("popover", show=on_off)
                if session.input.tooltip() != on_off:
                    ui.update_tooltip("tooltip", show=on_off)

            ui.update_navs("navset_bar", selected=letter)
            ui.update_navs("navset_card_pill", selected=letter)
            ui.update_navs("navset_card_tab", selected=letter)
            ui.update_navs("navset_hidden", selected=letter)
            ui.update_navs("navset_pill", selected=letter)
            ui.update_navs("navset_tab", selected=letter)

    module_keys = (
        ("update_global", ""),
        ("update_mod1", "mod1"),
        ("update_mod2", "mod2"),
    )

    offsets: dict[str, int] = {}
    for _input_key, session_key in module_keys:
        offsets[session_key] = 0

    @reactive.effect
    def _():
        # trigger reactivity
        input.reset()
        with reactive.isolate():
            for input_key, session_key in module_keys:
                offsets[session_key] = input[input_key]()
                update_session(session_dict[session_key], count=0)

    def update_session_effect(*, input_key: str, session_key: str) -> None:
        @reactive.effect
        @reactive.event(input[input_key])
        def _():
            update_session(
                session_dict[session_key],
                count=input[input_key]() - offsets[session_key],
            )

    for input_key, session_key in module_keys:
        update_session_effect(input_key=input_key, session_key=session_key)

    # # ## Debug

    # @reactive.Effect
    # def _():
    #     print("here")
    #     reactive.invalidate_later(1)
    #     print(input._ns)
    #     print(
    #         [
    #             key
    #             for key in input._map.keys()
    #             if not key.startswith(".") and not key.startswith("mod")
    #         ]
    #     )


app = App(app_ui, server)

import os
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from shiny import App, render, ui
from shiny.ui._theme_brand import bootstrap_colors

# TODO: Move this into the test that runs this app
os.environ["SHINY_BRAND_YML_RAISE_UNMAPPED"] = "true"
theme = ui.Theme.from_brand(__file__)
# theme = ui.Theme()
theme.add_rules((Path(__file__).parent / "_colors.scss").read_text())

app_ui = ui.page_navbar(
    ui.nav_panel(
        "Input Output Demo",
        ui.layout_sidebar(
            ui.sidebar(
                ui.input_slider("slider1", "Numeric Slider Input", 0, 11, 11),
                ui.input_numeric("numeric1", "Numeric Input Widget", 30),
                ui.input_date("date1", "Date Input Component", value="2024-01-01"),
                ui.input_switch("switch1", "Binary Switch Input", True),
                ui.input_radio_buttons(
                    "radio1",
                    "Radio Button Group",
                    choices=["Option A", "Option B", "Option C", "Option D"],
                ),
                ui.input_action_button("action1", "Action Button"),
            ),
            ui.layout_columns(
                ui.value_box(
                    "Metric 1",
                    "100",
                    theme="primary",
                ),
                ui.value_box(
                    "Metric 2",
                    "200",
                    theme="secondary",
                ),
                ui.value_box(
                    "Metric 3",
                    "300",
                    theme="info",
                ),
            ),
            ui.card(
                ui.card_header("Plot Output"),
                ui.output_plot("plot1"),
            ),
            ui.card(
                ui.card_header("Text Output"),
                ui.output_text_verbatim("out_text1"),
            ),
        ),
    ),
    ui.nav_panel(
        "Widget Gallery",
        ui.layout_column_wrap(
            ui.card(
                ui.card_header("Button Variants"),
                ui.input_action_button("btn1", "Default"),
                ui.input_action_button("btn2", "Primary", class_="btn-primary"),
                ui.input_action_button("btn3", "Secondary", class_="btn-secondary"),
                ui.input_action_button("btn4", "Info", class_="btn-info"),
                ui.input_action_button("btn5", "Success", class_="btn-success"),
                ui.input_action_button("btn6", "Warning", class_="btn-warning"),
                ui.input_action_button("btn7", "Danger", class_="btn-danger"),
            ),
            ui.card(
                ui.card_header("Radio Button Examples"),
                ui.input_radio_buttons(
                    "radio2",
                    "Standard Radio Group",
                    ["Selection 1", "Selection 2", "Selection 3"],
                ),
                ui.input_radio_buttons(
                    "radio3",
                    "Inline Radio Group",
                    ["Option 1", "Option 2", "Option 3"],
                    inline=True,
                ),
            ),
            ui.card(
                ui.card_header("Checkbox Examples"),
                ui.input_checkbox_group(
                    "check1",
                    "Standard Checkbox Group",
                    ["Item 1", "Item 2", "Item 3"],
                ),
                ui.input_checkbox_group(
                    "check2",
                    "Inline Checkbox Group",
                    ["Choice A", "Choice B", "Choice C"],
                    inline=True,
                ),
            ),
            ui.card(
                ui.card_header("Select Input Widgets"),
                ui.input_selectize(
                    "select1",
                    "Selectize Input",
                    ["Selection A", "Selection B", "Selection C"],
                ),
                ui.input_select(
                    "select2",
                    "Multiple Select Input",
                    ["Item X", "Item Y", "Item Z"],
                    multiple=True,
                ),
            ),
            ui.card(
                ui.card_header("Text Input Widgets"),
                ui.input_text("text1", "Text Input"),
                ui.input_text_area(
                    "textarea1",
                    "Text Area Input",
                    "Default text content for the text area widget",
                ),
                ui.input_password("password1", "Password Input"),
            ),
            width=300,
            heights_equal=False,
        ),
    ),
    ui.nav_panel(
        "Colors",
        ui.fill.as_fill_item(
            ui.div(
                ui.div(ui.output_ui("ui_colors"), class_="container-sm"),
                class_="overflow-y-auto",
            )
        ),
    ),
    ui.nav_panel(
        "Documentation",
        ui.fill.as_fill_item(
            ui.div(
                ui.div(
                    ui.markdown(
                        """
                _Just in case it isn't obvious, this text was written by an LLM._

                # Component Documentation

                The Shiny for Python framework, available at [shiny.posit.co/py](https://shiny.posit.co/py/),
                provides a comprehensive set of UI components for building interactive web applications. These
                components are designed with **consistency and usability** in mind, making it easier for
                developers to create professional-grade applications.

                Our framework implements the `ui.page_navbar()` component as the primary navigation structure,
                allowing for intuitive organization of content across multiple views. Each view can contain
                various input and output elements, managed through the `ui.card()` container system.

                ## Component Architecture

                *The architecture of our application framework* emphasizes modularity and reusability. Key
                components like `ui.value_box()` and `ui.layout_column_wrap()` work together to create
                structured, responsive layouts that adapt to different screen sizes.

                <table class="table table-striped">
                <thead>
                <tr>
                <th>Component</th>
                <th>Implementation</th>
                <th>Use Case</th>
                <th>Status</th>
                </tr>
                </thead>
                <tbody>
                <tr>
                <td>Value Box</td>
                <td><code>ui.value_box()</code></td>
                <td>Metric Display</td>
                <td>Production Ready</td>
                </tr>
                <tr>
                <td>Card</td>
                <td><code>ui.card()</code></td>
                <td>Content Container</td>
                <td>Production Ready</td>
                </tr>
                <tr>
                <td>Layout</td>
                <td><code>ui.layout_column_wrap()</code></td>
                <td>Component Organization</td>
                <td>Production Ready</td>
                </tr>
                <tr>
                <td>Navigation</td>
                <td><code>ui.page_navbar()</code></td>
                <td>Page Structure</td>
                <td>Production Ready</td>
                </tr>
                </tbody>
                </table>

                ## Implementation Best Practices

                When implementing components, maintain consistent patterns in your code. Use the
                `@render` decorators for output functions and follow the reactive programming model
                with `@reactive.effect` for side effects.

                Error handling should be implemented at both the UI and server levels. For input
                validation, use the `req()` function to ensure all required values are present
                before processing.

                ## Corporate Brand Guidelines

                Effective corporate brand guidelines should accomplish several key objectives:

                1. **Visual Consistency**: Establish a clear color palette using our theming system.
                Primary colors should be defined using `class_="btn-primary"` and similar Bootstrap
                classes.

                2. *Typography Standards*: Maintain consistent font usage across all text elements.
                Headers should use the built-in styling provided by the `ui.card_header()` component.

                3. `Component Styling`: Apply consistent styling to UI elements such as buttons,
                cards, and value boxes. Use the theme parameter in components like
                `ui.value_box(theme="primary")`.

                4. **Layout Principles**: Follow a grid-based layout system using
                `ui.layout_column_wrap()` with appropriate width parameters to ensure consistent
                spacing and alignment.

                5. *Responsive Design*: Implement layouts that adapt gracefully to different screen
                sizes using the `fillable` parameter in page components.

                Remember that brand guidelines should serve as a framework for consistency while
                remaining flexible enough to accommodate future updates and modifications to the
                application interface.
                """
                    ),
                    class_="container-sm ",
                ),
                class_="overflow-y-auto",
            )
        ),
    ),
    ui.nav_spacer(),
    ui.nav_control(ui.input_dark_mode(id="color_mode")),
    title="brand.yml Demo",
    fillable=True,
    theme=theme,
)


def server(input, output, session):
    @render.plot
    def plot1():
        colors = {
            "foreground": theme.brand.color.foreground,
            "background": theme.brand.color.background,
            "primary": theme.brand.color.primary,
        }

        if theme.brand.color:
            colors.update(theme.brand.color.to_dict("theme"))

        if input.color_mode() == "dark":
            bg = colors["foreground"]
            fg = colors["background"]
            colors.update({"foreground": fg, "background": bg})

        x = np.linspace(0, input.numeric1(), 100)
        y = np.sin(x) * input.slider1()
        fig, ax = plt.subplots(facecolor=colors["background"])
        ax.plot(x, y, color=colors["primary"])
        ax.set_title("Sine Wave Output", color=colors["foreground"])
        ax.set_facecolor(colors["background"])
        ax.tick_params(colors=colors["foreground"])
        for spine in ax.spines.values():
            spine.set_edgecolor(colors["foreground"])
            spine.set_alpha(0.25)
        return fig

    @render.text
    def out_text1():
        return "\n".join(
            ["def example_function():", '    return "Function output text"']
        )

    @render.ui
    def ui_colors():
        colors = []
        # Replicates: https://getbootstrap.com/docs/5.3/customize/color/#all-colors
        # Source: https://github.com/twbs/bootstrap/blob/6e1f75f4/site/content/docs/5.3/customize/color.md?plain=1#L395-L409
        for color in ["gray", *bootstrap_colors]:
            if color in ["white", "black"]:
                continue

            colors += [
                ui.div(
                    ui.div(color, class_=f"p-3 mb-2 position-relative bd-{color}-500"),
                    *[
                        ui.div(f"{color}-{r}", class_=f"p-3 bd-{color}-{r}")
                        for r in range(100, 1000, 100)
                    ],
                    class_="mb-3",
                )
            ]

        return ui.TagList(
            ui.div(
                *[
                    ui.div(
                        ui.div(
                            color, class_=f"p-3 mb-2 position-relative text-bg-{color}"
                        ),
                        class_="col-md-3 mb-3",
                    )
                    for color in [
                        "primary",
                        "secondary",
                        "dark",
                        "light",
                        "info",
                        "success",
                        "warning",
                        "danger",
                    ]
                ],
                class_="row font-monospace",
            ),
            ui.div(
                *[
                    ui.div(
                        ui.div(color, class_=f"p-3 mb-2 position-relative bd-{color}"),
                        class_="col-md-3 mb-3",
                    )
                    for color in ["black", "white", "foreground", "background"]
                ],
                class_="row font-monospace",
            ),
            ui.layout_column_wrap(*colors, class_="font-monospace"),
        )


app = App(app_ui, server)

# To run this app:
#   python3 app.py

# Then point web browser to:
#   http://localhost:8000/

# Add parent directory to path, so we can find the prism module.
# (This is just a temporary fix)
import os
import sys

# This will load the shiny module dynamically, without having to install it.
# This makes the debug/run cycle quicker.
shiny_module_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, shiny_module_dir)

from shiny import *

ui = page_fluid(
    panel_title("Changing the values of inputs from the server"),
    row(
        column(
            3,
            panel_well(
                tags.h4("These inputs control the other inputs on the page"),
                input_text(
                    "control_label", "This controls some of the labels:", "LABEL TEXT"
                ),
                input_slider(
                    "control_num", "This controls values:", min=1, max=20, value=15
                ),
            ),
        ),
        column(
            3,
            panel_well(
                tags.h4("These inputs are controlled by the other inputs"),
                input_text("inText", "Text input:", value="start text"),
                input_numeric(
                    "inNumber", "Number input:", min=1, max=20, value=5, step=0.5
                ),
                input_numeric(
                    "inNumber2", "Number input 2:", min=1, max=20, value=5, step=0.5
                ),
                input_slider("inSlider", "Slider input:", min=1, max=20, value=15),
                input_slider(
                    "inSlider2", "Slider input 2:", min=1, max=20, value=(5, 15)
                ),
                input_slider(
                    "inSlider3", "Slider input 3:", min=1, max=20, value=(5, 15)
                ),
                input_date("inDate", "Date input:"),
                input_date_range("inDateRange", "Date range input:"),
            ),
        ),
        column(
            3,
            panel_well(
                input_checkbox("inCheckbox", "Checkbox input", value=False),
                input_checkbox_group(
                    "inCheckboxGroup",
                    "Checkbox group input:",
                    ("label 1", "option1", "label 2", "option2"),
                ),
                input_radio_buttons(
                    "inRadio",
                    "Radio buttons:",
                    ("label 1", "option1", "label 2", "option2"),
                ),
                input_select(
                    "inSelect",
                    "Select input:",
                    {"label 1": "option1", "label 2": "option2"},
                ),
                input_select(
                    "inSelect2",
                    "Select input 2:",
                    {"label 1": "option1", "label 2": "option2"},
                    multiple=True,
                ),
            ),
            navs_tab(
                nav("panel1", h2("This is the first panel.")),
                nav("panel2", h2("This is the second panel.")),
                id="inTabset",
            ),
        ),
    ),
)


def server(sess: ShinySession):
    @observe_async()
    async def _():
        # We'll use these multiple times, so use short var names for
        # convenience.
        c_label = sess.input["control_label"]
        c_num = sess.input["control_num"]

        print(c_label)
        print(c_num)

        # Text =====================================================
        # Change both the label and the text
        await update_text(
            "inText",
            label="New " + c_label,
            value="New text " + str(c_num),
        )

        # Number ===================================================
        # Change the value
        await update_numeric("inNumber", value=c_num)

        # Change the label, value, min, and max
        await update_numeric(
            "inNumber2",
            label="Number " + c_label,
            value=c_num,
            min=c_num - 10,
            max=c_num + 10,
            step=5,
        )

        # Slider input =============================================
        # Only label and value can be set for slider
        await update_slider("inSlider", label="Slider " + c_label, value=c_num)

        # Slider range input =======================================
        # For sliders that pick out a range, pass in a vector of 2
        # values.
        await update_slider("inSlider2", value=(c_num - 1, c_num + 1))

        # TODO: an NA means to not change that value (the low or high one)
        # await update_slider(
        #    "inSlider3",
        #    value=(NA, c_num+2)
        # )

        # Date input ===============================================
        # Only label and value can be set for date input
        await update_date("inDate", label="Date " + c_label, value=date(2013, 4, c_num))

        # Date range input =========================================
        # Only label and value can be set for date range input
        await update_date_range(
            "inDateRange",
            label="Date range " + c_label,
            start=date(2013, 1, c_num),
            end=date(2013, 12, c_num),
            min=date(2001, 1, c_num),
            max=date(2030, 1, c_num),
        )

        # # Checkbox ===============================================
        await update_checkbox("inCheckbox", value=c_num % 2)

        # Checkbox group ===========================================
        # Create a list of new options, where the name of the items
        # is something like 'option label x A', and the values are
        # 'option-x-A'.
        opts = zip(
            [f"option label {c_num} {type}" for type in ["A", "B"]],
            [f"option-{c_num}-{type}" for type in ["A", "B"]],
        )

        # Set the label, choices, and selected item
        await update_checkbox_group(
            "inCheckboxGroup",
            label="Checkbox group " + c_label,
            choices=tuple(opts),
            selected=f"option-{c_num}-A",
        )

        # Radio group ==============================================
        await update_radio_buttons(
            "inRadio",
            label="Radio " + c_label,
            choices=tuple(opts),
            selected=f"option-{c_num}-A",
        )
        # Select input =============================================
        # Create a list of new options, where the name of the items
        # is something like 'option label x A', and the values are
        # 'option-x-A'.
        await update_select(
            "inSelect",
            label="Select " + c_label,
            choices=dict(opts),
            selected=f"option-{c_num}-A",
        )

        # Can also set the label and select an item (or more than
        # one if it's a multi-select)
        await update_select(
            "inSelect2",
            label="Select label " + c_label,
            choices=dict(opts),
            selected=f"option-{c_num}-B",
        )

        # Tabset input =============================================
        # Change the selected tab.
        # The tabsetPanel must have been created with an 'id' argument
        await nav_select("inTabset", selected="panel2" if c_num % 2 else "panel1")


app = ShinyApp(ui, server, debug=True)

if __name__ == "__main__":
    app.run()

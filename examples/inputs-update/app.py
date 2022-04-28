from datetime import date

from shiny import *
from shiny.ui import tags, h2

app_ui = ui.page_fluid(
    ui.panel_title("Changing the values of inputs from the server"),
    ui.row(
        ui.column(
            4,
            ui.panel_well(
                tags.h4("These inputs control the other inputs on the page"),
                ui.input_text(
                    "control_label", "This controls some of the labels:", "LABEL TEXT"
                ),
                ui.input_slider(
                    "control_num", "This controls values:", min=1, max=20, value=15
                ),
            ),
        ),
        ui.column(
            4,
            ui.panel_well(
                tags.h4("These inputs are controlled by the other inputs"),
                ui.input_text("inText", "Text input:", value="start text"),
                ui.input_numeric(
                    "inNumber", "Number input:", min=1, max=20, value=5, step=0.5
                ),
                ui.input_numeric(
                    "inNumber2", "Number input 2:", min=1, max=20, value=5, step=0.5
                ),
                ui.input_slider("inSlider", "Slider input:", min=1, max=20, value=15),
                ui.input_slider(
                    "inSlider2", "Slider input 2:", min=1, max=20, value=(5, 15)
                ),
                ui.input_slider(
                    "inSlider3", "Slider input 3:", min=1, max=20, value=(5, 15)
                ),
                ui.input_date("inDate", "Date input:"),
                ui.input_date_range("inDateRange", "Date range input:"),
            ),
        ),
        ui.column(
            4,
            ui.panel_well(
                ui.input_checkbox("inCheckbox", "Checkbox input", value=False),
                ui.input_checkbox_group(
                    "inCheckboxGroup",
                    "Checkbox group input:",
                    {
                        "option1": "label 1",
                        "option2": "label 2",
                    },
                ),
                ui.input_radio_buttons(
                    "inRadio",
                    "Radio buttons:",
                    {
                        "option1": "label 1",
                        "option2": "label 2",
                    },
                ),
                ui.input_select(
                    "inSelect",
                    "Select input:",
                    {
                        "option1": "label 1",
                        "option2": "label 2",
                    },
                ),
                ui.input_select(
                    "inSelect2",
                    "Select input 2:",
                    {
                        "option1": "label 1",
                        "option2": "label 2",
                    },
                    multiple=True,
                ),
            ),
            ui.navset_tab(
                ui.nav("panel1", h2("This is the first panel.")),
                ui.nav("panel2", h2("This is the second panel.")),
                id="inTabset",
            ),
        ),
    ),
)


def server(input: Inputs, output: Outputs, session: Session):
    @reactive.Effect()
    def _():
        # We'll use these multiple times, so use short var names for
        # convenience.
        c_label = input.control_label()
        c_num = input.control_num()

        # Text =====================================================
        # Change both the label and the text
        ui.update_text(
            "inText",
            label="New " + c_label,
            value="New text " + str(c_num),
        )

        # Number ===================================================
        # Change the value
        ui.update_numeric("inNumber", value=c_num)

        # Change the label, value, min, and max
        ui.update_numeric(
            "inNumber2",
            label="Number " + c_label,
            value=c_num,
            min=c_num - 10,
            max=c_num + 10,
            step=5,
        )

        # Slider input =============================================
        # Only label and value can be set for slider
        ui.update_slider("inSlider", label="Slider " + c_label, value=c_num)

        # Slider range input =======================================
        # For sliders that pick out a range, pass in a vector of 2
        # values.
        ui.update_slider("inSlider2", value=(c_num - 1, c_num + 1))

        # Only change the upper handle
        ui.update_slider("inSlider3", value=(input.inSlider3()[0], c_num + 2))

        # Date input ===============================================
        # Only label and value can be set for date input
        ui.update_date("inDate", label="Date " + c_label, value=date(2013, 4, c_num))

        # Date range input =========================================
        # Only label and value can be set for date range input
        ui.update_date_range(
            "inDateRange",
            label="Date range " + c_label,
            start=date(2013, 1, c_num),
            end=date(2013, 12, c_num),
            min=date(2001, 1, c_num),
            max=date(2030, 1, c_num),
        )

        # # Checkbox ===============================================
        ui.update_checkbox("inCheckbox", value=c_num % 2)

        # Checkbox group ===========================================
        # Create a list of new options, where the name of the items
        # is something like 'option label x A', and the values are
        # 'option-x-A'.
        opt_labels = [f"option label {c_num} {type}" for type in ["A", "B"]]
        opt_vals = [f"option-{c_num}-{type}" for type in ["A", "B"]]
        opts_dict = dict(zip(opt_vals, opt_labels))

        # Set the label, choices, and selected item
        ui.update_checkbox_group(
            "inCheckboxGroup",
            label="Checkbox group " + c_label,
            choices=opts_dict,
            selected=f"option-{c_num}-A",
        )

        # Radio group ==============================================
        ui.update_radio_buttons(
            "inRadio",
            label="Radio " + c_label,
            choices=opts_dict,
            selected=f"option-{c_num}-A",
        )
        # Select input =============================================
        # Create a list of new options, where the name of the items
        # is something like 'option label x A', and the values are
        # 'option-x-A'.
        ui.update_select(
            "inSelect",
            label="Select " + c_label,
            choices=opts_dict,
            selected=f"option-{c_num}-A",
        )

        # Can also set the label and select an item (or more than
        # one if it's a multi-select)
        ui.update_select(
            "inSelect2",
            label="Select label " + c_label,
            choices=opts_dict,
            selected=f"option-{c_num}-B",
        )

        # Tabset input =============================================
        # Change the selected tab.
        # The tabsetPanel must have been created with an 'id' argument
        ui.update_navs("inTabset", selected="panel2" if c_num % 2 else "panel1")


app = App(app_ui, server, debug=True)

from shiny import *

ui = page_fluid(
    tags.p("The first checkbox group controls the second"),
    input_checkbox_group(
        "inCheckboxGroup", "Input checkbox", ["Item A", "Item B", "Item C"]
    ),
    input_checkbox_group(
        "inCheckboxGroup2", "Input checkbox 2", ["Item A", "Item B", "Item C"]
    ),
)


def server(session: ShinySession):
    @observe()
    def _():
        x = session.input["inCheckboxGroup"]
        print(x)

        if x is None:
            x = []
        elif isinstance(x, str):
            x = [x]

        # Can also set the label and select items
        update_checkbox_group(
            "inCheckboxGroup2",
            label="Checkboxgroup label " + str(len(x)),
            choices=x,
            selected=x,
        )


ShinyApp(ui, server).run()

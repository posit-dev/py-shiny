from shiny import App, Inputs, Outputs, Session, ui

ui_app = ui.page_fluid(
    ui.markdown(
        """
        # Hello World

        This is **markdown** and here is some `code`:

        ```python
        print('Hello world!')
        ```
        """
    )
)


def server(input: Inputs, output: Outputs, session: Session):
    pass


app = App(ui_app, server)

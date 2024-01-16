from shiny.express import input, ui

ui.markdown(
    """
    # Hello World

    This is **markdown** and here is some `code`:

    ```python
    print('Hello world!')
    ```
    """
)

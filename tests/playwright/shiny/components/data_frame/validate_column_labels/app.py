from palmerpenguins import load_penguins_raw  # pyright: ignore[reportMissingTypeStubs]

from shiny.express import render, ui

ui.h2("Column labels w/ and w/o filters")

ui.h3("With filters")


@render.data_frame
def w_filters():
    return render.DataGrid(
        data=load_penguins_raw().iloc[:, 1:4],
        filters=True,
    )


ui.h3("Without filters")


@render.data_frame
def wo_filters():
    return render.DataGrid(
        data=load_penguins_raw().iloc[:, 1:4],
        filters=True,
    )

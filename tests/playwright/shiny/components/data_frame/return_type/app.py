from palmerpenguins import load_penguins_raw  # pyright: ignore[reportMissingTypeStubs]

from shiny.express import render


@render.code
def first_code():
    return str(type(first_df.data()))


@render.code
def second_code():
    return str(type(second_df.data()))


@render.data_frame
def first_df():
    return render.DataGrid(data=load_penguins_raw())


@render.data_frame
def second_df():
    return first_df.data_view(selected=False)

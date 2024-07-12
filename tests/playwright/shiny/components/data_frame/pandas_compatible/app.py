from __future__ import annotations

from astropy.table import Table  # pyright: ignore[reportMissingTypeStubs]

from shiny.express import render, ui

t = Table()
t["a"] = [1, 2, 3, 4]
t["b"] = ["a", "b", "c", "d"]


ui.h2("Original Data")


@render.code
def code_original():
    return str(type(t))


@render.data_frame  # pyright: ignore[reportArgumentType]
def df_astropy():
    return t


@render.code
def code_astropy():
    return str(
        type(  # pyright: ignore[reportUnknownArgumentType]
            df_astropy.data()  # pyright: ignore[reportUnknownArgumentType,reportUnknownMemberType]
        )
    )


ui.h2(ui.code(".data()"))


@render.data_frame
def df_data():  # pyright: ignore[reportUnknownParameterType]
    return (
        df_astropy.data()  # pyright: ignore[reportUnknownVariableType,reportUnknownMemberType]
    )


@render.code
def code_data():
    return str(
        type(  # pyright: ignore[reportUnknownArgumentType]
            df_data.data()  # pyright: ignore[reportUnknownArgumentType,reportUnknownMemberType]
        )
    )

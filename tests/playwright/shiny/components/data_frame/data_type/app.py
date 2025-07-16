from __future__ import annotations

import modin.pandas as mpd  # pyright: ignore[reportMissingTypeStubs]
import narwhals.stable.v1 as nw
import palmerpenguins  # pyright: ignore[reportMissingTypeStubs]
import polars as pl
import pyarrow as pa

from shiny.express import render, ui

pd_df = palmerpenguins.load_penguins_raw().iloc[0:2, 0:2]

nw_df = nw.from_native(pd_df, eager_only=True)
pa_df = pa.table(pd_df)  # pyright: ignore[reportUnknownMemberType]
mpd_df = mpd.DataFrame(pd_df)
pl_df = pl.DataFrame(pd_df)


with ui.layout_columns():

    with ui.card():
        ui.h2("Original Pandas Data")

        @render.data_frame
        def pd_df_original():
            return render.DataGrid(
                data=pd_df,  # pyright: ignore[reportUnknownArgumentType]
                selection_mode="row",
            )

        "Selected row:"

        @render.data_frame
        def selected_pandas_row():
            return pd_df_original.data_view(selected=True)

        "Data type:"

        @render.code
        def pd_type():
            return str(type(pd_df))

        ui.markdown("`.data()` type:")

        @render.code
        def pd_data():
            return str(type(pd_df_original.data()))

        ui.markdown("`.data_view()` type:")

        @render.code
        def pd_data_view():
            return str(type(pd_df_original.data_view()))

        ui.markdown("`.data_view(selected=True)` type:")

        @render.code
        def pd_data_view_selected():
            return str(type(pd_df_original.data_view(selected=True)))

    with ui.card():
        ui.h2("Original narwhals Data")

        @render.data_frame
        def nw_df_original():
            return render.DataGrid(
                data=nw_df,
                selection_mode="row",
            )

        "Selected row:"

        @render.data_frame
        def selected_nw_row():
            return nw_df_original.data_view(selected=True)

        "Data type:"

        @render.code
        def nw_type():
            return str(type(nw_df))

        ui.markdown("`.data()` type:")

        @render.code
        def nw_data():
            return str(type(nw_df_original.data()))

        ui.markdown("`.data_view()` type:")

        @render.code
        def nw_data_view():
            return str(type(nw_df_original.data_view()))

        ui.markdown("`.data_view(selected=True)` type:")

        @render.code
        def nw_data_view_selected():
            return str(type(nw_df_original.data_view(selected=True)))

    with ui.card():
        ui.h2("Original PyArrow Data")

        @render.data_frame
        def pa_df_original():
            return render.DataGrid(
                data=pa_df,
                selection_mode="row",
            )

        "Selected row:"

        @render.data_frame
        def selected_pa_row():
            return pa_df_original.data_view(selected=True)

        "Data type:"

        @render.code
        def pa_type():
            return str(type(pa_df))

        ui.markdown("`.data()` type:")

        @render.code
        def pa_data():
            return str(type(pa_df_original.data()))

        ui.markdown("`.data_view()` type:")

        @render.code
        def pa_data_view():
            return str(type(pa_df_original.data_view()))

        ui.markdown("`.data_view(selected=True)` type:")

        @render.code
        def pa_data_view_selected():
            return str(type(pa_df_original.data_view(selected=True)))

    with ui.card():
        ui.h2("Modin Data")

        @render.data_frame
        def mpd_df_original():
            return render.DataGrid(
                data=mpd_df,
                selection_mode="row",
            )

        "Selected row:"

        @render.data_frame
        def selected_mpd_row():
            return mpd_df_original.data_view(selected=True)

        "Data type:"

        @render.code
        def mpd_type():
            return str(type(mpd_df))

        ui.markdown("`.data()` type:")

        @render.code
        def mpd_data():
            return str(type(mpd_df_original.data()))

        ui.markdown("`.data_view()` type:")

        @render.code
        def mpd_data_view():
            return str(type(mpd_df_original.data_view()))

        ui.markdown("`.data_view(selected=True)` type:")

        @render.code
        def mpd_data_view_selected():
            return str(type(mpd_df_original.data_view(selected=True)))

    with ui.card():
        ui.h2("Polars Data")

        @render.data_frame
        def pl_df_original():
            return render.DataGrid(
                data=pl_df,
                selection_mode="row",
            )

        "Selected row:"

        @render.data_frame
        def selected_pl_row():
            return pl_df_original.data_view(selected=True)

        "Data type:"

        @render.code
        def pl_type():
            return str(type(pl_df))

        ui.markdown("`.data()` type:")

        @render.code
        def pl_data():
            return str(type(pl_df_original.data()))

        ui.markdown("`.data_view()` type:")

        @render.code
        def pl_data_view():
            return str(type(pl_df_original.data_view()))

        ui.markdown("`.data_view(selected=True)` type:")

        @render.code
        def pl_data_view_selected():
            return str(type(pl_df_original.data_view(selected=True)))

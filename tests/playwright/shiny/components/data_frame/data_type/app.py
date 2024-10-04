from __future__ import annotations

import narwhals.stable.v1 as nw
import palmerpenguins  # pyright: ignore[reportMissingTypeStubs]

from shiny.express import render, ui

pd_df = palmerpenguins.load_penguins_raw().iloc[0:2, 0:2]

nw_df = nw.from_native(pd_df, eager_only=True)

with ui.layout_columns():

    with ui.card():

        ui.h2("Original Pandas Data")

        @render.data_frame
        def pd_df_original():
            return pd_df

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
            return nw_df

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

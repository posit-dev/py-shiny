from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

from htmltools import TagNode

from ...session._utils import require_active_session
from ._html import col_contains_shiny_html, maybe_as_cell_html
from ._tbl_data import PdDataFrame, frame_column_names
from ._types import FrameDtype, FrameJson

if TYPE_CHECKING:
    import pandas as pd


def serialize_frame_pd(df: "pd.DataFrame") -> FrameJson:
    import pandas as pd

    columns = frame_column_names(df)
    columns_set = set(columns)
    if len(columns_set) != len(columns):
        raise ValueError(
            "The column names of the pandas DataFrame are not unique."
            " This is not supported by the data_frame renderer."
        )

    # Currently, we don't make use of the index; drop it so we don't error trying to
    # serialize it or something
    df = df.reset_index(drop=True)

    # # Can we keep the original column information?
    # # Maybe we need to inspect the original columns for any "unknown" column type. See if it contains any HTML or Tag objects
    # for col in columns:
    #     if df[col].dtype.name == "unknown":
    #         print(df[col].to_list())
    #         raise ValueError(
    #             "The pandas DataFrame contains columns of type 'object'."
    #             " This is not supported by the data_frame renderer."
    #         )

    type_hints = serialize_numpy_dtypes(df)

    # Auto opt-in for html columns
    html_columns = [
        i for i, type_hint in enumerate(type_hints) if type_hint["type"] == "html"
    ]

    if len(html_columns) > 0:
        # Enable copy-on-write mode for the data;
        # Use `deep=False` to avoid copying the full data; CoW will copy the necessary data when modified

        with pd.option_context("mode.copy_on_write", True):
            df = df.copy(deep=False)
            session = require_active_session(None)

            def wrap_shiny_html_with_session(x: TagNode):
                return maybe_as_cell_html(x, session=session)

            for html_column in html_columns:
                # _upgrade_ all the HTML columns to `CellHtml` json objects
                df[df.columns[html_column]] = df[
                    df.columns[html_column]
                ].apply(  # pyright: ignore[reportUnknownMemberType]
                    wrap_shiny_html_with_session
                )

    res = json.loads(
        # {index: [index], columns: [columns], data: [values]}
        df.to_json(  # pyright: ignore[reportUnknownMemberType]
            None,
            orient="split",
            # note that date_format iso converts durations to ISO8601 Durations.
            # e.g. 1 Day -> P1DT0H0M0S
            # see https://en.wikipedia.org/wiki/ISO_8601#Durations
            date_format="iso",
            default_handler=str,
        )
    )

    res["typeHints"] = type_hints

    # print(json.dumps(res, indent=4))
    return res


def serialize_numpy_dtypes(df: PdDataFrame) -> list[FrameDtype]:
    return [
        serialize_pd_dtype(df[col])  # pyright: ignore[reportUnknownArgumentType]
        for col in df.columns
    ]


def serialize_pd_dtype(
    col: "pd.Series[Any]",
) -> FrameDtype:
    import pandas as pd

    t = pd.api.types.infer_dtype(col)
    # t can be any of: string, bytes, floating, integer, mixed-integer,
    #     mixed-integer-float, decimal, complex, categorical, boolean, datetime64,
    #     datetime, date, timedelta64, timedelta, time, period, mixed, unknown-array

    if t == "string":
        if col_contains_shiny_html(col):
            t = "html"
        else:
            pass
        # If no HTML (which is a str) is found, then it is a string! (Keep t as `"string"`)
    elif t in ["bytes", "floating", "integer", "decimal", "mixed-integer-float"]:
        t = "numeric"
    elif t == "categorical":
        return {
            "type": "categorical",
            "categories": [
                str(x)  # pyright: ignore[reportUnknownArgumentType]
                for x in col.cat.categories.to_list()  # pyright: ignore[reportUnknownVariableType, reportUnknownMemberType]
            ],
        }
    elif t in {"datetime64", "datetime"}:
        t = "datetime"
    elif t in {"timedelta", "timedelta64"}:
        t = "timedelta"
    else:
        if col_contains_shiny_html(col):
            t = "html"
        else:
            t = "unknown"

    return {"type": t}

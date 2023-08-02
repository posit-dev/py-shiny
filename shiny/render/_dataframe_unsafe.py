# This file exists solely because I found it hard to write typesafe code for
# manipulating numpy dtypes. Rather than litter many lines of code with pyright ignore
# directives, I've moved the problematic code here and disabled some pyright checks at
# the file level. If anyone knows how to make this code typesafe, we can get rid of this
# file.

from __future__ import annotations

import typing
from typing import Any

if typing.TYPE_CHECKING:
    import pandas as pd

# pyright: reportMissingTypeArgument=false
# pyright: reportUnknownArgumentType=false
# pyright: reportUnknownMemberType=false
# pyright: reportUnknownParameterType=false
# pyright: reportUnknownVariableType=false


def serialize_numpy_dtypes(df: "pd.DataFrame") -> list[dict[str, Any]]:
    return [serialize_numpy_dtype(col) for _, col in df.items()]


def serialize_numpy_dtype(
    col: "pd.Series",
) -> dict[str, Any]:
    import pandas as pd

    t = pd.api.types.infer_dtype(col)
    # t can be any of: string, bytes, floating, integer, mixed-integer,
    #     mixed-integer-float, decimal, complex, categorical, boolean, datetime64,
    #     datetime, date, timedelta64, timedelta, time, period, mixed, unknown-array

    res: dict[str, Any] = {}

    if t == "string":
        pass
    elif t in ["bytes", "floating", "integer", "decimal", "mixed-integer-float"]:
        t = "numeric"
    elif t == "categorical":
        res["categories"] = [str(x) for x in col.cat.categories.to_list()]
    else:
        t = "unknown"

    res["type"] = t

    return res

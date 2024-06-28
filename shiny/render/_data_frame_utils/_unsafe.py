# This file exists solely because I found it hard to write typesafe code for
# manipulating numpy dtypes. Rather than litter many lines of code with pyright ignore
# directives, I've moved the problematic code here and disabled some pyright checks at
# the file level. If anyone knows how to make this code typesafe, we can get rid of this
# file.

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal, Protocol, Union, runtime_checkable

from htmltools import HTML, MetadataNode, Tagifiable

from ..._typing_extensions import TypedDict, TypeGuard
from ._tbl_data import PdDataFrame, SeriesLike

if TYPE_CHECKING:
    import pandas as pd

# pyright: reportMissingTypeArgument=false
# pyright: reportUnknownArgumentType=false
# pyright: reportUnknownMemberType=false
# pyright: reportUnknownParameterType=false
# pyright: reportUnknownVariableType=false
# pyright: reportAttributeAccessIssue=false
# pyrigth: reportMissingParameterType=false


class DataFrameDtypeSubset(TypedDict):
    type: Literal["numeric", "string", "html", "datetime", "timedelta", "unknown"]


class DataFrameDtypeCategories(TypedDict):
    type: Literal["categorical"]
    categories: list[str]


DataFrameDtype = Union[
    DataFrameDtypeSubset,
    DataFrameDtypeCategories,
]


def serialize_numpy_dtypes(df: PdDataFrame) -> list[DataFrameDtype]:
    return [serialize_numpy_dtype(col) for _, col in df.items()]


def col_contains_shiny_html(col: SeriesLike) -> bool:
    return any(is_shiny_html(val) for _, val in enumerate(col))


def serialize_numpy_dtype(
    col: "pd.Series[Any]",
) -> DataFrameDtype:
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
            "categories": [str(x) for x in col.cat.categories.to_list()],
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


# TODO-future; Replace this class with `htmltools.ReprHtml` when it is publically available. Even better... there should be a "is tag-like" method in htmltools that determines if the object could be enhanced by rendering
@runtime_checkable
class ReprHtml(Protocol):
    """
    Objects with a `_repr_html_()` method.
    """

    def _repr_html_(self) -> str: ...


# TODO-barret-test; Add test to assert the union type of `TagNode` contains `str` and (HTML | Tagifiable | MetadataNode | ReprHtml). Until a `is tag renderable` method is available in htmltools, we need to check for these types manually and must stay in sync with the `TagNode` union type.
# TODO-barret-future; Use `TypeIs[HTML | Tagifiable | MetadataNode | ReprHtml]` when it is available from typing_extensions
def is_shiny_html(val: Any) -> TypeGuard[HTML | Tagifiable | MetadataNode | ReprHtml]:
    return isinstance(val, (HTML, Tagifiable, MetadataNode, ReprHtml))

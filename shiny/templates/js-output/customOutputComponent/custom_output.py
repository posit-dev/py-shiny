# from pathlib import Path
from htmltools import Tag, HTMLDependency
from pathlib import PurePath

from shiny.render.transformer import (
    output_transformer,
    resolve_value_fn,
    TransformerMetadata,
    ValueFn,
)
from shiny.module import resolve_id


# This object is used to let Shiny know where the dependencies needed to run
# our component all live. In this case, we're just using a single javascript
# file but we could also include CSS.
custom_output_deps = HTMLDependency(
    "shiny-custom-output",
    "1.0.0",
    source={
        "package": "customOutputComponent",
        "subdir": str(PurePath(__file__).parent / "distjs"),
    },
    script={"src": "index.js", "type": "module"},
)


@output_transformer()
async def render_custom_output(
    _meta: TransformerMetadata,
    _fn: ValueFn[int | None],
):
    res = await resolve_value_fn(_fn)
    if res is None:
        return None

    if not isinstance(res, int):
        # Throw an error if the value is not a dataframe
        raise TypeError(f"Expected a integer, got {type(res)}. ")

    # Get data from dataframe as a list of lists where each inner list is a
    # row, column names as array of strings and types of each column as an
    # array of strings
    return {"value": res}


def custom_output(id, height="200px"):
    """
    A shiny output. To be paired with
    `render.custom_output` decorator.
    """
    return Tag(
        "shiny-custom-output",
        custom_output_deps,
        # Use resolve_id so that our component will work in a module
        id=resolve_id(id),
    )

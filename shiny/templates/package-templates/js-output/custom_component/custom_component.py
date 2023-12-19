# from pathlib import Path
from pathlib import PurePath

from htmltools import HTMLDependency, Tag

from shiny.module import resolve_id
from shiny.render.transformer import (
    TransformerMetadata,
    ValueFn,
    output_transformer,
    resolve_value_fn,
)

# This object is used to let Shiny know where the dependencies needed to run
# our component all live. In this case, we're just using a single javascript
# file but we could also include CSS.
custom_component_deps = HTMLDependency(
    "custom-component",
    "1.0.0",
    source={
        "package": "custom_component",
        "subdir": str(PurePath(__file__).parent / "distjs"),
    },
    script={"src": "index.js", "type": "module"},
)


@output_transformer()
async def render_custom_component(
    _meta: TransformerMetadata,
    _fn: ValueFn[int | None],
):
    res = await resolve_value_fn(_fn)
    if res is None:
        return None

    if not isinstance(res, int):
        # Throw an error if the value is not an integer.
        raise TypeError(f"Expected a integer, got {type(res)}. ")

    # Send the results to the client. Make sure that this is a serializable
    # object and matches what is expected in the javascript code.
    return {"value": res}


def custom_component(id: str, height: str = "200px"):
    """
    A shiny output. To be paired with
    `render_custom_component` decorator.
    """
    return Tag(
        "custom-component",
        custom_component_deps,
        # Use resolve_id so that our component will work in a module
        id=resolve_id(id),
    )

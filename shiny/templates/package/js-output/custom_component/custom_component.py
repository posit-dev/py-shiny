# from pathlib import Path
from pathlib import PurePath
from typing import Optional

from htmltools import HTMLDependency, Tag

from shiny.module import resolve_id
from shiny.render.renderer import Jsonifiable, Renderer, ValueFn

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


class render_custom_component(Renderer[int]):
    """
    Render a value in a custom component.
    """

    # The UI used within Shiny Express mode
    def auto_output_ui(self) -> Tag:
        return custom_component(self.output_id, height=self.height)

    # The init method is used to set up the renderer's parameters.
    # If no parameters are needed, then the `__init__()` method can be omitted.
    def __init__(self, _fn: Optional[ValueFn[int]] = None, *, height: str = "200px"):
        super().__init__(_fn)
        self.height: str = height

    # Transforms non-`None` values into a `Jsonifiable` object.
    # If you'd like more control on when and how the value is rendered,
    # please use the `async def render(self)` method.
    async def transform(self, value: int) -> Jsonifiable:
        # Send the results to the client. Make sure that this is a serializable
        # object and matches what is expected in the javascript code.
        return {"value": int(value)}


def custom_component(id: str, height: str = "200px") -> Tag:
    """
    A shiny UI output.

    To be paired with `render_custom_component` decorator within the Shiny server.
    """
    return Tag(
        "custom-component",
        custom_component_deps,
        # Use resolve_id so that our component will work in a module
        id=resolve_id(id),
    )

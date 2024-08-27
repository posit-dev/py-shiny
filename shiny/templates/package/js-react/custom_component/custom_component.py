from pathlib import PurePath

from htmltools import HTMLDependency, Tag

from shiny.module import resolve_id
from shiny.render.renderer import Jsonifiable, Renderer

# This object is used to let Shiny know where the dependencies needed to run
# our component all live. In this case, we're just using a single javascript
# file but we could also include CSS.
custom_component_deps = HTMLDependency(
    "custom_component",
    "1.0.0",
    source={
        "package": "custom_component",
        "subdir": str(PurePath(__file__).parent / "distjs"),
    },
    script={"src": "index.js", "type": "module"},
)


def input_custom_component(id: str):
    """
    A shiny input.
    """
    return Tag(
        # This is the name of the custom tag we created with our webcomponent
        "custom-component-input",
        custom_component_deps,
        # Use resolve_id so that our component will work in a module
        id=resolve_id(id),
    )


# Output component
class render_custom_component(Renderer[str]):
    """
    Render a value in a custom component.
    """

    # The UI used within Shiny Express mode
    def auto_output_ui(self) -> Tag:
        return output_custom_component(self.output_id)

    # # There are no parameters being supplied to the `output_custom_component` rendering function.
    # # Therefore, we can omit the `__init__()` method.
    # def __init__(self, _fn: Optional[ValueFn[int]] = None, *, extra_arg: str = "bar"):
    #     super().__init__(_fn)
    #     self.extra_arg: str = extra_arg

    # Transforms non-`None` values into a `Jsonifiable` object.
    # If you'd like more control on when and how the value is rendered,
    # please use the `async def render(self)` method.
    async def transform(self, value: str) -> Jsonifiable:
        # Send the results to the client. Make sure that this is a serializable
        # object and matches what is expected in the javascript code.
        return {"value": str(value)}


def output_custom_component(id: str):
    """
    Show a color
    """
    return Tag(
        "custom-component-output",
        custom_component_deps,
        id=resolve_id(id),
    )

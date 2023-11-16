from pathlib import PurePath

from htmltools import HTMLDependency, Tag

from shiny.module import resolve_id

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


def custom_component(id: str):
    """
    A shiny input.
    """
    return Tag(
        # This is the name of the custom tag we created with our webcomponent
        "custom-component",
        custom_component_deps,
        # Use resolve_id so that our component will work in a module
        id=resolve_id(id),
    )

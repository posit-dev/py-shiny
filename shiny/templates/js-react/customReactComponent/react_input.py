from htmltools import Tag, HTMLDependency
from pathlib import PurePath
from shiny.module import resolve_id

# This object is used to let Shiny know where the dependencies needed to run
# our component all live. In this case, we're just using a single javascript
# file but we could also include CSS.
custom_input_deps = HTMLDependency(
    "shiny-custom-input",
    "1.0.0",
    source={
        "package": "customReactComponent",
        "subdir": str(PurePath(__file__).parent / "distjs"),
    },
    script={"src": "index.js", "type": "module"},
)


def react_input(id):
    """
    A shiny input built with React!
    """
    return Tag(
        "custom-react-input",
        custom_input_deps,
        # Use resolve_id so that our component will work in a module
        id=resolve_id(id),
    )

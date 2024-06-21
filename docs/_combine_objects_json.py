import json
from dataclasses import asdict, dataclass
from typing import Literal, TypedDict


@dataclass
class QuartodocObject:
    project: str
    version: str
    count: int
    items: list["QuartodocObjectItem"]


@dataclass
class QuartodocObjectItem:
    name: str
    domain: str

    # function: "shiny.ui.page_sidebar"
    # class: "shiny.render.renderer._renderer.Renderer"
    # attribute: "shiny.render.renderer._renderer.Renderer.output_id"
    role: Literal["function", "class", "attribute", "module"]
    priority: str
    uri: str
    dispname: str


def read_objects_file(path: str) -> QuartodocObject:
    with open(path) as file:
        content = json.load(file)
    items = [QuartodocObjectItem(**item) for item in content.pop("items")]
    return QuartodocObject(**content, items=items)


def write_objects_file(objects: QuartodocObject, path: str) -> None:
    with open(path, "w") as file:
        json.dump(objects, file, indent=4, default=lambda dc: dc.__dict__)


print("\nCombining objects json files...")
objects_core = read_objects_file("_objects_core.json")
objects_express = read_objects_file("_objects_express.json")
objects_test = read_objects_file("_objects_test.json")

items_map: dict[str, QuartodocObjectItem] = {}

for item in [*objects_core.items, *objects_express.items, *objects_test.items]:
    if item.name in items_map:
        continue
    items_map[item.name] = item

objects_ret = QuartodocObject(
    project="shiny",
    version="1",
    count=len(items_map.values()),
    items=[*items_map.values()],
)


print("Core:", objects_core.count)
print("Express:", objects_express.count)
print("Testing:", objects_test.count)
print("Combined:", objects_ret.count)

# Save combined objects file info
write_objects_file(objects_ret, "objects.json")

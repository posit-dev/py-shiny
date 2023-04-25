from __future__ import annotations

from typing import Protocol

from htmltools import Tag, TagChild

from shiny._typing_extensions import TypeGuard


class CardItem:
    def __init__(
        self,
        item: Tag,
    ):
        self.item = item

    def tagify(self) -> Tag:
        return self.item.tagify()


# @describeIn card_body Mark an object as a card item. This will prevent the
#   [card()] from putting the object inside a `wrapper` (i.e., a
#   `card_body()`).
# @param x an object to test (or coerce to) a card item.
# @export
def as_card_item(x: Tag) -> CardItem:
    return CardItem(item=x)


def is_card_item(x: object) -> TypeGuard[CardItem]:
    return isinstance(x, CardItem)


# https://mypy.readthedocs.io/en/stable/protocols.html#callback-protocols
class WrapperCallable(Protocol):
    def __call__(self, *args: TagChild) -> CardItem:
        ...


def as_card_items(
    *children: TagChild | None, wrapper: WrapperCallable | None
) -> list[CardItem] | list[TagChild]:
    # We don't want NULLs creating empty card bodies
    children_vals = [child for child in children if child is not None]

    if not callable(wrapper):
        return children_vals

    # Any children that are `is.card_item` should be included verbatim. Any
    # children that are not, should be wrapped in card_body(). Consecutive children
    # that are not card_item, should be wrapped in a single card_body().
    state = "asis"  # "wrap" | "asis"
    new_children: list[CardItem] = []
    children_to_wrap: list[TagChild] = []

    def wrap_children():
        nonlocal children_to_wrap
        wrapped_children = wrapper(*children_to_wrap)
        new_children.append(wrapped_children)
        children_to_wrap = []

    for child in children_vals:
        if is_card_item(child):
            if state == "wrap":
                wrap_children()
            state = "asis"
            new_children.append(child)
        else:
            # Not a card, collect it for wrapping
            state = "wrap"
            children_to_wrap.append(child)
    if state == "wrap":
        wrap_children()

    return new_children

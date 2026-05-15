import sys

from htmltools import Tag, Tagifiable, TagList


# A decorator used for `def` statements. It makes sure that any `def` statement which
# returns a tag-like object, or one with a `_repr_html` method, will be passed on to
# the current sys.displayhook.
def _expressify_decorator_function_def(fn: object) -> object:
    # Narrowing `object` via isinstance against generic Tag/TagList yields
    # `Tag[Unknown] | TagList[Unknown]` arms which leak Unknown into the
    # surrounding return type. The signature stays `object -> object`, so
    # suppress the narrowed-Unknown report at the call site.
    if isinstance(fn, (Tag, TagList, Tagifiable)) or hasattr(fn, "_repr_html_"):
        sys.displayhook(fn)  # pyright: ignore[reportUnknownArgumentType]

    return fn  # pyright: ignore[reportUnknownVariableType]

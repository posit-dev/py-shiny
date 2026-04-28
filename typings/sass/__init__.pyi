from collections.abc import Mapping, Sequence
from typing import Any, Literal, overload

@overload
def compile(
    *,
    string: str,
    output_style: Literal["nested", "expanded", "compact", "compressed"] = ...,
    source_comments: bool = ...,
    source_map_contents: bool = ...,
    source_map_embed: bool = ...,
    omit_source_map_url: bool = ...,
    source_map_root: str | None = ...,
    include_paths: Sequence[str] = ...,
    precision: int = ...,
    custom_functions: Any = ...,
    indented: bool = ...,
    importers: Any = ...,
    custom_import_extensions: Any = ...,
) -> str: ...
@overload
def compile(**kwargs: Any) -> str | tuple[str, str] | None: ...

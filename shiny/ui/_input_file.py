from __future__ import annotations

__all__ = ("input_file",)

from typing import Literal, Optional

from htmltools import Tag, TagChild, css, div, span, tags

from .._docstring import add_example
from .._namespaces import resolve_id
from ._utils import shiny_input_label


@add_example()
def input_file(
    id: str,
    label: TagChild,
    *,
    multiple: bool = False,
    accept: Optional[str | list[str]] = None,
    width: Optional[str] = None,
    button_label: str = "Browse...",
    placeholder: str = "No file selected",
    capture: Optional[Literal["environment", "user"]] = None,
) -> Tag:
    """
    Create a file upload control that can be used to upload one or more files.

    Parameters
    ----------
    id
        An input id.
    label
        An input label.
    multiple
        Whether the user should be allowed to select and upload multiple files at once.
    accept
        Unique file type specifier(s) which give the browser a hint as to the type of
        file the server expects. Many browsers use this to prevent the user from
        selecting an invalid file. Examples of valid values include a case insensitive
        extension (e.g. ``.csv`` or ``.rds``), a valid MIME type (e.g. ``text/plain`` or
        ``application/pdf``) or one of ``audio/*``, ``video/*``, or ``image/*`` meaning
        any audio, video, or image type, respectively.
    width
        The CSS width, e.g. '400px', or '100%'
    button_label
        The label used on the button.
    placeholder
        The text to show on the input before a file has been uploaded.
    capture
        On mobile devices, this can be used to open the device's camera for input. If
        "environment", it will open the rear-facing camera. If "user", it will open the
        front-facing camera. By default, it will accept either still photos or video. To
        accept only still photos, use ``accept="image/*"``; to accept only video, use
        ``accept="video/*"``.

    Returns
    -------
    :
        A UI element.

    Notes
    -----

    ::: {.callout-note title="Server value"}
    A list of dictionaries (one for each file upload) with the following keys:

    * name: The filename provided by the web browser. This is *not* the path to read
        to get at the actual data that was uploaded (see 'datapath').
    * size: The size of the uploaded data, in bytes.
    * type: The MIME type reported by the browser (for example, 'text/plain'), or
        empty string if the browser didn't know.
    * datapath: The path to a temp file that contains the data that was uploaded.
        This file may be deleted if the user performs another upload operation.
    :::

    See Also
    --------
    ~shiny.ui.download_button
    """

    if isinstance(accept, str):
        accept = [accept]

    btn_file = span(
        button_label,
        tags.input(
            id=resolve_id(id),
            name=id,
            type="file",
            multiple="multiple" if multiple else None,
            accept=",".join(accept) if accept else None,
            capture=capture,
            # Don't use "display: none;" style, which causes keyboard accessibility issue; instead use the following workaround: https://css-tricks.com/places-its-tempting-to-use-display-none-but-dont/
            style="position: absolute !important; top: -99999px !important; left: -99999px !important;",
        ),
        class_="btn btn-default btn-file",
    )
    return div(
        shiny_input_label(id, label),
        div(
            tags.label(btn_file, class_="input-group-btn input-group-prepend"),
            tags.input(
                type="text",
                class_="form-control",
                placeholder=placeholder,
                readonly="readonly",
            ),
            class_="input-group",
        ),
        div(
            div(class_="progress-bar"),
            id=id + "_progress",
            class_="progress active shiny-file-input-progress",
        ),
        class_="form-group shiny-input-container",
        style=css(width=width),
    )

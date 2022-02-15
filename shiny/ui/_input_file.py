__all__ = ("input_file",)

from typing import Optional, List

from htmltools import tags, Tag, div, span, css, TagChildArg

from .._docstring import add_example
from ._utils import shiny_input_label


@add_example()
def input_file(
    id: str,
    label: TagChildArg,
    multiple: bool = False,
    accept: Optional[List[str]] = None,
    width: Optional[str] = None,
    button_label: str = "Browse...",
    placeholder: str = "No file selected",
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
        file the server expects. Many browsers use this prevent the user from selecting
        an invalid file. See the note below for more details.
    width
        The CSS width, e.g. '400px', or '100%'
    button_label
        The label used on the button.
    placeholder
        The text to show on the input before a file has been uploaded.

    Returns
    -------
    A UI element.

    Note
    ----
    A unique file type specifier (i.e. a string provided to the **accept** parameter)
    can be any of the following:

    * A case insensitive extension like ``.csv`` or ``.rds``.

    * A valid MIME type, like ``text/plain`` or ``application/pdf``

    * One of ``audio/*``, ``video/*``, or ``image/*`` meaning any audio, video, or image
      type, respectively.

    See Also
    --------
    ~shiny.ui.download_button
    """

    btn_file = span(
        button_label,
        tags.input(
            id=id,
            name=id,
            type="file",
            multiple="multiple" if multiple else None,
            accept=",".join(accept) if accept else None,
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

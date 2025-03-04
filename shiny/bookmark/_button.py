from typing import Optional

from htmltools import HTML, Tag, TagAttrValue, TagChild

from .._namespaces import resolve_id
from ..types import MISSING, MISSING_TYPE
from ..ui._input_action_button import input_action_button

BOOKMARK_ID = "._bookmark_"


#' Create a button for bookmarking/sharing
#'
#' A `bookmarkButton` is a [actionButton()] with a default label
#' that consists of a link icon and the text "Bookmark...". It is meant to be
#' used for bookmarking state.
#'
#' @inheritParams actionButton
#' @param title A tooltip that is shown when the mouse cursor hovers over the
#'   button.
#' @param id An ID for the bookmark button. The only time it is necessary to set
#'   the ID unless you have more than one bookmark button in your application.
#'   If you specify an input ID, it should be excluded from bookmarking with
#'   [setBookmarkExclude()], and you must create an observer that
#'   does the bookmarking when the button is pressed. See the examples below.
#'
#' @seealso [enableBookmarking()] for more examples.
#'
#' @examples
#' ## Only run these examples in interactive sessions
#' if (interactive()) {
#'
#' # This example shows how to use multiple bookmark buttons. If you only need
#' # a single bookmark button, see examples in ?enableBookmarking.
#' ui <- function(request) {
#'   fluidPage(
#'     tabsetPanel(id = "tabs",
#'       tabPanel("One",
#'         checkboxInput("chk1", "Checkbox 1"),
#'         bookmarkButton(id = "bookmark1")
#'       ),
#'       tabPanel("Two",
#'         checkboxInput("chk2", "Checkbox 2"),
#'         bookmarkButton(id = "bookmark2")
#'       )
#'     )
#'   )
#' }
#' server <- function(input, output, session) {
#'   # Need to exclude the buttons from themselves being bookmarked
#'   setBookmarkExclude(c("bookmark1", "bookmark2"))
#'
#'   # Trigger bookmarking with either button
#'   observeEvent(input$bookmark1, {
#'     session$doBookmark()
#'   })
#'   observeEvent(input$bookmark2, {
#'     session$doBookmark()
#'   })
#' }
#' enableBookmarking(store = "url")
#' shinyApp(ui, server)
#' }
#' @export
def input_bookmark_button(
    label: TagChild = "Bookmark...",
    *,
    icon: TagChild | MISSING_TYPE = MISSING,
    width: Optional[str] = None,
    disabled: bool = False,
    # id: str = "._bookmark_",
    title: str = "Bookmark this application's state and get a URL for sharing.",
    **kwargs: TagAttrValue,
) -> Tag:
    resolved_id = resolve_id(BOOKMARK_ID)
    if isinstance(icon, MISSING_TYPE):
        icon = HTML("&#x1F517;")

    return input_action_button(
        resolved_id,
        label,
        icon=icon,
        title=title,
        width=width,
        disabled=disabled,
        **kwargs,
    )

from htmltools import *
from typing import Optional, Dict, Any
from .input_utils import *
from .html_dependencies import selectize_deps, jqui_deps


def input_selectize(id: str, options: Dict[str, Any] = {}, **kwargs: TagAttrArg):
    # Make sure accessibility plugin is included by default
    if not options.get("plugins", None):
        options["plugins"] = []
    if "selectize-plugin-a11y" not in options["plugins"]:
        options["plugins"].append("selectize-plugin-a11y")
    deps = [selectize_deps()]
    if "drag_drop" in options["plugins"]:
        deps.append(jqui_deps())
    return jsx_tag("InputSelectize")(deps, id=id, options=options, **kwargs)


def input_select(
    id: str,
    label: str,
    choices,
    selected: Optional[str] = None,
    multiple: bool = False,
    selectize: bool = True,
    width: Optional[str] = None,
    size: Optional[str] = None,
):
    return jsx_tag("InputSelect")(
        selectize_deps(),
        id=id,
        label=label,
        choices=choices,
        selected=selected,
        multiple=multiple,
        selectize=selectize,
        width=width,
        size=size,
    )


# def input_selectize(id, options: Dict[str, Any]={}, **kwargs):
#   return selectize_it(id, input_select(id, selectize=False, **kwargs), options)
#
# def input_select(id: str, label: str, choices, selected: Optional[str] = None, multiple: bool = False, selectize: bool = True, width: Optional[str] = None, size: Optional[str] = None):
#   # resolve names
#   choices = choicesWithNames(choices)
#
#   # default value if it's not specified
#   if not selected and not multiple:
#     selected = firstChoice(choices)
#
#   if size and selectize:
#     raise Exception("'size' is not compatible with 'selectize=True'.")
#
#   # create select tag and add options
#   selectTag = tags.select(
#     selectOptions(choices, selected, id, selectize),
#     id = id, size = size, multiple = "multiple" if multiple else None,
#     class_="form-control" if not selectize else None,
#   )
#
#   # return label and select tag
#   container = div(
#     shiny_input_label(id, label),
#     div(selectTag),
#     class_="form-group shiny-input-container",
#     style=f"width: {width};" if width else None
#   )
#
#   if not selectize:
#     return container
#
#   return selectize_it(id, container, None, nonempty=not multiple and not "" in choices)
#
# firstChoice <- function(choices) {
#   if (length(choices) == 0L) return()
#   choice <- choices[[1]]
#   if (is.list(choice)) firstChoice(choice) else choice
# }
#
# # Create tags for each of the options; use <optgroup> if necessary.
# # This returns a HTML string instead of tags for performance reasons.
# def selectOptions(choices, selected: Optional[str]=None, id: str, perfWarning: bool=False):
#   if (length(choices) >= 1000) {
#     warning("The select input \"", inputId, "\" contains a large number of ",
#       "options; consider using server-side selectize for massively improved ",
#       "performance. See the Details section of the ?selectizeInput help topic.",
#       call. = FALSE)
#   }
#
#   return mapply(choices, names(choices), FUN = function(choice, label) {
#     if (is.list(choice)) {
#       # If sub-list, create an optgroup and recurse into the sublist
#       sprintf(
#         '<optgroup label="%s">\n%s\n</optgroup>',
#         htmlEscape(label, TRUE),
#         selectOptions(choice, selected, inputId, perfWarning)
#       )
#
#     } else {
#       # If single item, just return option string
#       sprintf(
#         '<option value="%s"%s>%s</option>',
#         htmlEscape(choice, TRUE),
#         if (choice %in% selected) ' selected' else '',
#         htmlEscape(label)
#       )
#     }
#   })
#
# # given a select input and its id, selectize it
# def selectize_it(id, select, options, nonempty = False):
#   if not options.get("plugins", None):
#     options["plugins"] = []
#
#   # Make sure accessibility plugin is included
#   if 'selectize-plugin-a11y' not in options["plugins"]:
#     options["plugins"].append('selectize-plugin-a11y')
#
#   deps = [selectize_deps()]
#   if 'drag_drop' in options["plugins"]:
#     deps.append(jqui_deps())
#
#   res = checkAsIs(options)
#
#   # Insert script on same level as <select> tag
#   select.children[1].append(
#       tags.script(
#           html(json.dumps(res.options)),
#           type='application/json',
#           data_for=id, data_nonempty='' if nonempty else None,
#           data_eval=html(json.dumps(res.eval)) if res.eval else None
#       )
#   )
#
#   return select
#
#
# # need <optgroup> when choices contains sub-lists
# #needOptgroup <- function(choices) {
# #  any(vapply(choices, is.list, logical(1)))
# #}
#
# #checkAsIs < - function(options) {
# #    evalOptions < - if (length(options)) {
# #        nms < - names(options)
# #        if (length(nms) == 0L | | any(nms == ""))
# #        stop("'options' must be a named list")
# #        i < - unlist(lapply(options, function(x) {
# #            is .character(x) & & inherits(x, "AsIs")
# #        }))
# #        if (any(i)) {
# #            options[i] < - lapply(options[i], paste, collapse="\n")
# #            nms[i]
# #        }
# #    }
# #    list(options=options, eval=evalOptions)
# #}
#

selectInput <- function(inputId, label, choices, selected = NULL,
  multiple = FALSE, selectize = TRUE, width = NULL,
  size = NULL) {

  selected <- restoreInput(id = inputId, default = selected)

  # resolve names
  choices <- choicesWithNames(choices)

  # default value if it's not specified
  if (is.null(selected)) {
    if (!multiple) selected <- firstChoice(choices)
  } else selected <- as.character(selected)

  if (!is.null(size) && selectize) {
    stop("'size' argument is incompatible with 'selectize=TRUE'.")
  }

  # create select tag and add options
  selectTag <- tags$select(
    id = inputId,
    class = if (!selectize) "form-control",
    size = size,
    selectOptions(choices, selected, inputId, selectize)
  )
  if (multiple)
    selectTag$attribs$multiple <- "multiple"

  # return label and select tag
  res <- div(
    class = "form-group shiny-input-container",
    style = css(width = validateCssUnit(width)),
    shinyInputLabel(inputId, label),
    div(selectTag)
  )

  if (!selectize) return(res)

  selectizeIt(inputId, res, NULL, nonempty = !multiple && !("" %in% choices))
}

firstChoice <- function(choices) {
  if (length(choices) == 0L) return()
  choice <- choices[[1]]
  if (is.list(choice)) firstChoice(choice) else choice
}

# Create tags for each of the options; use <optgroup> if necessary.
# This returns a HTML string instead of tags for performance reasons.
selectOptions <- function(choices, selected = NULL, inputId, perfWarning = FALSE) {
  if (length(choices) >= 1000) {
    warning("The select input \"", inputId, "\" contains a large number of ",
      "options; consider using server-side selectize for massively improved ",
      "performance. See the Details section of the ?selectizeInput help topic.",
      call. = FALSE)
  }

  html <- mapply(choices, names(choices), FUN = function(choice, label) {
    if (is.list(choice)) {
      # If sub-list, create an optgroup and recurse into the sublist
      sprintf(
        '<optgroup label="%s">\n%s\n</optgroup>',
        htmlEscape(label, TRUE),
        selectOptions(choice, selected, inputId, perfWarning)
      )

    } else {
      # If single item, just return option string
      sprintf(
        '<option value="%s"%s>%s</option>',
        htmlEscape(choice, TRUE),
        if (choice %in% selected) ' selected' else '',
        htmlEscape(label)
      )
    }
  })

  HTML(paste(html, collapse = '\n'))
}

# need <optgroup> when choices contains sub-lists
needOptgroup <- function(choices) {
  any(vapply(choices, is.list, logical(1)))
}

#' @rdname selectInput
#' @param ... Arguments passed to `selectInput()`.
#' @param options A list of options. See the documentation of \pkg{selectize.js}
#'   for possible options (character option values inside [base::I()] will
#'   be treated as literal JavaScript code; see [renderDataTable()]
#'   for details).
#' @param width The width of the input, e.g. `'400px'`, or `'100%'`;
#'   see [validateCssUnit()].
#' @note The selectize input created from `selectizeInput()` allows
#'   deletion of the selected option even in a single select input, which will
#'   return an empty string as its value. This is the default behavior of
#'   \pkg{selectize.js}. However, the selectize input created from
#'   `selectInput(..., selectize = TRUE)` will ignore the empty string
#'   value when it is a single choice input and the empty string is not in the
#'   `choices` argument. This is to keep compatibility with
#'   `selectInput(..., selectize = FALSE)`.
#' @export
selectizeInput <- function(inputId, ..., options = NULL, width = NULL) {
  selectizeIt(
    inputId,
    selectInput(inputId, ..., selectize = FALSE, width = width),
    options
  )
}

# given a select input and its id, selectize it
selectizeIt <- function(inputId, select, options, nonempty = FALSE) {
  if (length(options) == 0) {
    # For NULL and empty unnamed list, replace with an empty named list, so that
    # it will get translated to {} in JSON later on.
    options <- empty_named_list()
  }

  # Make sure accessibility plugin is included
  if (!('selectize-plugin-a11y' %in% options$plugins)) {
    options$plugins <- c(options$plugins, list('selectize-plugin-a11y'))
  }

  res <- checkAsIs(options)

  deps <- list(selectizeDependency())

  if ('drag_drop' %in% options$plugins) {
    deps <- c(
      deps,
      list(htmlDependency(
        'jqueryui', '1.12.1',
        c(href = 'shared/jqueryui'),
        script = 'jquery-ui.min.js'
      ))
    )
  }

  # Insert script on same level as <select> tag
  select$children[[2]] <- tagAppendChild(
    select$children[[2]],
    tags$script(
      type = 'application/json',
      `data-for` = inputId, `data-nonempty` = if (nonempty) '',
      `data-eval` = if (length(res$eval)) HTML(toJSON(res$eval)),
      HTML(toJSON(res$options))
    )
  )

  attachDependencies(select, deps)
}


selectizeDependency <- function() {
  bslib::bs_dependency_defer(selectizeDependencyFunc)
}

selectizeDependencyFunc <- function(theme) {
  if (!is_bs_theme(theme)) {
    return(selectizeStaticDependency(version_selectize))
  }

  selectizeDir <- system.file(package = "shiny", "www/shared/selectize/")
  bs_version <- bslib::theme_version(theme)
  stylesheet <- file.path(
    selectizeDir, "scss", paste0("selectize.bootstrap", bs_version, ".scss")
  )
  # It'd be cleaner to ship the JS in a separate, href-based,
  # HTML dependency (which we currently do for other themable widgets),
  # but DT, crosstalk, and maybe other pkgs include selectize JS/CSS
  # in HTML dependency named selectize, so if we were to change that
  # name, the JS/CSS would be loaded/included twice, which leads to
  # strange issues, especially since we now include a 3rd party
  # accessibility plugin https://github.com/rstudio/shiny/pull/3153
  script <- file.path(
    selectizeDir, c("js/selectize.min.js", "accessibility/js/selectize-plugin-a11y.min.js")
  )
  bslib::bs_dependency(
    input = sass::sass_file(stylesheet),
    theme = theme,
    name = "selectize",
    version = version_selectize,
    cache_key_extra = shinyPackageVersion(),
    .dep_args = list(script = script)
  )
}

selectizeStaticDependency <- function(version) {
  htmlDependency(
    "selectize", version,
    src = c(href = "shared/selectize"),
    stylesheet = "css/selectize.bootstrap3.css",
    script = c(
      "js/selectize.min.js",
      "accessibility/js/selectize-plugin-a11y.min.js"
    )
  )
}


#' Select variables from a data frame
#'
#' Create a select list that can be used to choose a single or multiple items
#' from the column names of a data frame.
#'
#' By default, `varSelectInput()` and `selectizeInput()` use the
#' JavaScript library \pkg{selectize.js}
#' (<https://github.com/selectize/selectize.js>) to instead of the basic
#' select input element. To use the standard HTML select input element, use
#' `selectInput()` with `selectize=FALSE`.
#'
#' @inheritParams selectInput
#' @param data A data frame. Used to retrieve the column names as choices for a [selectInput()]
#' @return A variable select list control that can be added to a UI definition.
#'
#' @family input elements
#' @seealso [updateSelectInput()]
#'
#' @section Server value:
#' The resulting server `input` value will be returned as:
#'
#'  * A symbol if `multiple = FALSE`. The `input` value should be
#'  used with rlang's [rlang::!!()]. For example,
#'  `ggplot2::aes(!!input$variable)`.
#'  * A list of symbols if `multiple = TRUE`. The `input` value
#'  should be used with rlang's [rlang::!!!()] to expand
#'  the symbol list as individual arguments. For example,
#'  `dplyr::select(mtcars, !!!input$variabls)` which is
#'  equivalent to `dplyr::select(mtcars, !!input$variabls[[1]], !!input$variabls[[2]], ..., !!input$variabls[[length(input$variabls)]])`.
#'
#' @examples
#'
#' ## Only run examples in interactive R sessions
#' if (interactive()) {
#'
#' library(ggplot2)
#'
#' # single selection
#' shinyApp(
#'   ui = fluidPage(
#'     varSelectInput("variable", "Variable:", mtcars),
#'     plotOutput("data")
#'   ),
#'   server = function(input, output) {
#'     output$data <- renderPlot({
#'       ggplot(mtcars, aes(!!input$variable)) + geom_histogram()
#'     })
#'   }
#' )
#'
#'
#' # multiple selections
#' \dontrun{
#' shinyApp(
#'  ui = fluidPage(
#'    varSelectInput("variables", "Variable:", mtcars, multiple = TRUE),
#'    tableOutput("data")
#'  ),
#'  server = function(input, output) {
#'    output$data <- renderTable({
#'       if (length(input$variables) == 0) return(mtcars)
#'       mtcars %>% dplyr::select(!!!input$variables)
#'    }, rownames = TRUE)
#'  }
#' )}
#'
#' }
#' @export
varSelectInput <- function(
  inputId, label, data, selected = NULL,
  multiple = FALSE, selectize = TRUE, width = NULL,
  size = NULL
) {
  # no place holders
  choices <- colnames(data)

  selectInputVal <- selectInput(
    inputId = inputId,
    label = label,
    choices = choices,
    selected = selected,
    multiple = multiple,
    selectize = selectize,
    width = width,
    size = size
  )

  # set the select tag class to be "symbol"
  selectClass <- selectInputVal$children[[2]]$children[[1]]$attribs$class
  if (is.null(selectClass)) {
    newClass <- "symbol"
  } else {
    newClass <- paste(selectClass, "symbol", sep = " ")
  }
  selectInputVal$children[[2]]$children[[1]]$attribs$class <- newClass

  selectInputVal
}



#' @rdname varSelectInput
#' @param ... Arguments passed to `varSelectInput()`.
#' @param options A list of options. See the documentation of \pkg{selectize.js}
#'   for possible options (character option values inside [base::I()] will
#'   be treated as literal JavaScript code; see [renderDataTable()]
#'   for details).
#' @param width The width of the input, e.g. `'400px'`, or `'100%'`;
#'   see [validateCssUnit()].
#' @note The variable selectize input created from `varSelectizeInput()` allows
#'   deletion of the selected option even in a single select input, which will
#'   return an empty string as its value. This is the default behavior of
#'   \pkg{selectize.js}. However, the selectize input created from
#'   `selectInput(..., selectize = TRUE)` will ignore the empty string
#'   value when it is a single choice input and the empty string is not in the
#'   `choices` argument. This is to keep compatibility with
#'   `selectInput(..., selectize = FALSE)`.
#' @export
varSelectizeInput <- function(inputId, ..., options = NULL, width = NULL) {
  selectizeIt(
    inputId,
    varSelectInput(inputId, ..., selectize = FALSE, width = width),
    options
  )
}

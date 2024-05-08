#!/usr/bin/env -S Rscript --vanilla

VERSION <- 5
VERSION_REQUIREJS <- "2.3.6"

# Load supporting files ------------------------------------------------------------
find_root <- function(dir = getwd()) {
  dir <- normalizePath(dir)
  if (file.exists(file.path(dir, "setup.cfg"))) {
    return(dir)
  }

  new_dir <- dirname(dir)
  if (new_dir == dir) {
    stop("Could not find shiny package root")
  }

  find_root(new_dir)
}

.root <- find_root()
path_root <- function(...) path(.root, ...)

source(file.path(.root, "scripts", "_functions_setup.R"))
source(file.path(.root, "scripts", "_functions_deps.R"))
package_ref <- source(file.path(.root, "scripts", "_pkg-sources.R"))$value

if (requireNamespace("cli", quietly = TRUE)) {
  message <- function(..., .envir = parent.frame()) {
    cli::cli_progress_step(paste0(...), .envir = .envir)
  }
}

assert_npm_is_installed()

versions <- list()

# Use local lib path for installing packages so we don't pollute the user's library
message("Installing GitHub packages: bslib, shiny, htmltools")
withr::local_temp_libpaths()
ignore <- capture.output({
  pak::pkg_install(c(
    package_ref$shiny,
    package_ref$bslib,
    package_ref$sass,
    package_ref$htmltools
  ))
  #pak::pkg_install(c("rstudio/bslib@main", "rstudio/shiny@main", "rstudio/htmltools@main"))
})

library(htmltools, quietly = TRUE, warn.conflicts = FALSE)
library(bslib, quietly = TRUE, warn.conflicts = FALSE)
library(fs, quietly = TRUE, warn.conflicts = FALSE)

WWW_SHARED <- path(.root, "shiny", "www", "shared")

# Set sass compilation options
local_sass_options <- withr::local_(function(x) rlang::exec(sass::sass_options_set, !!!x))
local_sass_options(list(
  output_style = "compressed",
  source_comments = FALSE,
  source_map_embed = FALSE
))

theme <- bs_theme(version = VERSION, preset = "shiny")

# ------------------------------------------------------------------------------
# Must come first!
message("Copy shiny www/shared")
# Copy over shiny's www/shared directory
copy_from_pkg("shiny", "www/shared", WWW_SHARED, WWW_SHARED)

# ------------------------------------------------------------------------------
message("Cleanup shiny www/shared")
# Don't need legacy (hopefully)
dir_delete(path(WWW_SHARED, "legacy"))
# Don't need dataTables (hopefully)
dir_delete(path(WWW_SHARED, "datatables"))
# Don't need sass files (hopefully)
dir_delete(path(WWW_SHARED, "shiny_scss"))

# jQuery will come in via bslib (below)
file_delete(
  dir_ls(WWW_SHARED, type = "file", regexp = "jquery")
)

# ------------------------------------------------------------------------------
message("Copy bslib components")
# Copy over bslib's components directory
www_bslib_components <- path(WWW_SHARED, "bslib", "components")
copy_from_pkg("bslib", "components/dist", www_bslib_components)
delete_non_minified(www_bslib_components)


# ------------------------------------------------------------------------------
message("Copy htmltools - fill")
# Copy over htmltools's fill directory
copy_from_pkg("htmltools", "fill", path(WWW_SHARED, "htmltools", "fill"))


# ------------------------------------------------------------------------------
message("Save ionRangeSlider dep")

# Upgrade to Bootstrap 5 by default
write_deps_ionrangeslider(theme, WWW_SHARED)


message("Save bootstrap bundle")
write_bootstrap_bslib_deps(theme, WWW_SHARED)


# ------------------------------------------------------------------------------
message("Render shiny.min.css with bs_theme()")
write_shiny_css(theme, WWW_SHARED)

message("Render selectize.min.js with bs_theme()")
write_selectize_css(theme, WWW_SHARED)

message("Render datepicker.min.css with bs_theme()")
write_datepicker_css(theme, WWW_SHARED)

# ------------------------------------------------------------------------------
message("Cleanup bootstrap bundle")
# This additional bs3compat HTMLDependency() only holds
# the JS shim for tab panel logic, which we don't need
# since we're generating BS5+ tab markup. Note, however,
# we still do have bs3compat's bundled CSS on the page, which
# comes in naturally via the bootstrap HTMLDependency()
delete_from_www_shared(
  WWW_SHARED,
  "bs3compat",
  # Remove non-minified or unused files
  "datepicker/css/bootstrap-datepicker3.css",
  "datepicker/js/bootstrap-datepicker.js",
  "datepicker/scss",
  "ionrangeslider/js/ion.rangeSlider.js",
  "ionrangeslider/scss",
  "jquery/jquery-3.6.0.js",
  "jqueryui/jquery-ui.css",
  "jqueryui/jquery-ui.js",
  "jqueryui/jquery-ui.structure.css",
  "jqueryui/jquery-ui.structure.min.css",
  "jqueryui/jquery-ui.theme.css",
  "jqueryui/jquery-ui.theme.min.css",
  "selectize/accessibility/js/selectize-plugin-a11y.js", # TODO: keep this one?
  "selectize/js/selectize.js"
)

# ------------------------------------------------------------------------------
message("Save requirejs")
write_require_js(VERSION_REQUIREJS, WWW_SHARED)

# ------------------------------------------------------------------------------
message("Save _versions.py")
write_versions_py(bootstrap = VERSION, requirejs = VERSION_REQUIREJS)


# ------------------------------------------------------------------------------
message("Copy ./js deps via npm")
npm_install_dependencies()

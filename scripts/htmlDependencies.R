#!/usr/bin/env -S Rscript --vanilla

VERSION_BOOTSTRAP <- 5
VERSION_REQUIREJS <- "2.3.6"
BUNDLED_PRESETS <- c("bootstrap", "shiny")

# Load supporting files ------------------------------------------------------------
find_root <- function(dir = getwd()) {
  dir <- normalizePath(dir)
  if (file.exists(file.path(dir, "setup.cfg"))) {
    return(dir)
  }
  if (file.exists(file.path(dir, "pyproject.toml"))) {
    return(dir)
  }

  new_dir <- dirname(dir)
  if (new_dir == dir) {
    stop("Could not find shiny package root")
  }

  find_root(new_dir)
}

.root <- find_root()

source(file.path(.root, "scripts", "_functions_setup.R"))
source(file.path(.root, "scripts", "_functions_deps.R"))
source(file.path(.root, "scripts", "_functions_sass.R"))
package_ref <- source(file.path(.root, "scripts", "_pkg-sources.R"))$value


# Setup clean package environment ---------------------------------------------------
if (!requireNamespace("withr", quietly = TRUE)) {
  message("Installing withr")
  install.packages("withr", quiet = TRUE)
}
library(withr)

local_temp_libpaths("replace")

message("Installing required packages...")
pak_install(
  "fs",
  package_ref$shiny,
  package_ref$bslib,
  package_ref$sass,
  package_ref$htmltools
)

local_options(bslib.precompiled = FALSE, sass.cache = FALSE)

# Setting up ---------------------------------------------------------------------
cli::cli_h2("Setting up")

assert_npm_is_installed()

library(bslib, warn.conflicts = FALSE)
library(htmltools)
library(sass)
library(fs)

PRESETS <- c(
  "bootstrap",
  "shiny",
  bootswatch_themes(VERSION_BOOTSTRAP)
)

path_root <- function(...) {
  path(.root, ...)
}

WWW_SHARED <- path(.root, "shiny", "www", "shared")
DIR_SASS <- path_root("shiny", "www", "shared", "sass")

if (dir_exists(WWW_SHARED)) {
  cli::cli_alert_warning("Reset {.path {path_rel(WWW_SHARED)}}")
  dir_delete(WWW_SHARED)
}

dir_create(WWW_SHARED)

# Copy dependencies from {shiny} and {bslib} -----------------------------------------
cli::cli_h2("Copy web dependencies from {.pkg shiny} and {.pkg bslib}")

copy_from_pkg("shiny", "www/shared", WWW_SHARED, WWW_SHARED)
www_bslib_components <- path(WWW_SHARED, "bslib", "components")
copy_from_pkg("bslib", "components/dist", www_bslib_components)
copy_from_pkg("htmltools", "fill", path(WWW_SHARED, "htmltools", "fill"))


# Pre-rendering Component CSS --------------------------------------------------------
cli::cli_h2("Pre-render Component CSS")

theme_bs <- bs_theme(version = VERSION_BOOTSTRAP, preset = "bootstrap")
theme_shiny <- bs_theme(version = VERSION_BOOTSTRAP, preset = "shiny")

write_bootstrap_bslib_deps(theme_shiny, WWW_SHARED)
write_deps_ionrangeslider(theme_bs, WWW_SHARED)
write_shiny_css(theme_bs, WWW_SHARED)
write_selectize_css(theme_bs, WWW_SHARED)
write_datepicker_css(theme_bs, WWW_SHARED)

# Finishing installing Dependencies ---------------------------------------------------
cli::cli_h2("Finish installing web dependencies")

write_require_js(VERSION_REQUIREJS, WWW_SHARED)
npm_install_dependencies()

cli::cli_progress_step("Remove unused files from copied dependencies")
delete_non_minified(www_bslib_components)
delete_from_www_shared(
  WWW_SHARED,
  "bs3compat",
  "legacy",
  "datatables",
  "shiny_scss",
  # jQuery comes from bslib
  path_rel(dir_ls(WWW_SHARED, type = "file", regexp = "jquery"), WWW_SHARED),
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
cli::cli_progress_done()


# Prepare Preset Sass Files ----------------------------------------------------------
cli::cli_h2("Prepare {length(PRESETS)} Bootstrap theme preset{?s}")

dir_create(DIR_SASS)
path_sass_markers <- write_sass_layer_markers(DIR_SASS)

dep_files <- c()
for (preset in PRESETS) {
  preset_files <-
    prepare_and_write_theme_sass_files(
      VERSION_BOOTSTRAP,
      preset,
      path_sass_markers,
      output_dir = DIR_SASS
    )

  dep_files <- unique(c(dep_files, preset_files$deps))
}

# Fixup Sass Files -------------------------------------------------------------------
cli::cli_h2("Fix up intermediate Sass Files")
fixup_bootswatch_mixins(dep_files)


# Precompile CSS Files ---------------------------------------------------------------
cli::cli_h2("Precompile CSS files")
for (preset in PRESETS) {
  compile_theme_sass(preset, BUNDLED_PRESETS, DIR_SASS)
}

copy_shiny_preset_to_base_bootstrap()

# Generate Python Files -------------------------------------------------------------
cli::cli_h2("Generate Python files")

write_python_preset_choices(VERSION_BOOTSTRAP, PRESETS, BUNDLED_PRESETS)
write_versions_py(bootstrap = VERSION_BOOTSTRAP, requirejs = VERSION_REQUIREJS)
write_spinners_py(WWW_SHARED)

#!/usr/bin/env -S Rscript --vanilla

VERSION <- 5
BUNDLED_PRESETS <- c("bootstrap", "shiny")

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

source(file.path(.root, "scripts", "_functions_sass.R"))
source(file.path(.root, "scripts", "_functions_setup.R"))

# Setup clean package environment ---------------------------------------------------
library(withr)

withr::local_temp_libpaths("replace")

message("Installing required packages...")
package_ref <- source(file.path(.root, "scripts", "_pkg-sources.R"))$value
pak_install(
  "fs",
  package_ref$shiny,
  package_ref$bslib,
  package_ref$sass
)

withr::local_options(bslib.precompiled = FALSE, sass.cache = FALSE)

# Setting up ---------------------------------------------------------------------
cli::cli_h2("Setting up")

library(bslib, warn.conflicts = FALSE)
library(sass)
library(fs)

PRESETS <- c(
  "bootstrap",
  "shiny",
  bootswatch_themes(VERSION)
)

path_root <- function(...) {
  path(.root, ...)
}

# bslib's assets will ultimately go into a packaged directory
DIR_SASS <- path_root("shiny", "www", "shared", "sass")

if (dir_exists(DIR_SASS)) {
  cli::cli_alert_warning("Reset {.path {path_rel(DIR_SASS)}}")
  dir_delete(DIR_SASS)
}

dir_create(DIR_SASS)

path_sass_markers <- write_sass_layer_markers(DIR_SASS)

# Prepare Preset Sass Files ----------------------------------------------------------
cli::cli_h2("Preparing {length(PRESETS)} Bootstrap theme preset{?s}")

dep_files <- c()
for (preset in PRESETS) {
  preset_files <-
    prepare_and_write_theme_sass_files(
      VERSION,
      preset,
      path_sass_markers,
      output_dir = DIR_SASS
    )

  dep_files <- unique(c(dep_files, preset_files$deps))
}

# Fixup Sass Files -------------------------------------------------------------------
cli::cli_h2("Fixing up intermediate Sass Files")
fixup_bootswatch_mixins(dep_files)


# Precompile CSS Files ---------------------------------------------------------------
cli::cli_h2("Precompiling CSS files")
for (preset in PRESETS) {
  compile_theme_sass(preset, BUNDLED_PRESETS, DIR_SASS)
}

# Generate Python Files -------------------------------------------------------------
cli::cli_h2("Generate Python files")

write_python_preset_choices(PRESETS, BUNDLED_PRESETS)
copy_shiny_preset_to_base_bootstrap()

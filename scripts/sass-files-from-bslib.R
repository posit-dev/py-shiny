#!/usr/bin/env -S Rscript --vanilla

# Setup clean package environment -----------------------------------------------------
package_ref <- if (file.exists("scripts/_pkg-sources.R")) {
  source("scripts/_pkg-sources.R")$value
} else if (file.exists("_pkg-sources.R")) {
  source("_pkg-sources.R")$value
} else {
  stop("Could not find _pkg-sources.R")
}

library(withr)

withr::local_temp_libpaths("replace")

ensure_base_packages <- function() {
  for (pkg in c("cli", "pak")) {
    if (!requireNamespace(pkg, quietly = TRUE)) {
      message("Installing base packge: ", pkg)
      install.packages(pkg, quiet = TRUE)
    }
  }
}

pak_install <- function(...) {
  ensure_base_packages()
  pkgs <- c(...)

  cli::cli_progress_step("Installing {length(pkgs)} package{?s}")

  pak::pak(pkgs, upgrade = TRUE, ask = FALSE, lib = .libPaths()[1])

  cli::cli_progress_done()

  cli::cli_h2("Packages")
  for (pkg in pkgs) {
    pkg_name <- pkg
    if (grepl("@", pkg)) {
      pkg_name <- basename(sub("@.+$", "", pkg))
    } else if (grepl("/", pkg)) {
      pkg_name <- basename(pkg)
    }
    v_pkg <- tryCatch(packageVersion(pkg_name), error = function(e) "???")

    cli::cli_inform("Installed {.strong {pkg_name}} v{v_pkg}")
  }

  invisible(pkgs)
}

message("Installing required packages...")
pak_install(
  "fs", "here",
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

version <- 5

# bslib's assets will ultimately go into a packaged directory
DIR_RESOURCES <- here::here("shiny", "www", "shared", "sass")
cli::cli_alert_warning("Reset {.path {path_rel(DIR_RESOURCES)}}")

if (dir_exists(DIR_RESOURCES)) dir_delete(DIR_RESOURCES)
dir_create(DIR_RESOURCES)

sass_markers <- "/*-- scss:functions --*/
// SPLIT: functions

/*-- scss:defaults --*/
// SPLIT: defaults

/*-- scss:rules --*/
// SPLIT: rules

/*-- scss:mixins --*/
// SPLIT: mixins
"

path_sass_markers <- path(DIR_RESOURCES, "_sass_layer_markers.scss")
writeLines(sass_markers, path_sass_markers)

# Functions ---------------------------------------------------------------------

bslib_bs_theme <- function(version, preset = "shiny") {
  theme <- bs_theme(version, preset = preset)
  bs_remove(theme, "bs3compat")
}

bs_full_theme <- function(theme) {
  bs_version <- bslib::theme_version(theme)

  bs_bundle(
    theme,
    bslib = bslib_component_sass(),
    shiny = shiny_sass(bs_version),
    selectize = shiny_sass_selectize(bs_version),
    ionrangeslider = shiny_sass_ionrangeslider(),
    daterange = shiny_sass_daterange_picker(),
    marker = sass_layer_file(path_sass_markers),
  )
}

bslib_component_sass <- function() {
  sass_layer(rules = bslib:::component_dependency_sass_layer())
}

shiny_sass <- function(bs_version) {
  shiny:::shinyDependencySass(bs_version)
}

shiny_sass_selectize <- function(bs_version) {
  sass_layer(rules = shiny:::selectizeSass(bs_version))
}

shiny_sass_ionrangeslider <- function() {
  sass_layer(rules = shiny:::ionRangeSliderDependencySass())
}

shiny_sass_daterange_picker <- function() {
  sass_layer(rules = shiny:::datePickerSass())
}

theme_as_sass_lines <- function(full_theme) {
  bs_sass <- as_sass(full_theme)
  strsplit(as.character(bs_sass), "\n")[[1]]
}

theme_relative_paths <- function(theme_sass_lines) {
  replace_package_path <- function(pkg) {
    replacement <- "@import \"../../"

    pkg_dir <- path_package(pkg)
    if (path_file(pkg_dir) == "inst") {
      # e.g /Users/garrick/work/rstudio/bslib/inst
      replacement <- paste0('@import "../../', pkg, "/")
    } else {
      # e.g. /path/to/libPath/sass
      pkg_dir <- path_dir(pkg_dir)
    }

    gsub(
      paste0("@import \"", pkg_dir, "/"),
      replacement,
      theme_sass_lines,
      fixed = TRUE
    )
  }

  for (pkg in c("bslib", "shiny")) {
    theme_sass_lines <- replace_package_path(pkg)
  }

  theme_sass_lines
}

find_sass_file <- function(file) {
  if (file_exists(file)) return(file)

  file_scss <- path(file, ext = "scss")
  file_sass <- path(file, ext = "sass")

  if (file_exists(file_scss)) {
    return(path(file_scss))
  } else if (file_exists(file_sass)) {
    return(path(file_sass))
  } else if (!grepl("^_", path_file(file))) {
    file_under <- path(path_dir(file), paste0("_", path_file(file)))
    return(find_sass_file(file_under))
  }

  NULL
}

theme_files_used <- function(theme_sass_lines) {
  imports <- grep("^\\s*@import \"", theme_sass_lines, value = TRUE)
  if (!length(imports)) return()

  imports <- trimws(imports)
  imports <- gsub("^@import \"([^\"]+?)\";", 'identity("\\1")', imports)

  files <- vapply(imports, \(x) eval(parse(text = x)), character(1))
  files_ret <- files <- unique(files)

  for (file in files) {
    if (!file_exists(file)) {
      found <- find_sass_file(file)
      if (is.null(found)) {
        stop("Could not find file: ", file)
      }
      files_ret[files == file] <- path_abs(found)
      file <- found
    } else if (file != path_abs(file)) {
      files_ret[files == file] <- path_abs(file)
    }

    lines <- readLines(file, warn = FALSE)

    used_in_file <- withr::with_dir(path_dir(file), {
      theme_files_used(lines)
    })
    files_ret <- c(files_ret, used_in_file)
  }

  files_ret
}

theme_sass_split <- function(theme_sass_lines) {
  # Splits the sass files into four layers:
  # 1. functions
  # 2. defaults
  # 3. rules
  # 4. mixins

  # These strings come from `path_sass_markers`
  splits <- grep("// SPLIT", theme_sass_lines)
  split_names <- gsub("// SPLIT: ", "", theme_sass_lines[splits])

  theme_split <- list()
  for (i in seq_along(splits)) {
    start <- if (i == 1) 1 else splits[i - 1] + 1
    end <- splits[i] - 1
    name <- split_names[i]
    theme_split[[name]] <- theme_sass_lines[start:end]
  }

  theme_split
}

fixup_bootswatch_mixins <- function(file) {
  # Some Bootswatch files include mixins that conflict with Bootstrap's own
  # mixins. We need to rename these mixins to avoid the conflict. This does't
  # happen in {bslib} because the conflicts appear in Sass that's compiled
  # with `sass_partial()`, which replaces the "rules" portion of the Sass
  # file with the incoming rules. Since the mixins are defined in the "rules"
  # area, they're dropped, e.g. when compiling the selectize Sass.

  lines <- readLines(file)
  mixins <- grep("^@mixin", lines, value = TRUE)
  if (!length(mixins)) return()

  mixins <- gsub("^@mixin ([^\\(]+)\\(.+", "\\1", mixins)

  for (mixin in mixins) {
    # Rename declarations `@mixin <name>-bootswatch`
    lines <- sub(
      sprintf("@mixin %s(", mixin),
      sprintf("@mixin %s-bootswatch(", mixin),
      lines,
      fixed = TRUE
    )
    # Rename calls, e.g. `@include <name>-bootswatch(`
    lines <- gsub(
      sprintf("@include %s(", mixin),
      sprintf("@include %s-bootswatch(", mixin),
      lines,
      fixed = TRUE
    )
  }

  writeLines(lines, file)
}

copy_theme_dependency_files <- function(theme_sass_lines, to = DIR_RESOURCES) {
  theme_files <- theme_files_used(theme_sass_lines)

  path_lib <- path_package("bslib")
  if (path_file(path_lib) != "inst") {
    path_lib <- path_dir(path_lib)
  }

  theme_files_new <- path_rel(theme_files, start = path_lib)
  theme_files_new <- path(to, theme_files_new)

  for (dir in unique(path_dir(theme_files_new))) {
    if (!dir_exists(dir)) dir_create(dir)
  }

  file_copy(theme_files, theme_files_new, overwrite = TRUE)
}

write_theme_sass_files <- function(preset, theme_sass_lines) {
  # Take out bslib's web-font-path override
  theme_sass_lines <- setdiff(theme_sass_lines, '$web-font-path: "font.css" !default;')

  theme_rel_lines <- theme_relative_paths(theme_sass_lines)
  theme_split <- theme_sass_split(theme_rel_lines)

  pkg_dir_preset <- path(DIR_RESOURCES, "preset", preset)
  if (dir_exists(pkg_dir_preset)) dir_delete(pkg_dir_preset)
  dir_create(pkg_dir_preset)

  file_names <- c()

  for (i in seq_along(theme_split)) {
    theme_name <- names(theme_split)[i]
    file_name <- sprintf("_%02d_%s.scss", i, theme_name)
    file_names <- c(file_names, file_name)

    writeLines(
      theme_split[[theme_name]],
      path(pkg_dir_preset, file_name)
    )
  }

  main_lines <- sprintf("@import \"%s\";", file_names)

  writeLines(main_lines, path(pkg_dir_preset, "preset.scss"))

  path(pkg_dir_preset, "preset.scss")
}

# Prepare Preset Sass Files ----------------------------------------------------------
presets <- c(
  "bootstrap",
  "shiny",
  bootswatch_themes(version)
)
bundled_presets <- c("bootstrap", "shiny")

dep_files <- c()
preset_sass_entry_files <- list()

cli::cli_h2("Preparing {length(presets)} Bootstrap theme preset{?s}")

for (preset in presets) {

  cli::cli_progress_step(
    "Preparing {.strong {preset}} theme Sass files...",
    "Prepared {.strong {preset}} theme in {.path {path_rel(path(DIR_RESOURCES, 'preset', preset))}}",
    "Failed to prepare {.strong {preset}} theme Sass files."
  )

  theme <- bslib_bs_theme(version, preset)
  theme_full <- bs_full_theme(theme)
  theme_sass_lines <- theme_as_sass_lines(theme_full)

  dep_files <<- unique(c(
    dep_files,
    copy_theme_dependency_files(theme_sass_lines, to = DIR_RESOURCES)
  ))

  preset_sass_entry_files[preset] <- write_theme_sass_files(preset, theme_sass_lines)
  cli::cli_progress_done()
}

# Fixup Sass Files -------------------------------------------------------------------
cli::cli_h2("Fixing up intermediate Sass Files")

cli::cli_progress_step("Fixing up Bootswatch mixin names")
bsw_files <- dep_files[path_file(dep_files) == "_bootswatch.scss"]
for (bsw_file in bsw_files) {
  fixup_bootswatch_mixins(bsw_file)
}

cli::cli_progress_done()

# Precompile CSS Files ---------------------------------------------------------------
cli::cli_h2("Precompiling CSS files")
for (preset in presets) {
  path_preset_scss <- preset_sass_entry_files[[preset]]
  verb <- if (preset %in% bundled_presets) "Pre-compil" else "Test"

  cli::cli_progress_step(
    "{verb}ing {.strong {preset}} theme CSS...",
    "{verb}ed {.strong {preset}} theme CSS {.path {path_rel(path_dir(path_preset_scss))}}",
    "Failed to precompile {.strong {preset}} theme CSS."
  )

  path_preset_compiled <- path(path_dir(path_preset_scss), "preset.min.css")

  # Pre-render the Sass files into compiled CSS
  tryCatch({
    sass(
      sass_file(path_preset_scss),
      output = path_preset_compiled,
      options = sass_options(
        output_style = "compressed",
        source_comments = FALSE,
        source_map_embed = FALSE
      )
    )
    cli::cli_progress_done()
  }, error = function(cnd) {
    cli::cli_progress_done(result = "error")
    cli::cli_inform("Failed to compile Sass file {.path {path_preset_scss}}.", parent = cnd)
  })

  # Remove intermediate entry-point Sass file
  file_delete(path_preset_scss)

  # Don't bundle precompiled Bootswatch files
  if (!preset %in% bundled_presets) {
    file_delete(path_preset_compiled)
  }
}

# Generate Python Files -------------------------------------------------------------
cli::cli_h2("Generate Python files")

path_presets_py <- path(here::here("shiny", "ui"), "_theme_presets.py")
cli::cli_progress_step("Generating {.path {path_rel(path_presets_py)}}")

template <- r"(# Generated by scripts/sass-files-from-bslib.R: do not edit by hand

from __future__ import annotations

from typing import Literal

ShinyThemePreset = Literal[
%s
]

ShinyThemePresets: tuple[ShinyThemePreset, ...] = (
%s
)

ShinyThemePresetsBundled: tuple[ShinyThemePreset, ...] = (
%s
))"

py_list <- function(x) {
  x <- paste(sprintf('"%s"', x), collapse = ",\n\t")
  paste0("\t", x, ",")
}

writeLines(
  sprintf(template, py_list(presets), py_list(presets), py_list(bundled_presets)),
  path_presets_py
)


path_preset_shiny <- here::here("shiny", "www", "shared", "sass", "preset", "shiny", "preset.min.css")
path_bootstrap <- here::here("shiny", "www", "shared", "bootstrap", "bootstrap.min.css")
cli::cli_progress_step("Copying shiny preset {.path {path_rel(path_bootstrap)}}")

preset_shiny_lines <- readLines(path_preset_shiny)
preset_shiny_lines[1] <- sub(
  "^@import url\\([^)]+\\)",
  "@import url(\"font.css\")",
  preset_shiny_lines[1]
)
writeLines(preset_shiny_lines, path_bootstrap)

cli::cli_process_done()

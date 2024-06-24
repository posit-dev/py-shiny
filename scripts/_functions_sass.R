#' Write a Sass layer file used to split the final theme into four layers
#' using the same logic as `sass::sass_layer_file()` and Quarto.
#' @param dir The directory where the `_sass_layer_markers.css` file will be written.
#' @return The path to the newly created Sass layer file.
write_sass_layer_markers <- function(dir) {
  sass_markers <- "/*-- scss:functions --*/
// SPLIT: functions

/*-- scss:defaults --*/
// SPLIT: defaults

/*-- scss:rules --*/
// SPLIT: rules

/*-- scss:mixins --*/
// SPLIT: mixins
"

  path_sass_markers <- path(dir, "_sass_layer_markers.scss")
  writeLines(sass_markers, path_sass_markers)

  path_sass_markers
}

#' Create a base Bootstrap theme via {bslib}.
bslib_bs_theme <- function(version, preset = "shiny") {
  bs_theme(version, preset = preset)
}

#' Create a full Shiny theme bundle with all dependencies.
#'
#' Adds styles for bslib components, shiny styles, `input_selectize()`, `input_slider()`
#' and `input_date_range()`.
#' @return A `bslib::bs_bundle()` object.
bs_full_theme <- function(theme, path_sass_markers) {
  bs_version <- bslib::theme_version(theme)

  bs_bundle(
    theme,
    bslib = bslib_component_sass(),
    shiny = shiny_sass(bs_version),
    selectize = shiny_sass_selectize(bs_version),
    ionrangeslider = shiny_sass_ionrangeslider(),
    daterange = shiny_sass_daterange_picker(),
    # The next layer must come last so that its text appears where a user layer would
    marker = sass_layer_file(path_sass_markers),
  )
}

bslib_component_sass <- function() {
  bslib:::component_dependency_sass_files()
}

shiny_sass <- function(bs_version) {
  shiny:::shinyDependencySass(bs_version)
}

shiny_sass_selectize <- function(bs_version) {
  shiny:::selectizeSass(bs_version)
}

shiny_sass_ionrangeslider <- function() {
  # iorangeslider sass files include a variable declaration that uses
  # `$component-active-bg` and needs to be forced into the rules layer
  sass::sass_layer(rules = shiny:::ionRangeSliderDependencySass())
}

shiny_sass_daterange_picker <- function() {
  shiny:::datePickerSass()
}

#' Flattens the Sass bundle into a single Sass file, ignoring file attachments
#' @return A character vector of lines of flattened Sass code
theme_as_sass_lines <- function(full_theme) {
  bs_sass <- as_sass(full_theme)
  strsplit(as.character(bs_sass), "\n")[[1]]
}

#' Replaces package-relative paths in the theme Sass with paths relative to the
#' `shiny/www/shared/sass/preset/{preset_name}` directory, where the preset Sass will
#' be stored.
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

#' Finds the Sass file for a given import statement, which may exclude a leading
#' underscore and/or the file extension.
#' @return The path to the Sass file, or `NULL` if the file could not be found.
find_sass_file <- function(file) {
  if (file_exists(file)) {
    return(file)
  }

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

#' Searches the Sass lines recursively for `@import` statements and returns the paths to
#' all imported files, including `@import` statements in imported files.
#' @return A character vector of absolute paths to all imported Sass files.
theme_files_used <- function(theme_sass_lines) {
  imports <- grep("^\\s*@import [\"']", theme_sass_lines, value = TRUE)
  if (!length(imports)) {
    return()
  }

  imports <- trimws(imports)
  imports <- gsub("^@import \"([^\"]+?)\";", "\\1", imports)
  imports <- gsub("^@import '([^']+?)';", "\\1", imports)

  if (any(grepl("^@import", imports))) {
    uncaught <- imports[grepl("^@import", imports)]
    cli::cli_abort(
      c(
        "Unexpected import statement(s): {.val {uncaught}}",
        i = "Please update {.fn theme_files_used} in {.path {path_root('scripts/_functions_sass.R')}}."
      )
    )
  }

  files_ret <- files <- unique(imports)

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

#' Splits the theme Sass into four layers: functions, defaults, rules, and mixins. Uses
#' the same logic as `sass::sass_layer_file()` and Quarto.
#' @return A named list of character vectors, each containing the lines of a Sass layer.
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

fixup_bootswatch_mixins_file <- function(file) {
  # Some Bootswatch files include mixins that conflict with Bootstrap's own
  # mixins. We need to rename these mixins to avoid the conflict. This does't
  # happen in {bslib} because the conflicts appear in Sass that's compiled
  # with `sass_partial()`, which replaces the "rules" portion of the Sass
  # file with the incoming rules. Since the mixins are defined in the "rules"
  # area, they're dropped, e.g. when compiling the selectize Sass.

  lines <- readLines(file)
  mixins <- grep("^@mixin", lines, value = TRUE)
  if (!length(mixins)) {
    return()
  }

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

#' Fixes up Bootswatch mixin names to avoid conflicts with Bootstrap's own mixins.
#' @param dep_files A character vector of paths to all Sass files to scan (looking for
#'   `_bootswatch.scss` files).
#' @return A character vector of paths to all `_bootswatch.scss` files.
fixup_bootswatch_mixins <- function(dep_files) {
  cli::cli_progress_step("Fix up Bootswatch mixin names")

  bsw_files <- dep_files[path_file(dep_files) == "_bootswatch.scss"]

  for (bsw_file in bsw_files) {
    fixup_bootswatch_mixins_file(bsw_file)
  }

  invisible(bsw_files)
}

#' Copies the theme Sass files to the `shiny/www/shared/sass` directory.
#' @param theme_sass_lines The lines of the theme Sass file.
#' @param to The directory to copy the files to.
#' @return A character vector of paths to the copied files.
copy_theme_sass_files <- function(theme_sass_lines, to = DIR_SASS) {
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

#' Writes the theme Sass files to the `shiny/www/shared/sass/preset/{preset}` directory.
#' @param preset The name of the preset.
#' @param theme_sass_lines The lines of the theme's flattened Sass.
#' @return The path to the entry-point Sass file for the preset.
write_theme_sass_files <- function(preset, theme_sass_lines, output_dir) {
  # Take out bslib's web-font-path override
  theme_sass_lines <- setdiff(theme_sass_lines, '$web-font-path: "font.css" !default;')

  theme_rel_lines <- theme_relative_paths(theme_sass_lines)
  theme_split <- theme_sass_split(theme_rel_lines)

  pkg_dir_preset <- path(output_dir, "preset", preset)
  if (dir_exists(pkg_dir_preset)) dir_delete(pkg_dir_preset)
  dir_create(pkg_dir_preset)

  # _01_functions.scss, _02_defaults.scss, etc.
  file_names <- sprintf("_%02d_%s.scss", seq_along(theme_split), names(theme_split))

  for (i in seq_along(theme_split)) {
    writeLines(
      theme_split[[i]],
      path(pkg_dir_preset, file_names[i])
    )
  }

  main_lines <- sprintf("@import \"%s\";", file_names)

  writeLines(main_lines, path(pkg_dir_preset, "preset.scss"))

  path(pkg_dir_preset, "preset.scss")
}

#' Creates a full Bootstrap theme with all dependencies and writes the theme Sass files.
#' @return A list with the dependencies (`$deps`) and the path to the entry-point Sass
#' file (`$preset`).
prepare_and_write_theme_sass_files <- function(version, presets, path_sass_markers, output_dir) {
  cli::cli_progress_step(
    "Prepare {.strong {preset}} theme Sass files...",
    "Prepared {.strong {preset}} theme in {.path {path_rel(path(output_dir, 'preset', preset))}}",
    "Failed to prepare {.strong {preset}} theme Sass files."
  )

  theme <- bslib_bs_theme(version, preset)
  theme_full <- bs_full_theme(theme, path_sass_markers)
  theme_sass_lines <- theme_as_sass_lines(theme_full)

  dep_files <- copy_theme_sass_files(theme_sass_lines, to = output_dir)

  preset_path <- write_theme_sass_files(
    preset,
    theme_sass_lines,
    output_dir = DIR_SASS
  )

  list(
    deps = dep_files,
    preset = preset_path
  )
}

#' Compiles the on-disk theme preset Sass files into CSS.
#' @param preset The name of the preset.
#' @param presets_precompiled A character vector of preset names that py-shiny will
#'   precompile and include in the package.
#' @param output_dir The directory where the compiled CSS will be written.
#' @return The path to the compiled CSS file if the preset is precompiled, otherwise
#'   `NULL`.
compile_theme_sass <- function(preset, presets_precompiled, output_dir) {
  path_preset_scss <- path(output_dir, "preset", preset, "preset.scss")
  path_preset_compiled <- path(path_dir(path_preset_scss), "bootstrap.min.css")

  verb <- if (preset %in% presets_precompiled) "Pre-compil" else "Test"
  path_out <- ""

  cli::cli_progress_step(
    "{verb}ing {.strong {preset}} theme CSS...",
    "{verb}ed {.strong {preset}} theme CSS {.path {path_out}}",
    "Failed to precompile {.strong {preset}} theme CSS."
  )

  # Pre-render the Sass files into compiled CSS
  tryCatch(
    {
      sass(
        sass_file(path_preset_scss),
        output = path_preset_compiled,
        options = sass_options(
          output_style = "compressed",
          source_comments = FALSE,
          source_map_embed = FALSE
        )
      )
      if (preset %in% presets_precompiled) {
        path_out <- path_rel(path_preset_compiled)
      }
      cli::cli_progress_done()
    },
    error = function(cnd) {
      cli::cli_progress_done(result = "error")
      cli::cli_inform("Failed to compile Sass file {.path {path_preset_scss}}.", parent = cnd)
    }
  )

  # Remove intermediate entry-point Sass file
  file_delete(path_preset_scss)

  # Don't bundle precompiled Bootswatch files
  if (!preset %in% presets_precompiled) {
    file_delete(path_preset_compiled)
    return(invisible())
  }

  invisible(path_preset_compiled)
}

#' Write the Python preset choices to `_theme_presets.py`.
#' @param presets A character vector of preset names.
#' @param presets_precompiled A character vector of preset names that were precompiled.
write_python_preset_choices <- function(version, presets, presets_precompiled) {
  path_presets_py <- path_root("shiny", "ui", "_theme_presets.py")
  cli::cli_progress_step("Generate {.path {path_rel(path_presets_py)}}")

  template <- r"(# Generated by scripts/htmlDependencies.R: do not edit by hand

from __future__ import annotations

from typing import Literal

ShinyThemePreset = Literal[
%s
]

shiny_theme_presets: tuple[ShinyThemePreset, ...] = (
%s
)

shiny_theme_presets_bundled: tuple[ShinyThemePreset, ...] = (
%s
)

shiny_theme_presets_bootswatch: tuple[ShinyThemePreset, ...] = (
%s
))"

  py_lines <- function(x) {
    x <- paste(sprintf('"%s"', x), collapse = ",\n    ")
    paste0("    ", x, ",")
  }

  writeLines(
    sprintf(
      template,
      py_lines(presets),
      py_lines(presets),
      py_lines(presets_precompiled),
      py_lines(bslib::bootswatch_themes(version))
    ),
    path_presets_py
  )

  invisible(path_presets_py)
}

#' Copy the compiled CSS from the Shiny preset to the base Bootstrap CSS file. It also
#' replaces the `@import` statement in the Bootstrap CSS file with the correct path to
#' the font CSS file to re-enable pre-downloaded fonts.
copy_shiny_preset_to_base_bootstrap <- function() {
  path_preset_shiny <- path_root("shiny", "www", "shared", "sass", "preset", "shiny", "bootstrap.min.css")
  path_bootstrap <- path_root("shiny", "www", "shared", "bootstrap", "bootstrap.min.css")
  cli::cli_progress_step("Copy shiny preset to {.path {path_rel(path_bootstrap)}}")

  preset_shiny_lines <- readLines(path_preset_shiny)

  if (!grepl("font|family", preset_shiny_lines[1])) {
    cli::cli_abort(
      c(
        "Expected a font import in {.path {path_preset_shiny}}:1",
        x = "{.val {preset_shiny_lines[1]}}",
        i = "Please update {.fn copy_shiny_preset_to_base_bootstrap} in {.path {path_root('scripts/_functions_sass.R')}}."
      )
    )
  }

  preset_shiny_lines[1] <- sub(
    "^@import url\\([^)]+\\)",
    "@import url(\"font.css\")",
    preset_shiny_lines[1]
  )
  writeLines(preset_shiny_lines, path_bootstrap)
  invisible(path_bootstrap)
}

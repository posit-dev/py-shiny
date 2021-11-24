#!/usr/bin/env Rscript

library(htmltools)
library(bslib)

www <- file.path(getwd(), "shiny", "www")
#unlink(www, recursive = TRUE)
dir.create(www)

# Copy over shiny's www/shared directory
withr::with_tempdir({
  cmd <- paste("git clone --depth 1 --branch main https://github.com/rstudio/shiny")
  system(cmd)
  file.copy(
    "shiny/inst/www/shared",
    www, recursive = TRUE
  )
})

# Don't need legacy (hopefully)
unlink(file.path(www, "shared", "legacy"), recursive = TRUE)

# jQuery will come in via bslib (below)
unlink(Sys.glob(file.path(www, "shared", "jquery*")))

# Upgrade to Bootstrap 5 by default
deps <- bs_theme_dependencies(bs_theme(version = 5))
withr::with_options(
  list(htmltools.dir.version = FALSE),
  lapply(deps, copyDependencyToDir, "shiny/www/shared")
)

# For JSX based nav() implementation
bslib <- file.path(www, "shared", "bslib")
dir.create(bslib)
withr::with_tempdir({
  cmd <- paste("git clone --depth 1 --branch jsx https://github.com/rstudio/bslib")
  system(cmd)
  file.copy(
    "bslib/inst/navs/dist",
    bslib, recursive = TRUE
  )
})


ipy_lib <- file.path(getwd(), "shiny", "ipywidgets", "lib")
if (!dir.exists(ipy_lib)) dir.create(ipy_lib)
# From https://github.com/jupyter-widgets/ipywidgets/blob/fbdbd005/python/ipywidgets/ipywidgets/embed.py#L32
download.file(
  "https://cdnjs.cloudflare.com/ajax/libs/require.js/2.3.4/require.min.js",
  file.path(ipy_lib, "require.min.js")
)
# From https://github.com/jupyter-widgets/ipywidgets/blob/fbdbd005/python/ipywidgets/ipywidgets/embed.py#L62
# Note that we also grab libembed-amd, not embed-amd, because our output binding will handle the actual rendering aspect
# https://github.com/jupyter-widgets/ipywidgets/blob/fbdbd00/packages/html-manager/scripts/concat-amd-build.js#L6
# TODO: minify the bundle and import the version via `from ipywidgets._version import __html_manager_version__`
download.file(
  "https://unpkg.com/@jupyter-widgets/html-manager@0.20.0/dist/libembed-amd.js",
  file.path(ipy_lib, "libembed-amd.js")
)

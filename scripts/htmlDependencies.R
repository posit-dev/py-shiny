#!/usr/bin/env Rscript

library(htmltools)
library(bslib)

www <- file.path(getwd(), "shiny", "www")
unlink(www, recursive = TRUE)
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

unlink("shiny/www/shared/bs3compat/", recursive = TRUE)

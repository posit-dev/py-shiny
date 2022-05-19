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

# We've manually included a newer and slimmer version jQuery UI (just the draggable
# interaction) so ignore whatever Shiny wants to bring in. The URL below is what I used
# to download it
# https://jqueryui.com/download/#!version=1.13.1&themeParams=none&components=101000000100100000000000010000000000000000000000
unlink(file.path(www, "shared", "jqueryui"), recursive = TRUE)

# Upgrade to Bootstrap 5 by default
deps <- bs_theme_dependencies(bs_theme(version = 5))
withr::with_options(
  list(htmltools.dir.version = FALSE),
  lapply(deps, copyDependencyToDir, "shiny/www/shared")
)

# This additional bs3compat HTMLDependency() only holds
# the JS shim for tab panel logic, which we don't need
# since we're generating BS5+ tab markup. Note, however,
# we still do have bs3compat's CSS on the page, which
# comes in via the bootstrap HTMLDependency()
unlink("shiny/www/shared/bs3compat/", recursive = TRUE)

requirejs <- file.path(www, "shared", "requirejs")
dir.create(requirejs)
download.file(
  "https://cdnjs.cloudflare.com/ajax/libs/require.js/2.3.6/require.min.js",
  file.path(requirejs, "require.min.js")
)

shims <- file.path(getwd(), "scripts", "define-shims.js")

cat(
  "\n\n",
  paste(readLines(shims), collapse = "\n"),
  file = file.path(requirejs, "require.min.js"),
  append = TRUE
)

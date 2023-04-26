#!/usr/bin/env Rscript

pak::pkg_install("rstudio/bslib")
# pak::pkg_install("cran::bslib")

bslib_info <- sessioninfo::package_info("bslib")
bslib_info_list <- bslib_info[bslib_info$package == "bslib", , drop = TRUE]

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
jsonlite::write_json(
  list(
    bslib_version = bslib_info_list$source,
    bootstrap_version = names(bslib::versions())[bslib::versions() == "5"]
  ),
  "shiny/www/shared/bootstrap/version.json",
  pretty = TRUE, auto_unbox = TRUE
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

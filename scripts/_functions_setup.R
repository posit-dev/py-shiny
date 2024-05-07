
ensure_base_packages <- function() {
  for (pkg in c("cli", "pak")) {
    if (!requireNamespace(pkg, quietly = TRUE)) {
      message("Installing base package: ", pkg)
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
